"""
Rich text editor component with inline highlighting support.
Like Microsoft Word - select text, click color, see it highlighted immediately.
"""

import streamlit.components.v1 as components
import json


def rich_text_editor_component(content: str, highlights: list, height: int = 500):
    """
    Rich text editor with inline highlighting (Word-like experience).
    
    Args:
        content: Markdown content to display
        highlights: List of existing highlights
        height: Editor height in pixels
    
    Returns:
        User actions via component value
    """
    
    # Apply highlights to content for initial display
    highlighted_content = content
    for hl in sorted(highlights, key=lambda h: len(h.get("text", "")), reverse=True):
        text = hl.get("text", "")
        color = hl.get("color", "#ffeb3b")
        if text:
            import re
            escaped = re.escape(text)
            replacement = f'<mark style="background-color: {color}; padding: 2px 0;">{text}</mark>'
            highlighted_content = re.sub(escaped, replacement, highlighted_content)
    
    # Convert markdown to HTML with line breaks
    html_content = highlighted_content.replace('\n', '<br/>')
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: 'Arial', 'Traditional Arabic', sans-serif;
                background: #f0f2f6;
                padding: 0;
                margin: 0;
            }}
            .container {{
                background: white;
                height: 100vh;
                display: flex;
                flex-direction: column;
            }}
            .toolbar {{
                background: #f8f9fa;
                padding: 12px;
                border-bottom: 2px solid #e0e0e0;
                display: flex;
                gap: 12px;
                align-items: center;
                flex-wrap: wrap;
            }}
            .toolbar-label {{
                font-weight: bold;
                font-size: 13px;
                color: #333;
            }}
            .color-btn {{
                width: 32px;
                height: 32px;
                border-radius: 4px;
                border: 2px solid #ddd;
                cursor: pointer;
                transition: all 0.2s;
                position: relative;
            }}
            .color-btn:hover {{
                transform: scale(1.15);
                border-color: #666;
                box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            }}
            .color-btn.active {{
                border-color: #0066cc;
                border-width: 3px;
                box-shadow: 0 0 0 2px rgba(0,102,204,0.2);
            }}
            .action-btn {{
                padding: 8px 16px;
                background: #0066cc;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 13px;
                font-weight: 500;
                transition: background 0.2s;
            }}
            .action-btn:hover {{
                background: #0052a3;
            }}
            .action-btn:disabled {{
                background: #ccc;
                cursor: not-allowed;
            }}
            .action-btn.remove {{
                background: #dc3545;
            }}
            .action-btn.remove:hover {{
                background: #c82333;
            }}
            #editor {{
                flex: 1;
                padding: 20px;
                overflow-y: auto;
                font-size: 15px;
                line-height: 1.8;
                direction: rtl;
                text-align: right;
                outline: none;
                color: #1a1a1a;
            }}
            #editor:focus {{
                background: #fffef7;
            }}
            mark {{
                padding: 2px 0;
                border-radius: 2px;
                cursor: pointer;
            }}
            mark:hover {{
                opacity: 0.85;
            }}
            .selection-info {{
                font-size: 12px;
                color: #666;
                padding: 4px 8px;
                background: #e3f2fd;
                border-radius: 4px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="toolbar">
                <span class="toolbar-label">🖍️ Highlight:</span>
                <div class="color-btn active" data-color="#ffeb3b" style="background: #ffeb3b;" title="Yellow"></div>
                <div class="color-btn" data-color="#8bc34a" style="background: #8bc34a;" title="Green"></div>
                <div class="color-btn" data-color="#ff80ab" style="background: #ff80ab;" title="Pink"></div>
                <div class="color-btn" data-color="#64b5f6" style="background: #64b5f6;" title="Blue"></div>
                <div class="color-btn" data-color="#ff9800" style="background: #ff9800;" title="Orange"></div>
                <button class="action-btn" id="highlightBtn" disabled>✨ Highlight Selection</button>
                <button class="action-btn remove" id="removeBtn" disabled>🗑️ Remove Highlight</button>
                <span class="selection-info" id="selectionInfo"></span>
            </div>
            <div id="editor" contenteditable="true">{html_content}</div>
        </div>
        
        <script>
            const editor = document.getElementById('editor');
            const highlightBtn = document.getElementById('highlightBtn');
            const removeBtn = document.getElementById('removeBtn');
            const selectionInfo = document.getElementById('selectionInfo');
            const colorBtns = document.querySelectorAll('.color-btn');
            
            let selectedColor = '#ffeb3b';
            let currentRange = null;
            
            // Color selection
            colorBtns.forEach(btn => {{
                btn.addEventListener('click', () => {{
                    colorBtns.forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    selectedColor = btn.dataset.color;
                }});
            }});
            
            // Track selection
            document.addEventListener('selectionchange', updateSelection);
            
            function updateSelection() {{
                const selection = window.getSelection();
                const selectedText = selection.toString().trim();
                
                if (selectedText && selection.rangeCount > 0) {{
                    currentRange = selection.getRangeAt(0);
                    highlightBtn.disabled = false;
                    selectionInfo.textContent = `Selected: "${{selectedText.substring(0, 40)}}${{selectedText.length > 40 ? '...' : ''}}"`;
                    
                    // Check if selection is within a mark tag
                    const container = currentRange.commonAncestorContainer;
                    const parent = container.nodeType === 3 ? container.parentNode : container;
                    removeBtn.disabled = parent.tagName !== 'MARK';
                }} else {{
                    highlightBtn.disabled = true;
                    removeBtn.disabled = true;
                    selectionInfo.textContent = '';
                    currentRange = null;
                }}
            }}
            
            // Highlight selected text
            highlightBtn.addEventListener('click', () => {{
                if (currentRange) {{
                    const selection = window.getSelection();
                    const selectedText = selection.toString().trim();
                    
                    if (selectedText) {{
                        // Create mark element
                        const mark = document.createElement('mark');
                        mark.style.backgroundColor = selectedColor;
                        mark.style.padding = '2px 0';
                        
                        try {{
                            currentRange.surroundContents(mark);
                        }} catch (e) {{
                            // Fallback if selection spans multiple elements
                            mark.textContent = selectedText;
                            currentRange.deleteContents();
                            currentRange.insertNode(mark);
                        }}
                        
                        // Notify Streamlit
                        window.parent.postMessage({{
                            type: 'streamlit:setComponentValue',
                            value: {{
                                action: 'highlight',
                                text: selectedText,
                                color: selectedColor,
                                content: editor.innerText
                            }}
                        }}, '*');
                        
                        // Clear selection
                        selection.removeAllRanges();
                        updateSelection();
                    }}
                }}
            }});
            
            // Remove highlight
            removeBtn.addEventListener('click', () => {{
                const selection = window.getSelection();
                if (selection.rangeCount > 0) {{
                    const range = selection.getRangeAt(0);
                    const container = range.commonAncestorContainer;
                    const parent = container.nodeType === 3 ? container.parentNode : container;
                    
                    if (parent.tagName === 'MARK') {{
                        const text = parent.textContent;
                        const textNode = document.createTextNode(text);
                        parent.parentNode.replaceChild(textNode, parent);
                        
                        // Notify Streamlit
                        window.parent.postMessage({{
                            type: 'streamlit:setComponentValue',
                            value: {{
                                action: 'remove',
                                text: text,
                                content: editor.innerText
                            }}
                        }}, '*');
                    }}
                }}
                selection.removeAllRanges();
                updateSelection();
            }});
            
            // Sync content changes
            let contentChangeTimer;
            editor.addEventListener('input', () => {{
                clearTimeout(contentChangeTimer);
                contentChangeTimer = setTimeout(() => {{
                    window.parent.postMessage({{
                        type: 'streamlit:setComponentValue',
                        value: {{
                            action: 'edit',
                            content: editor.innerText
                        }}
                    }}, '*');
                }}, 1000);
            }});
            
            // Prevent enter key from creating divs (use br instead)
            editor.addEventListener('keydown', (e) => {{
                if (e.key === 'Enter') {{
                    e.preventDefault();
                    document.execCommand('insertLineBreak');
                }}
            }});
        </script>
    </body>
    </html>
    """
    
    # Return component
    component_value = components.html(html_code, height=height, scrolling=False)
    return component_value
