# Custom Gemini Agent GUI Product Requirements Document (PRD)

## Goal, Objective and Context

[cite_start]The primary goal of this project is to develop a personal, standalone desktop application for Windows 10 that serves as a highly customizable and powerful interface for the Google Gemini API.  The project is born from the need to overcome the limitations of standard web UIs, specifically regarding configuration flexibility and the size of the knowledge base. The objective is to create a robust tool that provides an enhanced user experience with a custom Retrieval-Augmented Generation (RAG) system, giving the user full control over the application's code and functionality.

## Functional Requirements (MVP)

* The system shall provide a GUI for naming an agent and setting its instructions.
* The system shall support knowledge ingestion from local files (one-by-one), a monitored local folder, a GitHub repository URL, and Google Drive.
* The system shall support the ingestion of common document and source code file types (e.g., .txt, .md, .pdf, .docx).
* The system shall implement a custom RAG pipeline using a persistent vector database that is saved to local disk.
* The system shall allow the user to save and load multiple, named "Gem" configurations (Name, Instructions, Knowledge Base file list).
* The system shall automatically remember and reload the last used settings (session state) upon startup.
* [cite_start]The system shall integrate with the Google Gemini API using a user-provided API key. 

## Non Functional Requirements (MVP)

* **Platform:** The application must be a stable, standalone desktop application for Windows 10.
* **Usability:** The UI must be intuitive and clean, based on the modern aesthetic of the user-provided image.
* **Persistence:** All user settings, named configurations, and the RAG vector database must be persistent across application restarts.
* **Modularity:** The application's source code should be well-structured and modular to allow the user to easily customize and extend it.
* [cite_start]**Performance:** The application must be responsive, with fast startups after the initial RAG indexing. 

## User Interaction and Design Goals

The application will feature a modern, clean, and professional look, adhering to the layout presented in the user's reference image. [cite_start]As a PyQt6 application, it should feel like a native Windows tool while incorporating modern design elements.  [cite_start]The user experience should be centered on efficiency and control, allowing the user to quickly configure agents and manage large knowledge bases without friction.  [cite_start]This product-focused vision will be handed off to the Design Architect for detailed UI/UX specification. 

## Technical Assumptions

* **GUI Framework:** The application will be built using **PyQt6**.
* **Platform:** The primary target platform is **Windows 10**.
* **Core API:** The application will use the **Google Gemini API** for its generative AI capabilities.
* [cite_start]**Repository & Service Architecture:** A **Monorepo** and **Monolithic Application Architecture** is the chosen approach. 
    * **Rationale:** As a standalone desktop application for a single user who will also be the primary developer, this approach drastically simplifies the development, debugging, building, and maintenance process. [cite_start]There is no need for the complexity of microservices or multiple repositories. 

## Epic Overview

* **Epic 1: Foundational Setup & Core UI Shell**
    * [cite_start]Goal: To establish the project structure and build a runnable application shell with a non-functional UI layout, providing a visible foundation for all future work. 
    * Story 1.1: As a developer, I want to set up the Python project with PyQt6, dependencies, and a Git repository so that I have a clean, version-controlled starting point.
    * Story 1.2: As a user, I want a main application window with the primary layout sections (Instructions, File List, Chat/Preview) visible so that the core structure of the app is in place.
    * Story 1.3: As a user, I want a settings area where I can input and save my Google API key so that the application can authenticate with the API.
* **Epic 2: Core AI Integration & Chat Functionality**
    * [cite_start]Goal: To enable the core functionality of sending instructions to the Gemini API and receiving a response, making the application a useful chatbot. 
    * [cite_start]Story 2.1: As a user, I want to type in the "Instructions" text area and click a "Run" button to send the content to the Gemini API. 
    * [cite_start]Story 2.2: As a user, I want to see the response from the Gemini API displayed in the "Preview" or chat area. 
    * Story 2.3: As a user, I want to have a conversational chat history within the "Preview" area, so that my interactions with the AI are maintained within a session.
* **Epic 3: Persistent RAG Implementation**
    * [cite_start]Goal: To build the core custom RAG pipeline with a persistent database, enabling the AI to answer questions based on a local knowledge base. 
* **Epic 4: Advanced Knowledge Ingestion Methods**
    * [cite_start]Goal: To provide the user with multiple, flexible methods for building their knowledge base as per the functional requirements. 
* **Epic 5: Configuration & Session Management**
    * [cite_start]Goal: To implement the saving and loading of agent configurations and session state, making the tool convenient and powerful for repeated use. 

## Initial Architect Prompt

Based on our discussions and requirements analysis for the Custom Gemini Agent GUI, I've compiled the following technical guidance to inform your architecture analysis and decisions to kick off Architecture Creation Mode:

### Technical Infrastructure

* [cite_start]**Repository & Service Architecture Decision:** Monorepo with a Monolithic Application Architecture. 
* [cite_start]**Hosting/Cloud Provider:** Specified cloud platform (AWS, Azure, GCP, etc.) or hosting requirements 
* [cite_start]**Frontend Platform:** Framework/library preferences or requirements (React, Angular, Vue, etc.) 
* [cite_start]**Backend Platform:** Framework/language preferences or requirements (Node.js, Python/Django, etc.) 
* [cite_start]**Database Requirements:** Relational, NoSQL, specific products or services preferred 

### Deployment Considerations

* [cite_start]CI/CD requirements 
* [cite_start]Environment requirements (local, dev, staging, production)