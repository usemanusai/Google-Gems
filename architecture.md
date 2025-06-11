# Custom Gemini Agent GUI Architecture Document

## Introduction / Preamble

[cite_start]This document outlines the overall project architecture for the Custom Gemini Agent GUI.  Its primary goal is to serve as the guiding architectural blueprint for development, ensuring consistency and adherence to the chosen patterns and technologies. It is based on the previously approved PRD and UI/UX Specification.

## Technical Summary

The project is a monolithic Python desktop application for Windows 10, built with the **PyQt6** framework. The architecture is designed around a custom, persistent **Retrieval-Augmented Generation (RAG)** system that uses **ChromaDB** and a local **Sentence-Transformers** model. The system features a modular, service-based backend logic designed for extensibility and continuous, automated monitoring of knowledge sources, including local files, GitHub repositories, and Google Drive. The architecture follows a Model-View-Controller (MVC) pattern to cleanly separate application logic from the user interface.

## High-Level Overview

[cite_start]The system is designed as a single, self-contained desktop application (a monolith) residing within a single repository (a monorepo).  This simplifies development, deployment, and user modification. The primary user interaction involves configuring an AI agent's instructions and knowledge base, and then engaging in a conversation where the AI's responses are augmented by the information retrieved from that knowledge base.

## Architectural / Design Patterns Adopted
* **Model-View-Controller (MVC):** This is the primary high-level pattern.
* **Service-Oriented Architecture:** The backend logic is broken down into distinct, modular services (`ConfigService`, `RAGService`, etc.) with clear responsibilities.
* [cite_start]**Signals and Slots:** The native Qt mechanism for event-driven communication between the View (widgets) and Controllers. 

## Component View (Core Services)
[cite_start]The backend logic is organized into four primary services that manage the application's functionality. 
* **`ConfigService`:** Handles all persistence *except* the RAG database.
* **`APIService`:** Manages all communication with external APIs.
* **`RAGService`:** The central brain of the RAG system.
* **`MonitoringService`:** Fulfills the "continuous monitoring" requirement.

## Project Structure
[cite_start]The project will follow a standard structure for a Python desktop application.


project_root/
├── app/
│   ├── main.py
│   ├── main_window.py
│   ├── controllers/
│   ├── models/
│   ├── services/
│   ├── ui/
│   └── widgets/
├── assets/
├── docs/
├── tests/
└── requirements.txt

## Data Models
* **`KnowledgeSource`:** Represents a single item in the knowledge base. 
* **`GemConfiguration`:** The main structure for the configuration files you will save and load. 

## Core Workflow / Sequence Diagrams
This section illustrates key workflows using Mermaid sequence diagrams. 

## Definitive Tech Stack Selections
This table serves as the single source of truth for all technologies, libraries, and frameworks to be used in the project. 

| Category | Technology | Description / Purpose |
| :--- | :--- | :--- |
| **Languages** | Python | Primary language for the entire application. |
| **UI Framework**| PyQt6 | Core framework for building the desktop user interface.  |
| **Databases** | ChromaDB | The persistent, local vector database for the RAG system.  |
| **AI / ML** | sentence-transformers | The library used to run the local embedding model.  |
| | `msmarco-MiniLM-L-6-v3` | The specific local model for converting text to vectors. |
| | Google Gemini API | The external LLM used for generative responses. |
| **Key Libraries**| watchdog | For monitoring local file system changes. |
| | GitPython | For cloning and interacting with GitHub repositories. |
| | google-api-python-client| For interacting with the Google Drive API. |
| | langchain | Used for its robust document loaders and text splitters. |
| **Testing** | pytest, pytest-qt| Frameworks for testing widgets and application logic.  |
| **Deployment** | PyInstaller | The tool used to package the application into a `.exe`. |

## Security Best Practices
* **API Key Storage:** The user's Google API key must not be stored in plain text. It should be stored securely using the native OS credential manager (e.g., Windows Credential Manager). 