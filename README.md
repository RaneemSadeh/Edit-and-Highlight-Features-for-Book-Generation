<div align="center">

# ✨Book Generation & Knowledge Base Chat✨

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-Open_Source-brightgreen.svg)](LICENSE)

A sophisticated document processing and conversational AI system that transforms your static documents into an intelligent, interactive knowledge base. Powered by Google's Gemini 2.5 Flash and built with modern Python frameworks, this application enables seamless document ingestion, intelligent consolidation, and context-aware conversations.

---

<img width="1200" height="684" alt="image" src="https://github.com/user-attachments/assets/2d4ec8ad-ed38-4f2f-8523-6a3dbdfedc63" />
</div>


## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [User Guide](#user-guide)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
---

## Overview

The **Book Generation & Knowledge Base Chat** application provides an end-to-end solution for document intelligence. It processes various document formats, extracts and consolidates their content, and enables users to engage in meaningful, context-aware conversations with their data through a natural language interface.

This system is ideal for researchers, students, professionals, and organizations seeking to unlock insights from their document repositories through AI-powered interactions.

---

## Key Features

###  Universal Document Support
Process multiple document formats seamlessly:
- PDF documents
- Microsoft Word files (.docx)
- Plain text files (.txt)
- Markdown files (.md)

###  Intelligent Content Extraction
Leverages **Docling** for accurate document parsing, preserving formatting, structure, and semantic meaning from your source files.

###  Advanced Context Consolidation
Automatically merges content from multiple documents into a unified knowledge base, creating a comprehensive "Base Context" that serves as the foundation for all AI interactions.

###  Interactive Chat with Session Memory
- Multi-turn conversational interface with complete session history
- Context-aware responses based on your uploaded documents
- Natural dialogue flow with memory of previous exchanges

###  Configurable AI Behavior
Fine-tune the AI's response characteristics through adjustable temperature settings, balancing between creative exploration and factual precision.

###  Modern, Scalable Architecture
Built on industry-standard frameworks:
- **FastAPI** backend for high-performance API operations
- **Streamlit** frontend for an intuitive, responsive user experience
- Asynchronous processing for optimal performance

---

## System Architecture

The application follows a three-phase modular architecture: Ingestion, Consolidation, and Interaction.

<img width="1008" height="801" alt="image" src="https://github.com/user-attachments/assets/10787aa1-eb7e-4490-b3e3-7670d8bbaa1e" />


### Architecture Highlights

1. **Separation of Concerns**: Clear boundaries between document processing, AI operations, and user interface
2. **Stateful Sessions**: Persistent conversation history for seamless multi-turn interactions
3. **Modular Design**: Each component can be independently maintained and scaled
4. **Efficient Storage**: File-based persistence for simplicity and portability

---

## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Language** | Python 3.10+ | Core programming language |
| **Backend Framework** | FastAPI | RESTful API and business logic |
| **Frontend Framework** | Streamlit | Interactive user interface |
| **AI Model** | Google Gemini 2.5 Flash | Natural language processing and generation |
| **Document Parser** | Docling | Document extraction and conversion |
| **ASGI Server** | Uvicorn | High-performance async server |
| **Environment Management** | python-dotenv | Secure configuration handling |

---

## Installation

### Prerequisites

Ensure your system meets the following requirements:

- **Python**: Version 3.10 or higher
- **Google Cloud**: Active project with Gemini API enabled
- **API Credentials**: Valid Gemini API key

### Step 1: Clone the Repository

```bash
git clone <repository_url>
cd <project_directory>
```

### Step 2: Create Virtual Environment

It is strongly recommended to use a virtual environment to isolate dependencies:

**On Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Configuration

### Environment Variables

Create a `.env` file in the project root directory to store sensitive configuration:

```bash
cp .env.example .env
```

Edit the `.env` file and add your credentials:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

**Security Note**: Never commit the `.env` file to version control. Ensure it is listed in `.gitignore`.

### Optional Configuration

Additional settings can be configured in the application:

- **Model Temperature**: Adjustable via UI (range: 0.0 - 2.0)
- **Storage Paths**: Configurable in `app/main.py`
- **Model Selection**: Can be modified in `app/chat.py`

---

## Running the Application

The application requires two concurrent processes: the backend API server and the frontend interface.

### Terminal 1: Start the Backend Server

Launch the FastAPI server to handle document processing and AI operations:

```bash
uvicorn app.main:app --reload
```

**Server will be available at:** `http://127.0.0.1:8000`

**API Documentation (Swagger UI):** `http://127.0.0.1:8000/docs`

### Terminal 2: Start the Frontend Interface

Launch the Streamlit application for user interaction:

```bash
streamlit run streamlit_app.py
```

**Application will open automatically at:** `http://localhost:8501`

---

## User Guide

### Workflow Overview

#### 1. Document Upload and Processing

1. Navigate to the **sidebar** in the Streamlit interface
2. Click **"Browse files"** to select your documents (PDF, DOCX, TXT, or MD)
3. Upload multiple files simultaneously if needed
4. Click **"Process Uploaded Files"** to initiate extraction
5. Monitor the progress and wait for confirmation

#### 2. Knowledge Base Consolidation

1. After all files are processed, locate the **"Generate Base Context"** button in the sidebar
2. Click to merge all extracted content into a unified knowledge base
3. The system will create a consolidated context that serves as the foundation for AI interactions
4. Wait for the consolidation confirmation message

#### 3. Interactive Chat

1. Click **"New Chat"** to create a fresh conversation session
2. Adjust the **Temperature** slider to control response creativity:
   - **Lower values (0.0-0.5)**: More factual, focused responses
   - **Medium values (0.5-1.0)**: Balanced creativity and accuracy
   - **Higher values (1.0-2.0)**: More creative, exploratory responses
3. Enter your question in the chat input field
4. The AI will respond based exclusively on the content from your uploaded documents
5. Continue the conversation naturally; the system maintains full context

### Best Practices

- **Document Quality**: Ensure uploaded documents are well-formatted for optimal extraction
- **Consolidation**: Re-consolidate the knowledge base after adding new documents
- **Session Management**: Create new chat sessions for different topics or contexts
- **Temperature Tuning**: Experiment with temperature settings to find the optimal balance for your use case

---

## Project Structure

```
book-generation-kb-chat/
│
├── app/
│   ├── main.py              # FastAPI application and API endpoints
│   ├── chat.py              # Gemini LLM integration and chat logic
│   ├── consolidator.py      # Document consolidation engine
│   └── history.py           # Session management and history persistence
│
├── consolidated_docs/       # Generated knowledge base storage
│   └── base_context.md      # Unified consolidated context
│
├── extracted_docs/          # Intermediate markdown extractions
│   └── *.md                 # Individual document extractions
│
├── uploaded_files/          # Raw uploaded documents
│   └── *.*                  # Original user files
│
├── streamlit_app.py         # Streamlit frontend application
├── requirements.txt         # Python package dependencies
├── .env.example             # Environment variable template
├── .env                     # Local environment configuration (gitignored)
├── .gitignore              # Git ignore patterns
├── README.md               # Project documentation
└── LICENSE                 # License information
```

---

## API Documentation

Once the backend is running, comprehensive API documentation is available through Swagger UI:

**Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/extract/` | POST | Upload and extract content from documents |
| `/consolidate/` | POST | Generate unified knowledge base from extracted documents |
| `/chat/` | POST | Submit questions and receive AI-generated responses |
| `/sessions/` | GET | Retrieve list of active chat sessions |
| `/history/{session_id}` | GET | Fetch conversation history for a specific session |

---

## Acknowledgments

- **Google DeepMind** for the Gemini AI model
- **Docling** team for the document processing library
- The **FastAPI** and **Streamlit** communities for excellent frameworks
