import os
import streamlit.components.v1 as components

# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
# (This is, of course, optional - there are innumerable ways to manage your
# release process.)
_RELEASE = True

if not _RELEASE:
    _component_func = components.declare_component(
        # We give the component a simple, descriptive name ("my_component"
        # does not fit this bill, so please choose something better for your
        # own component :)
        "audio_component",
        # Pass `url` here to tell Streamlit that the component will be served
        # by the local dev server that you run via `npm run start`.
        # (This is useful while your component is in development.)
        url="http://localhost:3001",
    )
else:
    # When we're distributing a production version of the component, we'll
    # replace the `url` param with `path`, and point it to the component's
    # build directory:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("audio_component", path=build_dir)

# Create a wrapper function for the component. This is an optional
# best practice - we could simply expose the component function returned by
# `declare_component` and call it done. The wrapper allows us to customize
# our component's API: we can pre-process its input args, post-process its
# output value, and add a docstring for users

def audio_player(audio_url, autoplay=True, key=None):
    """Create a hidden audio player component that autoplays and reports when playback stops.
    
    Parameters
    ----------
    audio_url: str
        URL of the audio to play
    autoplay: bool
        Whether to start playing automatically
    key: str or None
        Streamlit component instance key
        
    Returns
    -------
    dict or None
        Contains event data when audio playback ends or other events occur
    """
    component_value = _component_func(
        audioUrl=audio_url, 
        autoplay=autoplay,
        key=key, 
        default=None
    )
    return component_value