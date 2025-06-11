# Visual Architecture Guide - Custom Gemini Agent GUI

## 📊 **Comprehensive Visual Documentation**

This guide provides detailed visual representations of the Custom Gemini Agent GUI architecture, workflows, and data structures to help developers, users, and stakeholders understand the sophisticated system we've built.

## 🏗️ **1. System Architecture Overview**

### **Epic-Based Architecture Evolution**

The application evolved through 5 major epics, each building upon the previous foundation:

```mermaid
graph TB
    subgraph "Epic 1: Core Infrastructure"
        UI[PyQt6 UI Framework]
        API[Google Gemini API]
        CONFIG[Configuration Management]
        LOG[Logging System]
    end
    
    subgraph "Epic 2: Enhanced UI/UX"
        MAIN[Main Window]
        INST[Instructions Widget]
        KNOW[Knowledge Widget]
        CHAT[Chat Widget]
        SET[Settings Widget]
    end
    
    subgraph "Epic 3: Persistent RAG"
        CHROMA[ChromaDB Vector Store]
        EMBED[Text Embedding]
        CHUNK[Document Chunking]
        SEARCH[Semantic Search]
        MONITOR[File Monitoring]
    end
    
    subgraph "Epic 4: Advanced Ingestion"
        LOCAL[Local Files/Folders]
        GITHUB[GitHub Integration]
        GDRIVE[Google Drive API]
        WEB[Web Scraping]
        BATCH[Batch Processing]
    end
    
    subgraph "Epic 5: Configuration Management"
        WORKSPACE[Multi-Workspace]
        TEMPLATE[Template System]
        IMPORT[Import/Export]
        SESSION[Session Management]
        MANAGER[Config Manager UI]
    end
    
    subgraph "Core Services Layer"
        CONTROLLER[Main Controller]
        RAGSERV[RAG Service]
        APISERVICE[API Service]
        CONFIGSERV[Config Service]
        WORKSERV[Workspace Service]
        TEMPSERV[Template Service]
        SESSSERV[Session Service]
        IMPEXPSERV[Import/Export Service]
    end
    
    %% Epic 1 Connections
    UI --> MAIN
    API --> APISERVICE
    CONFIG --> CONFIGSERV
    
    %% Epic 2 Connections
    MAIN --> INST
    MAIN --> KNOW
    MAIN --> CHAT
    MAIN --> SET
    
    %% Epic 3 Connections
    RAGSERV --> CHROMA
    RAGSERV --> EMBED
    RAGSERV --> CHUNK
    RAGSERV --> SEARCH
    MONITOR --> RAGSERV
    
    %% Epic 4 Connections
    LOCAL --> RAGSERV
    GITHUB --> RAGSERV
    GDRIVE --> RAGSERV
    WEB --> RAGSERV
    BATCH --> RAGSERV
    
    %% Epic 5 Connections
    WORKSPACE --> WORKSERV
    TEMPLATE --> TEMPSERV
    IMPORT --> IMPEXPSERV
    SESSION --> SESSSERV
    MANAGER --> WORKSERV
    
    %% Service Layer Connections
    CONTROLLER --> RAGSERV
    CONTROLLER --> APISERVICE
    CONTROLLER --> CONFIGSERV
    CONTROLLER --> WORKSERV
    CONTROLLER --> TEMPSERV
    CONTROLLER --> SESSSERV
    CONTROLLER --> IMPEXPSERV
    
    %% UI to Controller
    MAIN --> CONTROLLER
    INST --> CONTROLLER
    KNOW --> CONTROLLER
    CHAT --> CONTROLLER
    SET --> CONTROLLER
    MANAGER --> CONTROLLER
    
    %% Data Flow
    CHROMA --> APISERVICE
    APISERVICE --> CHAT
    
    classDef epic1 fill:#e1f5fe
    classDef epic2 fill:#f3e5f5
    classDef epic3 fill:#e8f5e8
    classDef epic4 fill:#fff3e0
    classDef epic5 fill:#fce4ec
    classDef services fill:#f5f5f5
    
    class UI,API,CONFIG,LOG epic1
    class MAIN,INST,KNOW,CHAT,SET epic2
    class CHROMA,EMBED,CHUNK,SEARCH,MONITOR epic3
    class LOCAL,GITHUB,GDRIVE,WEB,BATCH epic4
    class WORKSPACE,TEMPLATE,IMPORT,SESSION,MANAGER epic5
    class CONTROLLER,RAGSERV,APISERVICE,CONFIGSERV,WORKSERV,TEMPSERV,SESSSERV,IMPEXPSERV services
```

**Architecture Highlights:**
- **Layered Design**: Clear separation between UI, Controller, Services, and Data layers
- **Epic Evolution**: Each epic adds capabilities without disrupting existing functionality
- **Service-Oriented**: Modular services enable independent development and testing
- **Data Flow**: Efficient data flow from knowledge sources through RAG to AI responses

## 🔄 **2. RAG Pipeline Data Flow**

### **Document Ingestion to AI Response Pipeline**

```mermaid
flowchart TD
    subgraph "Knowledge Sources"
        FILES[📄 Local Files]
        FOLDERS[📁 Folders]
        GITHUB[🐙 GitHub Repos]
        GDRIVE[☁️ Google Drive]
        WEB[🌐 Web Content]
    end
    
    subgraph "Document Processing Pipeline"
        DETECT[🔍 Format Detection]
        EXTRACT[📝 Text Extraction]
        CLEAN[🧹 Text Cleaning]
        CHUNK[✂️ Text Chunking]
        EMBED[🧠 Generate Embeddings]
    end
    
    subgraph "Vector Storage"
        CHROMA[(🗄️ ChromaDB)]
        METADATA[📊 Metadata Store]
        INDEX[🔗 Vector Index]
    end
    
    subgraph "Query Processing"
        USER_Q[❓ User Question]
        Q_EMBED[🧠 Query Embedding]
        SEARCH[🔍 Semantic Search]
        RETRIEVE[📋 Retrieve Context]
        RANK[📈 Relevance Ranking]
    end
    
    subgraph "AI Response Generation"
        CONTEXT[📄 Context Assembly]
        PROMPT[💭 Prompt Construction]
        GEMINI[🤖 Google Gemini API]
        RESPONSE[💬 AI Response]
        CITATIONS[📚 Source Citations]
    end
    
    subgraph "User Interface"
        CHAT_UI[💻 Chat Interface]
        DISPLAY[📺 Response Display]
        FEEDBACK[👍 User Feedback]
    end
    
    %% Document Ingestion Flow
    FILES --> DETECT
    FOLDERS --> DETECT
    GITHUB --> DETECT
    GDRIVE --> DETECT
    WEB --> DETECT
    
    DETECT --> EXTRACT
    EXTRACT --> CLEAN
    CLEAN --> CHUNK
    CHUNK --> EMBED
    
    %% Storage Flow
    EMBED --> CHROMA
    CHUNK --> METADATA
    EMBED --> INDEX
    
    %% Query Flow
    USER_Q --> Q_EMBED
    Q_EMBED --> SEARCH
    SEARCH --> CHROMA
    CHROMA --> RETRIEVE
    RETRIEVE --> RANK
    
    %% Response Generation Flow
    RANK --> CONTEXT
    USER_Q --> PROMPT
    CONTEXT --> PROMPT
    PROMPT --> GEMINI
    GEMINI --> RESPONSE
    CONTEXT --> CITATIONS
    
    %% UI Flow
    RESPONSE --> CHAT_UI
    CITATIONS --> CHAT_UI
    CHAT_UI --> DISPLAY
    DISPLAY --> FEEDBACK
    
    %% Monitoring and Updates
    MONITOR[👁️ File Monitoring] --> DETECT
    FEEDBACK --> RANK
    
    classDef sources fill:#e3f2fd
    classDef processing fill:#f1f8e9
    classDef storage fill:#fff3e0
    classDef query fill:#fce4ec
    classDef ai fill:#f3e5f5
    classDef ui fill:#e8f5e8
    
    class FILES,FOLDERS,GITHUB,GDRIVE,WEB sources
    class DETECT,EXTRACT,CLEAN,CHUNK,EMBED processing
    class CHROMA,METADATA,INDEX storage
    class USER_Q,Q_EMBED,SEARCH,RETRIEVE,RANK query
    class CONTEXT,PROMPT,GEMINI,RESPONSE,CITATIONS ai
    class CHAT_UI,DISPLAY,FEEDBACK ui
```

**Pipeline Features:**
- **Multi-Source Ingestion**: Supports 5 different knowledge source types
- **Intelligent Processing**: Format detection and optimized text extraction
- **Persistent Storage**: ChromaDB provides reliable vector storage
- **Semantic Search**: Advanced relevance ranking and context retrieval
- **Real-time Updates**: File monitoring enables automatic reprocessing

## 🏢 **3. Multi-Workspace Management System**

### **Workspace Organization and Management**

```mermaid
graph TB
    subgraph "Workspace Types"
        PERSONAL[👤 Personal Workspace]
        TEAM[👥 Team Workspace]
        PROJECT[📋 Project Workspace]
        TEMPLATE[📄 Template Workspace]
    end
    
    subgraph "Personal Workspace"
        P_CONFIG1[Research Assistant]
        P_CONFIG2[Code Helper]
        P_CONFIG3[Writing Assistant]
        P_KNOWLEDGE1[(Personal Docs)]
        P_KNOWLEDGE2[(Code Projects)]
    end
    
    subgraph "Team Workspace"
        T_CONFIG1[Team Standards Bot]
        T_CONFIG2[Code Review Assistant]
        T_CONFIG3[Documentation Helper]
        T_KNOWLEDGE1[(Team Guidelines)]
        T_KNOWLEDGE2[(Shared Codebase)]
        T_KNOWLEDGE3[(Meeting Notes)]
    end
    
    subgraph "Project Workspace"
        PR_CONFIG1[Project Analyst]
        PR_CONFIG2[Technical Writer]
        PR_CONFIG3[QA Assistant]
        PR_KNOWLEDGE1[(Project Specs)]
        PR_KNOWLEDGE2[(Requirements)]
        PR_KNOWLEDGE3[(Test Cases)]
    end
    
    subgraph "Template Workspace"
        TEMP1[Research Template]
        TEMP2[Code Template]
        TEMP3[Business Template]
        TEMP4[Writing Template]
        TEMP5[Learning Template]
        TEMP6[Creative Template]
    end
    
    subgraph "Workspace Management"
        WM[Workspace Manager]
        SWITCH[Workspace Switcher]
        IMPORT[Import/Export]
        BACKUP[Backup System]
        ANALYTICS[Usage Analytics]
    end
    
    subgraph "Configuration Management"
        CONFIG_MANAGER[Configuration Manager]
        TEMPLATE_BROWSER[Template Browser]
        SEARCH[Search & Filter]
        DUPLICATE[Duplicate Configs]
        MOVE[Move Between Workspaces]
    end
    
    subgraph "Session Management"
        SESSION[Session State]
        RECENT[Recent Configs]
        WINDOW_STATE[Window Geometry]
        PANEL_STATE[Panel States]
        CHAT_HISTORY[Chat History]
    end
    
    %% Workspace connections
    PERSONAL --> P_CONFIG1
    PERSONAL --> P_CONFIG2
    PERSONAL --> P_CONFIG3
    P_CONFIG1 --> P_KNOWLEDGE1
    P_CONFIG2 --> P_KNOWLEDGE2
    P_CONFIG3 --> P_KNOWLEDGE1
    
    TEAM --> T_CONFIG1
    TEAM --> T_CONFIG2
    TEAM --> T_CONFIG3
    T_CONFIG1 --> T_KNOWLEDGE1
    T_CONFIG2 --> T_KNOWLEDGE2
    T_CONFIG3 --> T_KNOWLEDGE3
    
    PROJECT --> PR_CONFIG1
    PROJECT --> PR_CONFIG2
    PROJECT --> PR_CONFIG3
    PR_CONFIG1 --> PR_KNOWLEDGE1
    PR_CONFIG2 --> PR_KNOWLEDGE2
    PR_CONFIG3 --> PR_KNOWLEDGE3
    
    TEMPLATE --> TEMP1
    TEMPLATE --> TEMP2
    TEMPLATE --> TEMP3
    TEMPLATE --> TEMP4
    TEMPLATE --> TEMP5
    TEMPLATE --> TEMP6
    
    %% Management connections
    WM --> PERSONAL
    WM --> TEAM
    WM --> PROJECT
    WM --> TEMPLATE
    
    SWITCH --> WM
    IMPORT --> WM
    BACKUP --> WM
    ANALYTICS --> WM
    
    CONFIG_MANAGER --> WM
    TEMPLATE_BROWSER --> TEMPLATE
    SEARCH --> CONFIG_MANAGER
    DUPLICATE --> CONFIG_MANAGER
    MOVE --> CONFIG_MANAGER
    
    SESSION --> SWITCH
    RECENT --> SESSION
    WINDOW_STATE --> SESSION
    PANEL_STATE --> SESSION
    CHAT_HISTORY --> SESSION
    
    %% Template application
    TEMP1 -.-> P_CONFIG1
    TEMP2 -.-> P_CONFIG2
    TEMP3 -.-> T_CONFIG1
    TEMP4 -.-> PR_CONFIG2
    
    classDef workspace fill:#e3f2fd
    classDef personal fill:#e8f5e8
    classDef team fill:#fff3e0
    classDef project fill:#f3e5f5
    classDef template fill:#fce4ec
    classDef management fill:#f1f8e9
    classDef session fill:#e0f2f1
    
    class PERSONAL,TEAM,PROJECT,TEMPLATE workspace
    class P_CONFIG1,P_CONFIG2,P_CONFIG3,P_KNOWLEDGE1,P_KNOWLEDGE2 personal
    class T_CONFIG1,T_CONFIG2,T_CONFIG3,T_KNOWLEDGE1,T_KNOWLEDGE2,T_KNOWLEDGE3 team
    class PR_CONFIG1,PR_CONFIG2,PR_CONFIG3,PR_KNOWLEDGE1,PR_KNOWLEDGE2,PR_KNOWLEDGE3 project
    class TEMP1,TEMP2,TEMP3,TEMP4,TEMP5,TEMP6 template
    class WM,SWITCH,IMPORT,BACKUP,ANALYTICS,CONFIG_MANAGER,TEMPLATE_BROWSER,SEARCH,DUPLICATE,MOVE management
    class SESSION,RECENT,WINDOW_STATE,PANEL_STATE,CHAT_HISTORY session
```

**Workspace Features:**
- **Multi-Type Support**: Personal, Team, Project, and Template workspaces
- **Configuration Organization**: Logical grouping of AI assistants by purpose
- **Template Integration**: Built-in templates for quick configuration creation
- **Session Persistence**: Complete state management across workspace switches
- **Advanced Management**: Search, filter, duplicate, and move operations

## 📊 **4. Database Schema and Data Relationships**

### **ChromaDB Vector Storage Schema**

```mermaid
erDiagram
    COLLECTIONS {
        string collection_id PK
        string name
        json metadata
        datetime created_at
        datetime updated_at
        int document_count
        string embedding_model
    }
    
    DOCUMENTS {
        string document_id PK
        string collection_id FK
        string source_path
        string source_type
        string filename
        string content_hash
        text original_content
        json metadata
        datetime created_at
        datetime updated_at
        int chunk_count
    }
    
    CHUNKS {
        string chunk_id PK
        string document_id FK
        string collection_id FK
        text content
        vector embedding
        int chunk_index
        int start_position
        int end_position
        json metadata
        datetime created_at
        float relevance_score
    }
    
    EMBEDDINGS {
        string embedding_id PK
        string chunk_id FK
        vector embedding_vector
        string model_name
        int vector_dimension
        datetime created_at
        json model_metadata
    }
    
    KNOWLEDGE_SOURCES {
        string source_id PK
        string collection_id FK
        string source_type
        string source_path
        string source_name
        json source_config
        string status
        datetime last_processed
        datetime created_at
        datetime updated_at
        int document_count
        boolean monitoring_enabled
    }
    
    CONFIGURATIONS {
        string config_id PK
        string name
        text instructions
        string description
        string category
        json tags
        json knowledge_sources
        json settings
        datetime created_at
        datetime modified_at
        datetime last_used_at
        int usage_count
        int total_messages
        string template_id
        boolean is_shared
    }
    
    WORKSPACES {
        string workspace_id PK
        string name
        string description
        string workspace_type
        json configurations
        json settings
        datetime created_at
        datetime modified_at
        string created_by
        boolean is_shared
        json permissions
        string color
        string icon
    }
    
    TEMPLATES {
        string template_id PK
        string name
        string description
        string category
        text instructions
        json default_knowledge_sources
        json settings
        json tags
        datetime created_at
        string created_by
        string version
        boolean is_builtin
    }
    
    SESSIONS {
        string session_id PK
        string current_workspace_id FK
        string current_configuration_id FK
        json window_geometry
        json panel_states
        json recent_configurations
        json chat_history
        datetime created_at
        datetime last_active_at
    }
    
    COLLECTIONS ||--o{ DOCUMENTS : contains
    DOCUMENTS ||--o{ CHUNKS : split_into
    CHUNKS ||--|| EMBEDDINGS : has
    COLLECTIONS ||--o{ KNOWLEDGE_SOURCES : sources
    WORKSPACES ||--o{ CONFIGURATIONS : contains
    TEMPLATES ||--o{ CONFIGURATIONS : creates
    SESSIONS }o--|| WORKSPACES : current
    SESSIONS }o--|| CONFIGURATIONS : current
```

**Schema Highlights:**
- **Hierarchical Structure**: Collections → Documents → Chunks → Embeddings
- **Rich Metadata**: Comprehensive tracking of all entities and relationships
- **Performance Optimized**: Efficient indexing and foreign key relationships
- **Audit Trail**: Complete timestamp tracking for all operations
- **Scalable Design**: Supports enterprise-level data volumes

## 📋 **5. Cross-Reference Guide**

### **Diagram Usage by Documentation**

| Document | Diagrams Included | Purpose |
|----------|------------------|---------|
| **README.md** | System Architecture, RAG Pipeline | Project overview and technical introduction |
| **USER_MANUAL.md** | Agent Creation Workflow, Knowledge Ingestion, Multi-Workspace | User guidance and tutorials |
| **DEPLOYMENT_GUIDE.md** | Service Architecture, Database Schema | Technical deployment and configuration |
| **PROJECT_FINAL_SUMMARY.md** | Complete Architecture Overview | Comprehensive project documentation |
| **VISUAL_ARCHITECTURE_GUIDE.md** | All diagrams with detailed explanations | Complete visual reference |

### **Diagram Types and Applications**

- **System Architecture**: Understanding overall application structure
- **Data Flow**: Following information from input to output
- **User Workflows**: Step-by-step process guidance
- **Service Architecture**: Technical implementation details
- **Database Schema**: Data structure and relationships
- **Multi-Workspace**: Organization and management concepts

---

**This visual architecture guide provides comprehensive diagrams to understand every aspect of the Custom Gemini Agent GUI, from high-level architecture to detailed data flows and user workflows.**
