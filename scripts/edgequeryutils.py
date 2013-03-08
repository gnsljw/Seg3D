import os
import sys
import configparser
import seg3d2
import threading

# TODO: filepaths don't work with strings (even escaped ones) yet...

def stringEscape(s):
  return s.replace("(","\\(").replace(")","\\)").replace(" ","\\ ")

def processFilepath(configureParser, configSection, option, basename):
  fileName = configureParser.get(configSection, option)
  fullPath = os.path.join(basename, fileName)
  return stringEscape(fullPath)

class EdgeQueryUtils:
  def processEdgeQuery(self, iteration):
    try:
      self.__importMatlabSingleMaskLayer(iteration)
      seg3d2.activatelayer(layerid=self.maskLayerID)

      self.__getPointsFromFile(iteration)
      (targetStateID, verticesStateID, edgesStateID, saveStateID, stopStateID) = self.__setupEdgeQueryTool()

      c = threading.Condition()
      c.acquire()

      #print("max checks=%i, timeout=%d" % self.iterationMax, self.timeout)

      counter = 1
      with c:
        while not seg3d2.get(stateid=saveStateID):
          if counter > self.iterationMax:
            break
          counter += 1
          c.wait(self.timeout)

      c.release()
      print("Waiting for edge query selection is done.")
      self.__writeLabelsToFile(edgesStateID, iteration)

    except Exception as err:
      print(err)
    finally:
      self.stop = seg3d2.get(stateid=stopStateID)
      seg3d2.closetool(toolid=self.toolID)
      seg3d2.deletelayers(layers=self.maskLayerID)
      # reset ids
      self.__setTransientDefaults()

  def __getPointsFromFile(self, iteration):
    if len(self.vertices) > 0:
      self.vertices = []

    pointsFilename = "%s_%d.%s" % (self.pointsFileBasename, iteration, self.dataFileExt)
    print("Points from ", pointsFilename)
    with open(pointsFilename) as pointsFile:
      for line in pointsFile:
        floats = [float(points) for points in line.split()]
        self.vertices.append(floats)

    if len(self.vertices) < 3:
      # TODO: error class
      raise Exception('ListError', 'Points list should contain 3 points.') 

    # 2D case - add default z location (0)
    for pointList in self.vertices:
      if len(pointList) == 2:
        pointList.append(0)

    print("Edge query vertices read from %s." % pointsFilename)

  def __writeLabelsToFile(self, stateID, iteration):
    edges = seg3d2.get(stateid=stateID)
    l = list(edges)
    if len(l) != 5:
      raise Exception('ListError', 'Malformed edges list')

    labelsFilename = "%s_%d.%s" % (self.labelsFileBasename, iteration, self.dataFileExt)
    print("Labels to ", labelsFilename)
    self.labels = "%s %s" % (l[1], l[3])
    with open(labelsFilename, 'wt') as edgeFile:
      edgeFile.write(self.labels)

    print("Saved %s to %s." % (self.labels, labelsFilename))

  def __importMatlabDataLayer(self):
    idHandle = seg3d2.importlayer(filename=self.volumeFilename, importer='[Matlab Importer]', mode='data')
    self.dataLayerID = idHandle[0]

    # set(..) returns bool
    result = seg3d2.set(stateid='view::layout', value='single')
    # sets up Axial view (0) by default
    # Axial = 0, Coronal = 1, Sagittal = 2
    result = seg3d2.set(stateid='view::active_viewer', value=0)
    result = seg3d2.set(stateid='viewer0::view_mode', value='Axial')


  def __importMatlabSingleMaskLayer(self, iteration):
    maskFilename = "%s_%d.%s" % (self.maskFileBasename, iteration, self.maskFileExt)
    print("Points from ", maskFilename)

    idHandle = seg3d2.importlayer(filename=maskFilename, importer='[Matlab Importer]', mode='single_mask')
    self.maskLayerID = idHandle[0]

  def __setupEdgeQueryTool(self):
    self.toolID = seg3d2.opentool(tooltype='edgequerytool')

    targetStateID = self.toolID + "::target"
    verticesStateID = self.toolID + "::vertices"
    edgesStateID = self.toolID + "::edges"
    saveStateID = self.toolID + "::save"
    stopStateID = self.toolID + "::stop"

    result = seg3d2.set(stateid=targetStateID, value=self.maskLayerID)
    result = seg3d2.set(stateid=verticesStateID, value=self.vertices)

    # assuming axial view here...
    z = self.vertices[0][2]
    result = seg3d2.set(stateid='viewer0::slice_number', value=z)
    return (targetStateID, verticesStateID, edgesStateID, saveStateID, stopStateID)

  def __importConfiguration(self):
    # import configuration from settings.ini
    # (contains file paths)
    config = configparser.ConfigParser()
    config.read(os.path.join(self.configFileLocation, 'settings.ini'))

    # location of points file read into Seg3D and labels written by Seg3d
    dataLocation = config.get('DataSettings', 'data_dir')
    if not os.path.exists(dataLocation):
      raise ValueError("Path %s does not exist." % dataLocation)

    # volume and mask(s) location
    self.volumeFilename = processFilepath(config, 'DataSettings', 'volume_file', dataLocation)
    self.pointsFileBasename = processFilepath(config, 'DataSettings', 'query_file_base', dataLocation)
    self.labelsFileBasename = processFilepath(config, 'DataSettings', 'labels_file_base', dataLocation)
    self.dataFileExt = config.get('DataSettings', 'data_file_ext')
    self.maskFileBasename = processFilepath(config, 'DataSettings', 'mask_file_base', dataLocation)
    self.maskFileExt = config.get('DataSettings', 'mask_file_ext')

    # Matlab config
    self.matlabScriptsDirectory = stringEscape(config.get('MatlabSettings', 'matlab_scripts_dir'))

  def __setTransientDefaults(self):
    self.toolID = ''
    self.maskLayerID = ''

  # import data volume in constructor
  def __init__(self, configFileLocation, timeout=2.0, iterationMax=60):
    self.configFileLocation = configFileLocation
    self.timeout = timeout
    self.iterationMax = iterationMax

    self.volumeFilename = ''
    self.pointsFileBasename = ''
    self.labelsFileBasename = '' 
    self.dataFileExt = ''
    self.maskFileBasename = ''
    self.maskFileExt = ''
    self.vertices = []
    self.labels = ''
    self.stop = False

    self.__setTransientDefaults()
    self.__importConfiguration()
    self.__importMatlabDataLayer()
