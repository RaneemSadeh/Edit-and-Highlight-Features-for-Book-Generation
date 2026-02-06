"""
Rich text editor component with text selection highlighting support.
Uses HTML/JavaScript to capture text selection.
"""

import streamlit.components.v1 as components


def rich_text_editor(content: str, key: str = "rich_editor", height: int = 400):
    """
    Display a rich text editor with text selection capability.
    
    Args:
        content: Initial content to display
        key: Unique key for the component
        height: Height of the editor in pixels
    
    Returns:
        Dictionary with:
        - content: Current editor content
        - selected_text: Currently selected text
        - selection_start: Selection start position
        - selection_end: Selection end position
    """
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                margin: 0;
                padding: 0;
                font-family: 'Arial', 'Traditional Arabic', sans-serif;
            }}
            #editor {{
                width: 100%;
                height: {height}px;
                padding: 12px;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                line-height: 1.8;
                direction: rtl;
                text-align: right;
                resize: vertical;
                background: #ffffff;
                color: #1a1a1a;
            }}
            #editor:focus {{
                outline: 2px solid #0066cc;
                border-color: #0066cc;
            }}
            .toolbar {{
                margin-bottom: 8px;
                padding: 8px;
                background: #f5f5f5;
                border-radius: 4px;
                display: flex;
                gap: 8px;
                align-items: center;
            }}
            .color-btn {{
                width: 30px;
                height: 30px;
                border-radius: 4px;
                border: 2px solid #ddd;
                cursor: pointer;
                transition: transform 0.2s;
            }}
            .color-btn:hover {{
                transform: scale(1.1);
                border-color: #999;
            }}
            .color-btn.selected {{
                border-color: #000;
                border-width: 3px;
            }}
            button {{
                padding: 6px 16px;
                background: #0066cc;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
            }}
            button:hover {{
                background: #0052a3;
            }}
            button:disabled {{
                background: #ccc;
                cursor: not-allowed;
            }}
        </style>
    </head>
    <body>
        <div class="toolbar">
            <span style="font-weight: bold;">Highlight color:</span>
            <div class="color-btn selected" data-color="#ffeb3b" style="background: #ffeb3b;" title="Yellow"></div>
            <div class="color-btn" data-color="#8bc34a" style="background: #8bc34a;" title="Green"></div>
            <div class="color-btn" data-color="#ff80ab" style="background: #ff80ab;" title="Pink"></div>
            <div class="color-btn" data-color="#64b5f6" style="background: #64b5f6;" title="Blue"></div>
            <div class="color-btn" data-color="#ff9800" style="background: #ff9800;" title="Orange"></div>
            <button id="highlightBtn" disabled>Highlight Selection</button>
            <span id="selectionInfo" style="margin-left: auto; color: #666;"></span>
        </div>
        <textarea id="editor">{content}</textarea>
        
        <script>
            const editor = document.getElementById('editor');
            const highlightBtn = document.getElementById('highlightBtn');
            const selectionInfo = document.getElementById('selectionInfo');
            const colorBtns = document.querySelectorAll('.color-btn');
            
            let selectedColor = '#ffeb3b';
            let currentSelection = null;
            
            // Color selection
            colorBtns.forEach(btn => {{
                btn.addEventListener('click', () => {{
                    colorBtns.forEach(b => b.classList.remove('selected'));
                    btn.classList.add('selected');
                    selectedColor = btn.dataset.color;
                }});
            }});
            
            // Track text selection
            editor.addEventListener('mouseup', updateSelection);
            editor.addEventListener('keyup', updateSelection);
            
            function updateSelection() {{
                const start = editor.selectionStart;
                const end = editor.selectionEnd;
                const selectedText = editor.value.substring(start, end);
                
                if (selectedText.length > 0) {{
                    highlightBtn.disabled = false;
                    selectionInfo.textContent = `Selected: ${{selectedText.length}} characters`;
                    currentSelection = {{ text: selectedText, start, end }};
                }} else {{
                    highlightBtn.disabled = true;
                    selectionInfo.textContent = '';
                    currentSelection = null;
                }}
                
                // Send state to Streamlit
                window.parent.postMessage({{
                    type: 'streamlit:componentReady',
                    data: {{
                        content: editor.value,
                        selected_text: selectedText,
                        selection_start: start,
                        selection_end: end
                    }}
                }}, '*');
            }}
            
            // Highlight selected text
            highlightBtn.addEventListener('click', () => {{
                if (currentSelection) {{
                    // Send highlight request to Streamlit
                    window.parent.postMessage({{
                        type: 'streamlit:highlightRequest',
                        data: {{
                            text: currentSelection.text,
                            color: selectedColor,
                            start: currentSelection.start,
                            end: currentSelection.end
                        }}
                    }}, '*');
                    
                    // Visual feedback
                    highlightBtn.textContent = 'Highlighted!';
                    setTimeout(() => {{
                        highlightBtn.textContent = 'Highlight Selection';
                    }}, 2000);
                }}
            }});
            
            // Send initial state
            updateSelection();
        </script>
    </body>
    </html>
    """
    
    # Use Streamlit's HTML component
    return components.html(html_code, height=height + 60, scrolling=False)
