import streamlit as st
import os
import shutil
from pathlib import Path
from docling.document_converter import DocumentConverter
import pypdf
import app.history as history
from app.chat import chat_with_data
from app.consolidator import generate_summary

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

# --- Main Area: Chat ---
st.divider()
st.header("3. Chat with Data")

# --- Session Management (Sidebar) ---
with st.sidebar:
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

# --- Chat Interface ---

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
