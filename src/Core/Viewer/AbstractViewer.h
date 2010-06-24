/*
 For more information, please see: http://software.sci.utah.edu

 The MIT License

 Copyright (c) 2009 Scientific Computing and Imaging Institute,
 University of Utah.


 Permission is hereby granted, free of charge, to any person obtaining a
 copy of this software and associated documentation files (the "Software"),
 to deal in the Software without restriction, including without limitation
 the rights to use, copy, modify, merge, publish, distribute, sublicense,
 and/or sell copies of the Software, and to permit persons to whom the
 Software is furnished to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included
 in all copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
 OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 DEALINGS IN THE SOFTWARE.
 */

#ifndef APPLICATION_VIEWER_ABSTRACTVIEWER_H
#define APPLICATION_VIEWER_ABSTRACTVIEWER_H

#if defined(_MSC_VER) && (_MSC_VER >= 1020)
# pragma once
#endif

// Boost includes 
#include <boost/smart_ptr.hpp>

// Core includes
#include <Core/RendererBase/AbstractRenderer.h>
#include <Core/State/State.h>
#include <Core/State/StateHandler.h>
#include <Core/Utils/EnumClass.h>
#include <Core/Utils/Lockable.h>
#include <Core/Viewer/Mouse.h>

namespace Core
{

// Forward declarations
class AbstractViewer;
typedef boost::shared_ptr< AbstractViewer > AbstractViewerHandle;
typedef boost::weak_ptr< AbstractViewer > AbstractViewerWeakHandle;

class AbstractViewerPrivate;
typedef boost::shared_ptr< AbstractViewerPrivate > AbstractViewerPrivateHandle;

// Class definition
class AbstractViewer : public StateHandler, public RecursiveLockable
{

  // -- constructor/destructor --
public:
  AbstractViewer( size_t viewer_id, size_t version_number );
  virtual ~AbstractViewer();

  // -- mouse events handling --
public:

  // MOUSE_MOVE_EVENT:
  // This function is called by the render widget when a mouse move event has occurred.
  // This function needs to be overloaded to record mouse movements.
  virtual void mouse_move_event( const MouseHistory& mouse_history, int button, int buttons,
      int modifiers );
    
  // MOUSE_PRESS_EVENT:
  // This function is called by the render widget when a mouse button press event has occurred.
  // This function needs to be overloaded to record mouse buttons being pressed.
  virtual void mouse_press_event( const MouseHistory& mouse_history, int button, int buttons,
      int modifiers );
  
  // MOUSE_RELEASE_EVENT:
  // This function is called by the render widget when a mouse button release event has occurred.
  // This function needs to be overloaded to record mouse buttons being released.
  virtual void mouse_release_event( const MouseHistory& mouse_history, int button, int buttons,
      int modifiers );
  
  // WHEEL_EVENT:
  // This function is called by the render widget when a mouse wheel event has occurred.
  // This function needs to be overloaded to track mouse wheel events. 
  virtual bool wheel_event( int delta, int x, int y, int buttons, int modifiers );

  // KEY_EVENT:
  // This function is called when a key is pressed while hovering over the render widget
  virtual bool key_event( int key, int modifiers );

  // RESIZE:
  // This function is called when the viewer is resized by the render widget.
  virtual void resize( int width, int height );

  // GET_VIEWER_ID:
  // Get the id number of this viewer. All the viewers are number and can be identified by
  // this number
  size_t get_viewer_id() const;

  // -- Signals and Slots --
public:
  // UPDATE_DISPLAY_SIGNAL_:
  // Triggered when new texture is received.
  typedef boost::signals2::signal< void () > update_display_signal_type;
  update_display_signal_type update_display_signal_;

  // -- renderer/texture access --
public:
  // INSTALL_RENDERER:
  // Install a renderer to the viewer.
  void install_renderer( Core::AbstractRendererHandle renderer );

  // GET_RENDERER:
  // Get the renderer base class that is associated with this viewer
  Core::AbstractRendererHandle get_renderer();

  // GET_TEXTURE:
  // Returns the texture generated by the renderer
  Core::Texture2DHandle get_texture();

  // GET_OVERLAY_TEXTURE:
  // Returns the overlay texture generated by the renderer
  Core::Texture2DHandle get_overlay_texture();

  // GET_WIDTH:
  // Get the width of the viewer
  int get_width();

  // GET_HEIGHT:
  // Get the height of the viewer
  int get_height();

  // -- callback functions for renderer --
  // NOTE: These functions are private as the textures are inserted by the renderer
private:
  // SET_TEXTURE:
  // Connected to the redraw_completed_signal_ of the renderer.
  void set_texture( Core::Texture2DHandle texture, bool delay_update );

  // SET_OVERLAY_TEXTURE:
  // Connected to the redraw_overlay_completed_signal_ of the renderer.
  void set_overlay_texture( Core::Texture2DHandle texture, bool delay_update );

  // -- internals of the abstract renderer --
private:
  AbstractViewerPrivateHandle private_;

  // -- State information --
public:

  // State variable that keeps track of whether this viewer is visible and hence needs
  // data to be rendered.
  Core::StateBoolHandle viewer_visible_state_;

};

} // end namespace Core

#endif
