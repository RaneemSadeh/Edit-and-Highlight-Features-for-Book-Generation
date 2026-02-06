# LearnSync AI - Project Documentation

## 🚀 New Feature: Smart Editor & Highlighter

We have introduced a powerful new **Edit & Highlight** module designed to streamline the review and refinement of the Knowledge Base.

### 💼 Business Value
*   **Unified Workflow**: Users can now View, Edit, and Highlight content in a single interface without switching tools.
*   **Precision Review**: The "Smart Highlight" system allows users to flag specific terms or phrases even if the underlying text has hidden formatting (like bolding or list bullets), ensuring no feedback is lost.
*   **Bilingual Excellence**: The interface is optimized for both Arabic (RTL) and English (LTR), preserving the correct flow and alignment for mixed-language documents (e.g., Al Jazeera training materials).
*   **Data Integrity**: Edits are saved directly to the source `base_context.md`, ensuring the Knowledge Base remains the single source of truth.

### 🛠️ Technical Implementation
*   **Bi-directional Streamlit Component**:
    *   We built a custom component (`app/word_editor_component`) using HTML5 `contenteditable` and JavaScript.
    *   Unlike standard Streamlit components, this editor communicates bi-directionally, sending edits back to Python in real-time to enable the "Save Changes" functionality.
*   **Smart Fuzzy Matching**:
    *   The highlighting engine (`app/viewer.py`) uses advanced regex logic to ignore Markdown syntax characters (like `*`, `#`, `-`) when searching.
    *   It wraps individual words in `<mark>` tags instead of entire blocks, preserving the document's structure (headers, lists) while applying highlights.
*   **Robust View Rendering**:
    *   We replaced the standard renderer with `markdown-it-py` and wrapped the output in a custom container with `dir="auto"`.
    *   This ensures that Markdown headers (`##`) are rendered as actual large headers and that Arabic/English text direction is handled natively by the browser.

---

## 📥 Installation & Setup

Follow these instructions to download and run the project locally.

### Prerequisites
*   Python 3.10 or higher installed.
*   Git installed.

### 1. Download the Project
Clone the repository from GitHub:
```bash
git clone <your-repo-url>
cd <project-folder-name>
```

### 2. Set Up Environment
It is recommended to use a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Install the required packages using pip:
```bash
pip install -r requirements.txt
```

### 4. Run the Application
Start the Streamlit app:
```bash
python -m streamlit run streamlit_app.py
```
*Note: Using `python -m streamlit` ensures the correct Python environment is used.*

The application will open in your default browser at `http://localhost:8501`.