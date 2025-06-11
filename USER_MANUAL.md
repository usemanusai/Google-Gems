# Custom Gemini Agent GUI - User Manual

## 📖 **Complete User Guide**

Welcome to the Custom Gemini Agent GUI - your comprehensive platform for creating, managing, and deploying custom AI assistants with advanced knowledge management capabilities.

## 🚀 **Getting Started**

### **First Launch**
1. **Start the Application**: Launch the Custom Gemini Agent GUI
2. **API Setup**: Go to Settings and enter your Google Gemini API key
3. **Test Connection**: Verify your API connection is working
4. **Choose a Template**: Select from built-in templates or create a custom configuration

### **Quick Start with Templates**
The application includes 6 professional templates to get you started:

- **Research Assistant**: For research and analysis tasks
- **Code Assistant**: For programming and development
- **Writing Assistant**: For content creation and editing
- **Business Analyst**: For business analysis and strategy
- **Learning Tutor**: For education and tutoring
- **Creative Assistant**: For creative projects and brainstorming

## 🏗️ **Interface Overview**

### **Main Window Layout**
The application features a three-panel design:

1. **Left Panel - Instructions**: Configure your AI assistant's behavior and personality
2. **Center Panel - Knowledge Sources**: Manage your knowledge base and data sources
3. **Right Panel - Chat**: Interact with your custom AI assistant

### **Menu System**
- **File**: Configuration management, import/export, backup operations
- **Workspace**: Multi-workspace management and organization
- **Templates**: Template application and creation
- **Settings**: API configuration and application preferences

## 🧠 **Creating Your AI Assistant**

### **Step 1: Define Instructions**
1. **Open Instructions Panel**: Left panel of the main window
2. **Write Clear Instructions**: Define your assistant's role, expertise, and behavior
3. **Be Specific**: Include specific tasks, tone, and response style
4. **Use Examples**: Provide examples of desired responses

**Example Instructions:**
```
You are a technical documentation assistant. Your role is to:
1. Help create clear, comprehensive technical documentation
2. Review and improve existing documentation for clarity
3. Suggest best practices for documentation structure
4. Maintain a professional, helpful tone

Always ask clarifying questions when requirements are unclear.
```

### **Step 2: Add Knowledge Sources**
1. **Open Knowledge Panel**: Center panel of the main window
2. **Choose Source Type**: Files, folders, GitHub repos, Google Drive, or web content
3. **Configure Sources**: Set up your knowledge base with relevant information
4. **Process Sources**: Let the system index and prepare your knowledge

**Supported Source Types:**
- **Local Files**: Documents, PDFs, text files, code files
- **Folders**: Entire directories with automatic monitoring
- **GitHub Repositories**: Public and private repositories
- **Google Drive**: Folders and documents with OAuth integration
- **Web Content**: Single pages, website crawling, or sitemap extraction

### **Step 3: Test and Refine**
1. **Start Chatting**: Use the right panel to interact with your assistant
2. **Test Knowledge**: Ask questions about your knowledge sources
3. **Refine Instructions**: Adjust based on responses and behavior
4. **Add More Sources**: Expand knowledge base as needed

## 📁 **Knowledge Source Management**

### **Adding Local Files and Folders**
1. **Click "Add Files"**: Select individual files or documents
2. **Click "Add Folder"**: Select entire directories for processing
3. **Monitor Changes**: Enable automatic monitoring for file updates
4. **Supported Formats**: TXT, PDF, DOCX, MD, code files, and more

### **GitHub Integration**
1. **Click "Add GitHub"**: Enter repository URL
2. **Authentication**: Provide GitHub token for private repositories
3. **Automatic Processing**: System clones and processes repository content
4. **Update Monitoring**: Automatic updates when repository changes

### **Google Drive Integration**
1. **Setup Authentication**: Configure Google Drive API credentials
2. **Click "Add Google Drive"**: Enter folder URL
3. **OAuth Flow**: Complete authentication process
4. **Automatic Sync**: Process all files in the specified folder

### **Web Content Extraction**
1. **Click "Add URL/Website"**: Enter website URL
2. **Choose Mode**:
   - **Single Page**: Extract content from one page
   - **Crawl Website**: Follow links and extract multiple pages
   - **From Sitemap**: Use sitemap for bulk extraction
3. **Configure Options**: Set crawling limits and domain restrictions

### **Batch Processing**
1. **Select Multiple Sources**: Choose sources for batch processing
2. **Click "Batch Process"**: Start parallel processing
3. **Monitor Progress**: Track processing status and completion
4. **Review Results**: Check for any processing errors

## 🏢 **Workspace Management**

### **Understanding Workspaces**
Workspaces help organize your configurations by project, team, or purpose:
- **Personal**: Individual configurations and projects
- **Team**: Shared configurations for team collaboration
- **Project**: Project-specific AI assistants and knowledge
- **Template**: Template configurations for reuse

### **Creating Workspaces**
1. **Go to Workspace Menu**: Select "New Workspace"
2. **Enter Details**: Name, description, and workspace type
3. **Organize Configurations**: Move or create configurations in the workspace
4. **Share and Collaborate**: Export workspace for team sharing

### **Switching Workspaces**
1. **Workspace Menu**: Select "Switch Workspace"
2. **Choose Workspace**: Select from available workspaces
3. **Automatic Loading**: Configurations and settings load automatically
4. **Session Persistence**: Last workspace remembered across sessions

## 📋 **Template System**

### **Using Built-in Templates**
1. **Templates Menu**: Select "Apply Template"
2. **Choose Template**: Select from 6 professional templates
3. **Name Configuration**: Provide name for new configuration
4. **Customize**: Modify instructions and add knowledge sources

### **Creating Custom Templates**
1. **Configure Assistant**: Set up instructions and knowledge sources
2. **Templates Menu**: Select "Create Template from Current"
3. **Template Details**: Name, description, and category
4. **Save Template**: Template becomes available for future use

### **Template Categories**
- **Research**: Research and analysis assistants
- **Development**: Programming and technical assistants
- **Writing**: Content creation and editing assistants
- **Business**: Business analysis and strategy assistants
- **Education**: Learning and tutoring assistants
- **Creative**: Creative and brainstorming assistants

## 💾 **Configuration Management**

### **Saving Configurations**
1. **Automatic Saving**: Configurations save automatically
2. **Manual Save**: Use File menu "Save Configuration"
3. **Version Tracking**: System tracks usage and modification dates
4. **Metadata**: Rich information including categories and tags

### **Loading Configurations**
1. **File Menu**: Select "Open Configuration"
2. **Recent Configurations**: Quick access to recently used
3. **Workspace Browsing**: Browse configurations by workspace
4. **Search**: Find configurations by name, description, or tags

### **Configuration Manager**
1. **Workspace Menu**: Select "Manage Configurations"
2. **Advanced Interface**: Tabbed interface for comprehensive management
3. **Bulk Operations**: Select multiple configurations for operations
4. **Statistics**: View usage statistics and analytics

## 📤 **Import & Export**

### **Exporting Data**
1. **Single Configuration**: File menu > "Export Configuration"
2. **Entire Workspace**: File menu > "Export Workspace"
3. **Complete Backup**: File menu > "Create Backup"
4. **Options**: Include or exclude knowledge source files

### **Importing Data**
1. **File Menu**: Select "Import from File"
2. **Choose File**: Select exported JSON file
3. **Conflict Resolution**: Choose how to handle existing items:
   - **Skip**: Keep existing, skip imports
   - **Overwrite**: Replace existing with imported
   - **Rename**: Create new items with modified names
4. **Review Results**: Check import summary and any errors

### **Sharing Configurations**
1. **Export Configuration**: Create shareable file
2. **Share File**: Send to team members or colleagues
3. **Import on Target**: Recipients import using standard process
4. **Template Distribution**: Share templates for standardization

## 💬 **Chat Interface**

### **Basic Chat Operations**
1. **Type Message**: Enter your question or request
2. **Send Message**: Press Enter or click Send button
3. **View Response**: AI assistant responds with knowledge-enhanced answers
4. **Continue Conversation**: Build on previous messages for context

### **Advanced Chat Features**
- **Message History**: Scroll through previous conversations
- **Copy Responses**: Copy AI responses for use elsewhere
- **Clear History**: Start fresh conversation when needed
- **Context Awareness**: Assistant remembers conversation context

### **Knowledge Integration**
- **Source Citations**: Responses include relevant knowledge sources
- **Contextual Answers**: AI uses your knowledge base for accurate responses
- **Real-time Processing**: New knowledge sources immediately available
- **Relevance Scoring**: Most relevant information prioritized

## ⚙️ **Settings & Preferences**

### **API Configuration**
1. **Settings Tab**: Access application settings
2. **API Key**: Enter your Google Gemini API key
3. **Test Connection**: Verify API connectivity
4. **Model Selection**: Choose AI model if multiple available

### **Application Preferences**
- **Auto-save**: Configure automatic saving intervals
- **Monitoring**: Enable/disable file system monitoring
- **Batch Processing**: Set worker thread counts
- **UI Preferences**: Panel visibility and layout options

### **Advanced Settings**
- **Chunk Size**: Configure text processing parameters
- **Vector Database**: ChromaDB settings and optimization
- **Memory Limits**: Set memory usage constraints
- **Logging**: Configure logging levels and output

## 🔧 **Troubleshooting**

### **Common Issues**

#### **API Connection Problems**
- **Check API Key**: Verify key is correct and active
- **Network Connection**: Ensure internet connectivity
- **Quota Limits**: Check API usage limits and billing
- **Firewall**: Verify firewall allows API connections

#### **Knowledge Source Issues**
- **File Permissions**: Ensure application can read files
- **File Formats**: Verify files are in supported formats
- **Large Files**: Break down very large files if needed
- **Encoding**: Ensure text files use UTF-8 encoding

#### **Performance Issues**
- **Memory Usage**: Reduce chunk size or batch processing
- **Large Knowledge Bases**: Consider splitting into smaller sets
- **Background Processing**: Allow time for indexing to complete
- **System Resources**: Ensure adequate RAM and storage

### **Getting Help**
1. **Documentation**: Comprehensive guides and references
2. **Error Messages**: Read error messages for specific guidance
3. **Log Files**: Check application logs for detailed information
4. **Community Support**: GitHub issues and community forums

## 🎯 **Best Practices**

### **Creating Effective Instructions**
- **Be Specific**: Clear, detailed instructions work better
- **Include Examples**: Show desired response formats
- **Set Boundaries**: Define what the assistant should and shouldn't do
- **Iterate**: Refine instructions based on actual usage

### **Knowledge Base Management**
- **Organize Sources**: Group related sources in folders
- **Regular Updates**: Keep knowledge sources current
- **Quality Control**: Review sources for accuracy and relevance
- **Size Management**: Balance comprehensiveness with performance

### **Workspace Organization**
- **Logical Grouping**: Organize by project, team, or purpose
- **Naming Conventions**: Use clear, consistent naming
- **Template Usage**: Leverage templates for consistency
- **Regular Cleanup**: Archive or remove unused configurations

### **Collaboration**
- **Template Sharing**: Create and share standard templates
- **Configuration Export**: Share successful configurations
- **Documentation**: Document configuration purposes and usage
- **Version Control**: Track changes and improvements

## 📈 **Advanced Features**

### **Analytics and Insights**
- **Usage Statistics**: Track configuration usage and popularity
- **Performance Metrics**: Monitor response times and accuracy
- **Knowledge Utilization**: See which sources are most valuable
- **Session Analytics**: Understand usage patterns

### **Automation**
- **File Monitoring**: Automatic updates when files change
- **Batch Processing**: Efficient handling of large knowledge sets
- **Scheduled Backups**: Automatic backup creation
- **Template Application**: Quick configuration creation

### **Integration Capabilities**
- **API Extensions**: Connect with external systems
- **Custom Sources**: Add new knowledge source types
- **Workflow Integration**: Embed in existing workflows
- **Data Pipelines**: Automated knowledge ingestion

---

**This user manual provides comprehensive guidance for using all features of the Custom Gemini Agent GUI. For additional support, refer to the documentation or community resources.**
