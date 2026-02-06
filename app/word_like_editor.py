import os
import streamlit.components.v1 as components

# Create a _RELEASE constant. We'll set this to False while we're developing.
_RELEASE = True

# Declare the component
if not _RELEASE:
    # _component_func = components.declare_component(
    #     "word_like_editor",
    #     url="http://localhost:3001",
    # )
    pass
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "word_editor_component")
    _component_func = components.declare_component("word_like_editor", path=build_dir)

def word_like_editor(content: str, height: int = 600, key=None):
    """
    Display a Word-like editor with inline highlighting.
    
    Args:
        content: Initial content to display (text)
        height: Height of the editor container in pixels
        key: Optional key for the component
    
    Returns:
        The current text content of the editor
    """
    
    # Pre-process content for HTML display if needed, 
    # but since our JS handles innerText vs innerHTML, passing raw text with newlines replaced by <br> might be safest for initial load
    # or just pass it as is and let JS handle it.
    # Let's simple replace newlines with <br> for display
    safe_content = content.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br/>')

    component_value = _component_func(content=safe_content, height=height, key=key, default=content)
    return component_value
