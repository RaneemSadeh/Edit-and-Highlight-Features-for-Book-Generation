import streamlit as st
import os
import shutil
from pathlib import Path
from docling.document_converter import DocumentConverter
import pypdf
from markdown_it import MarkdownIt

import app.history as history
from app.chat import chat_with_data
from app.consolidator import generate_summary
import app.viewer as viewer
from app.word_like_editor import word_like_editor

# ... (Configuration setup remains the same) ...
st.set_page_config(page_title="Book Gen Pipeline", layout="wide")

# Validating API Key
if not os.getenv("GEMINI_API_KEY"):
    st.error("⚠️ GENAI_API_KEY is missing! Please set it in your .env file or Streamlit secrets.")

# Setup Directories
UPLOAD_DIR = Path("uploaded_files")
OUTPUT_DIR = Path("extracted_docs")
CONSOLIDATED_DIR = Path("consolidated_docs")

UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
CONSOLIDATED_DIR.mkdir(exist_ok=True)

st.title("📚 Book Generation Pipeline")
st.markdown("Upload content, consolidate it into a Knowledge Base, and chat with your data.")

# Initialize viewer session state
if "viewer_collapsed" not in st.session_state:
    st.session_state.viewer_collapsed = False

if "md_content" not in st.session_state:
    context_file = CONSOLIDATED_DIR / "base_context.md"
    if context_file.exists():
        with open(context_file, "r", encoding="utf-8") as f:
            st.session_state.md_content = f.read()
    else:
        st.session_state.md_content = "# No Base Context\n\nPlease generate the base context first."

if "highlights_data" not in st.session_state:
    st.session_state.highlights_data = viewer.load_highlights()

# --- Sidebar: Upload & Consolidation ---
with st.sidebar:
    st.header("1. Upload Files")
    uploaded_files = st.file_uploader(
        "Upload PDF or other documents", 
        accept_multiple_files=True,
        type=["pdf", "docx", "txt", "md"]
    )
    
    if uploaded_files:
        if st.button("Process Uploaded Files"):
            progress_bar = st.progress(0)
            total_files = len(uploaded_files)
            
            for index, uploaded_file in enumerate(uploaded_files):
                status_text = st.empty()
                status_text.write(f"Processing: *{uploaded_file.name}*...")
                
                # Save uploaded file to disk
                file_path = UPLOAD_DIR / uploaded_file.name
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                try:
                    # Try advanced extraction first
                    converter = DocumentConverter()
                    result = converter.convert(file_path)
                    md_content = result.document.export_to_markdown()
                    st.success(f"✅ Extracted (Advanced): {uploaded_file.name}")
                    
                except Exception as e:
                    # Fallback to standard pypdf extraction
                    print(f"Docling failed: {e}. Falling back to pypdf.")
                    try:
                        reader = pypdf.PdfReader(file_path)
                        text_content = ""
                        for page in reader.pages:
                            text_content += page.extract_text() + "\n\n"
                        
                        md_content = f"# {uploaded_file.name}\n\n{text_content}"
                        st.warning(f"⚠️ Used standard extraction for {uploaded_file.name} (Advanced method failed).")
                        
                    except Exception as fallback_e:
                        st.error(f"❌ Failed to extract {uploaded_file.name}: {str(fallback_e)}")
                        md_content = None # Skip saving if both fail

                # Save markdown if content was extracted
                if md_content:
                    output_filename = f"{file_path.stem}.md"
                    output_path = OUTPUT_DIR / output_filename
                    
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(md_content)
                
                progress_bar.progress((index + 1) / total_files)
                status_text.empty()

    st.divider()
    
    st.header("2. Consolidate Context")
    st.info("Merge all extracted files into a single Base Context.")
    
    if st.button("Generate Base Context"):
        with st.spinner("Consolidating with Gemini... This may take a minute."):
            try:
                # 1. Read all markdown files from extracted_docs
                md_files = list(OUTPUT_DIR.glob("*.md"))
                if not md_files:
                    st.warning("No extracted documents found to consolidate.")
                else:
                    combined_text = ""
                    for md_file in md_files:
                        with open(md_file, "r", encoding="utf-8") as f:
                            content = f.read()
                            combined_text += f"\n\n--- START OF FILE: {md_file.name} ---\n\n"
                            combined_text += content
                            combined_text += f"\n\n--- END OF FILE: {md_file.name} ---\n\n"
                    
                    # 2. Call Gemini Consolidator
                    summary_md = generate_summary(combined_text)
                    
                    # 3. Save to consolidated_docs
                    output_file = CONSOLIDATED_DIR / "base_context.md"
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(summary_md)
                        
                    st.success("✅ Consolidation Complete!")
                    st.markdown(f"**Output saved to:** `{output_file}`")
            except Exception as e:
                st.error(f"❌ Error during consolidation: {e}")
    
    st.divider()
    st.header("Chat Settings")
    temperature = st.slider("Model Temperature", 0.0, 1.0, 0.7, help="Higher = Creative, Lower = Precise")
    
    st.divider()
    st.header("Chat Sessions")
    
    if st.button("➕ New Chat"):
        new_id = history.create_session()
        st.session_state["current_session_id"] = new_id
        st.session_state.messages = [] # Clear local view
        st.rerun()

    # List recent sessions
    try:
        sessions = history.list_sessions()
        for sess in sessions:
            label = f"Session {sess['id'][:8]}... ({sess['message_count']} msgs)"
            if st.button(label, key=sess["id"]):
                st.session_state["current_session_id"] = sess["id"]
                st.rerun()
    except Exception:
        st.warning("Could not fetch sessions.")

# --- Main Area: Chat with Right Panel Viewer ---
st.divider()
st.header("3. Chat with Data")

# Two-column layout: Chat (left) + Viewer (right)
if not st.session_state.viewer_collapsed:
    chat_col, viewer_col = st.columns([2, 1])
else:
    chat_col, viewer_col = st.columns([3, 0.3])

# --- LEFT COLUMN: Chat Interface ---
with chat_col:
    # --- Session Management (Already in sidebar above) ---
    
    # Initialize or Load Session
    if "current_session_id" not in st.session_state:
        # Try to create one if none exists
        new_id = history.create_session()
        st.session_state["current_session_id"] = new_id

    current_id = st.session_state.get("current_session_id")

    if current_id:
        st.subheader(f"Current Session: `{current_id}`")
        
        # Load history
        session_data = history.get_session(current_id)
        if session_data:
            st.session_state.messages = session_data.get("messages", [])
        else:
            st.warning("Session file not found, starting fresh.")
            st.session_state.messages = []

        # Display chat messages
        for message in st.session_state.messages:
            role = message["role"]
            with st.chat_message(role):
                st.markdown(message["content"])

        # React to user input
        if prompt := st.chat_input("Ask a question about your uploaded documents..."):
            # Display user message
            st.chat_message("user").markdown(prompt)
            # Append to local state
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        # 1. Load the Base Context
                        context_file = CONSOLIDATED_DIR / "base_context.md"
                        
                        if not context_file.exists():
                            st.error("Base context not found. Please run 'Generate Base Context' first.")
                            answer = "Context missing."
                        else:
                            with open(context_file, "r", encoding="utf-8") as f:
                                context_content = f.read()
                            
                            # 2. Chat Logic
                            response_text = chat_with_data(
                                user_query=prompt, 
                                context_content=context_content, 
                                history=st.session_state.messages,
                                temperature=temperature
                            )
                            
                            answer = response_text
                            
                            # 3. Save interaction
                            history.save_message(current_id, "user", prompt)
                            history.save_message(current_id, "assistant", answer)
                            
                            st.markdown(answer)
                            st.session_state.messages.append({"role": "assistant", "content": answer})
                    
                    except Exception as e:
                        st.error(f"Error: {e}")
    else:
        st.info("Please create a new chat session to start.")

# --- RIGHT COLUMN: Base Context Viewer ---
with viewer_col:
    if not st.session_state.viewer_collapsed:
        # Header with collapse button
        col_header1, col_header2 = st.columns([3, 1])
        with col_header1:
            st.markdown("###  Base Context")
        with col_header2:
            if st.button("Show Base Context", help="Collapse viewer"):
                st.session_state.viewer_collapsed = True
                st.rerun()
        
        # File info
        context_file = CONSOLIDATED_DIR / "base_context.md"
        file_info = viewer.get_file_info(context_file)
        if file_info["exists"]:
            st.caption(f"{file_info['size_str']} • {file_info['last_modified_str']}")
        
        # Tabs for different modes
        view_tab, edit_tab = st.tabs(["View", "Edit"])
        
        # --- VIEW MODE TAB ---
        with view_tab:
            # Apply highlights to markdown
            highlights = st.session_state.highlights_data.get("highlights", [])
            highlighted_content = viewer.apply_highlights(st.session_state.md_content, highlights)
            
            # Custom CSS is no longer needed regarding container overrides, 
            # we will use native container + parsed HTML.
            
            # Render markdown with highlights inside a styled container with Scrolling
            # Using st.container(height=...) for scrolling block
            with st.container(height=600):
                 # Manually parse Markdown to HTML to avoid Streamlit's div-wrapping limitation
                 md_processor = MarkdownIt()
                 # Ensure we have a string
                 safe_content = str(highlighted_content) if highlighted_content else ""
                 # Render HTML
                 html_content = md_processor.render(safe_content)
                 
                 # Wrap in RTL/Auto div
                 # We use 'dir="auto"' to let browser decide per block, or "rtl" for base.
                 # Given Al Jazeera context, base RTL is safer even for English titles if user wants consistent alignment,
                 # but "english from left to right" implies 'dir="auto"' or specific mixed handling.
                 # 'dir="auto"' works best for paragraphs.
                 
                 st.markdown(
                     f'<div dir="auto" style="text-align: right; direction: rtl;">{html_content}</div>', 
                     unsafe_allow_html=True
                 )
            
            # Compact legend
            if highlights:
                with st.expander("Highlights Legend", expanded=False):
                    for hl in highlights[:5]:  # Show first 5
                        st.markdown(f"<mark style='background-color: {hl['color']}'>{hl['text'][:30]}...</mark>", unsafe_allow_html=True)
            
            # --- HIGHLIGHTING SECTION (Moved from Edit Tab) ---
            st.divider()
            st.markdown("##### Manage Highlights")
            
            # Add new highlight
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                text_to_highlight = st.text_input("Text to highlight", key="highlight_input", placeholder="Enter text to highlight...")
            
            with col2:
                colors = {
                    "Yellow": "#ffeb3b",
                    "Green": "#8bc34a",
                    "Pink": "#ff80ab",
                    "Blue": "#64b5f6",
                    "Orange": "#ff9800"
                }
                selected_color_name = st.selectbox("Color", list(colors.keys()))
                selected_color = colors[selected_color_name]
            
            with col3:
                st.write("")  # Spacing
                st.write("")  # Spacing
                if st.button("Add Highlight", type="primary", use_container_width=True):
                    if text_to_highlight.strip():
                        highlights = st.session_state.highlights_data.get("highlights", [])
                        viewer.add_highlight(text_to_highlight, selected_color, highlights)
                        st.session_state.highlights_data = viewer.load_highlights()
                        st.success("Highlight added!")
                        st.rerun()
                    else:
                        st.warning("Please enter text to highlight")
            
            # List existing highlights
            st.markdown("**Existing Highlights:**")
            highlights = st.session_state.highlights_data.get("highlights", [])
            
            if highlights:
                for idx, hl in enumerate(highlights):
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.markdown(f"<mark style='background-color: {hl['color']}'>{hl['text']}</mark>", unsafe_allow_html=True)
                    with col2:
                        if st.button("Remove", key=f"del_{hl['id']}"):
                            viewer.remove_highlight(hl['id'], highlights)
                            st.session_state.highlights_data = viewer.load_highlights()
                            st.rerun()
                
                if st.button("Clear All", type="secondary", use_container_width=True):
                    viewer.save_highlights([])
                    st.session_state.highlights_data = viewer.load_highlights()
                    st.success("All highlights cleared!")
                    st.rerun()
            else:
                st.info("No highlights yet. Add one above!")
        
        # --- EDIT MODE TAB ---
        with edit_tab:
            
            # Display Word-like editor (Bidirectional)
            # The component now returns the edited content!
            new_content = word_like_editor(
                content=st.session_state.md_content,
                height=600,
                key="editor_component"
            )
            
            st.markdown("---")
            
            # Save mechanism
            if st.button("Save Changes", type="primary"):
                if new_content and new_content != st.session_state.md_content:
                    try:
                        # Update session state
                        st.session_state.md_content = new_content
                        
                        # Save to file
                        context_file = CONSOLIDATED_DIR / "base_context.md"
                        with open(context_file, "w", encoding="utf-8") as f:
                            f.write(new_content)
                            
                        st.success("✅ Changes saved successfully!")
                        st.balloons()
                        # Rerun to update View tab
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to save changes: {e}")
                else:
                    st.info("No changes detected or empty content.")
    
    else:
        # Collapsed state - just show expand button
        if st.button("Show Base Context", help="Expand viewer"):
            st.session_state.viewer_collapsed = False
            st.rerun()

