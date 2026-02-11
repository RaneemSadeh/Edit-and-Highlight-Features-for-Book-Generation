# Technical Report: Viewer, Editor, & Visualizer

## 1. Overview
This report documents the implementation of the **Viewer**, **Editor**, and **Visualizer** features in the `streamlit_app.py` based application. These features allow users to view markdown content, edit it in a Word-like interface, and apply colored highlights that persist across sessions.

## 2. Architecture & File Structure

| Component | Primary File(s) | Role |
| :--- | :--- | :--- |
| **Main App** | `streamlit_app.py` | Orchestrates the UI, session state, and saving logic. |
| **Visualizer** | `app/viewer.py` | Handles highlight logic (regex matching) and JSON persistence. |
| **Editor** | `app/word_like_editor.py` | Python wrapper for the custom Streamlit component. |
| **Editor UI** | `app/word_editor_component/index.html` | HTML/JS implementation of the `contenteditable` editor. |
| **Data** | `consolidated_docs/base_context.md` | Stores the main content (Markdown). |
| **Metadata** | `consolidated_docs/highlights_metadata.json` | Stores highlight offsets/color data. |

## 3. Implementation Details

### 3.1 The Viewer (Display & Styling)
**Location:** `streamlit_app.py` (Lines ~254-376) & `app/viewer.py`

*   **Logic:**
    *   Loads content from `base_context.md` into `st.session_state.md_content`.
    *   Loads highlights from `highlights_metadata.json` via `viewer.load_highlights()`.
    *   **Rendering:**
        1.  Calls `viewer.apply_highlights(text, highlights)` to inject HTML `<mark>` tags into the Markdown text.
        2.  Converts the Markdown (with `<mark>` tags) to HTML using `MarkdownIt`.
        3.  Renders the final HTML using `st.markdown(..., unsafe_allow_html=True)` inside a custom `div` for RTL support.
*   **Styling:**
    *   Uses inline styles in the injected HTML for highlighters (`background-color`, `padding`, `border-radius`).
    *   The container uses `dir="auto"` and `style="text-align: right; direction: rtl;"` to support Arabic text.

### 3.2 The Visualizer (Highlighting System)
**Location:** `app/viewer.py`

*   **Core Logic (`apply_highlights`):**
    *   Iterates through stored highlights.
    *   Uses **Regex** to find text matches in the markdown.
    *   **Smart Matching:** It attempts an exact match first. If that fails, it tries a "fuzzy" match that allows for markdown syntax (like `**bold**` or `_italic_`) to exist between words in the highlighted phrase.
    *   **Injection:** Wraps matched text in `<mark>` tags.
*   **Persistence:**
    *   Highlights are stored as a JSON list of objects: `{id, text, color, created_at}`.
    *   Functions `add_highlight` and `remove_highlight` manage this list and save it to disk immediately.

### 3.3 The Editor (Live Editing)
**Location:** `app/word_like_editor.py` & `app/word_editor_component/index.html`

*   **Architecture:** Implemented as a [Custom Streamlit Component](https://docs.streamlit.io/library/components).
*   **Python Side (`word_like_editor.py`):**
    *   Sets up the component using `components.declare_component`.
    *   Passes initial `content` to the frontend.
    *   Updates `st.session_state` when the frontend returns new data.
*   **Frontend Side (`index.html`):**
    *   **HTML:** A simply `div` with `contenteditable="true"`.
    *   **CSS:** Styles the div to look like a document page (white background, padding, shadow).
    *   **JavaScript:**
        *   Listens for input events.
        *   **Debouncing:** Waits 300ms after typing stops before sending data back to Streamlit (to prevent lag).
        *   Sends `editor.innerText` back to Python via `Streamlit.setComponentValue`.

## 4. How to Update & Edit

### To Change the Viewer Styles
*   **Goal:** Change font size, margins, or RTL behavior.
*   **File:** `streamlit_app.py`
*   **Action:** Locate the `st.markdown(...)` call inside the **View Tab** section (around line 309). Edit the `style="..."` attribute of the wrapping `div`.

### To Modify Highlight Colors
*   **Goal:** Add new colors or change existing ones.
*   **File:** `streamlit_app.py`
*   **Action:** Find the `colors` dictionary definition (around line 331). Add or modify key-value pairs (e.g., `"Purple": "#9c27b0"`).

### To Improve Highlight Matching Logic
*   **Goal:** Make highlighting robust against more complex markdown (e.g., inside tables).
*   **File:** `app/viewer.py`
*   **Action:** Modify the `apply_highlights` function. You can refine the regex patterns in the "Smart Match" section.

### To Customize the Editor Interface
*   **Goal:** Change the editor's background color, font, or add toolbar buttons.
*   **File:** `app/word_editor_component/index.html`
*   **Action:**
    *   **Styles:** Edit the `<style>` block in the `<head>`.
    *   **Behavior:** Edit the JavaScript in the `<script>` block (e.g., to handle paste events differently).

## 5. Data Flow Diagram

<img width="1891" height="773" alt="image" src="https://github.com/user-attachments/assets/b6c036af-949a-4661-94cd-a9d2c84c2168" />

