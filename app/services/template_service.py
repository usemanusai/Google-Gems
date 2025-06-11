"""
Template Service

Manages configuration templates, built-in templates, and template operations.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from loguru import logger

from models.workspace import ConfigurationTemplate
from services.config_service import ConfigService


class TemplateService:
    """Service for managing configuration templates."""
    
    def __init__(self, config_service: ConfigService):
        self.config_service = config_service
        self.templates_dir = config_service.get_app_directory() / "templates"
        self.builtin_templates_dir = Path(__file__).parent.parent / "templates"
        
        # Create directories
        self.templates_dir.mkdir(exist_ok=True)
        
        # Initialize built-in templates
        self._initialize_builtin_templates()
    
    def _initialize_builtin_templates(self):
        """Initialize built-in templates."""
        builtin_templates = [
            ConfigurationTemplate(
                name="Research Assistant",
                description="AI assistant specialized in research and analysis",
                category="research",
                instructions="""You are a research assistant AI. Your role is to:

1. Help users find and analyze information
2. Provide well-sourced, accurate responses
3. Break down complex topics into understandable parts
4. Suggest additional research directions
5. Maintain objectivity and cite sources when possible

Always ask clarifying questions when the research topic is broad or unclear.""",
                tags=["research", "analysis", "academic"],
                is_builtin=True
            ),
            
            ConfigurationTemplate(
                name="Code Assistant",
                description="AI assistant for programming and software development",
                category="development",
                instructions="""You are a code assistant AI. Your expertise includes:

1. Writing clean, efficient, and well-documented code
2. Debugging and troubleshooting issues
3. Code review and optimization suggestions
4. Explaining programming concepts and best practices
5. Helping with architecture and design decisions

Always provide working code examples and explain your reasoning. Ask about the specific programming language, framework, or context when needed.""",
                tags=["programming", "development", "coding"],
                is_builtin=True
            ),
            
            ConfigurationTemplate(
                name="Writing Assistant",
                description="AI assistant for writing, editing, and content creation",
                category="writing",
                instructions="""You are a writing assistant AI. You excel at:

1. Helping with various forms of writing (essays, articles, reports, creative writing)
2. Editing and proofreading for grammar, style, and clarity
3. Providing structure and organization suggestions
4. Adapting tone and style for different audiences
5. Brainstorming ideas and overcoming writer's block

Always ask about the target audience, purpose, and desired tone before providing writing assistance.""",
                tags=["writing", "editing", "content"],
                is_builtin=True
            ),
            
            ConfigurationTemplate(
                name="Business Analyst",
                description="AI assistant for business analysis and strategy",
                category="business",
                instructions="""You are a business analyst AI. Your capabilities include:

1. Analyzing business problems and opportunities
2. Creating strategic recommendations
3. Market research and competitive analysis
4. Financial analysis and forecasting
5. Process improvement suggestions

Always ask for relevant business context, industry information, and specific goals before providing analysis.""",
                tags=["business", "strategy", "analysis"],
                is_builtin=True
            ),
            
            ConfigurationTemplate(
                name="Learning Tutor",
                description="AI assistant for education and learning support",
                category="education",
                instructions="""You are a learning tutor AI. Your teaching approach includes:

1. Adapting explanations to the learner's level
2. Using examples and analogies to clarify concepts
3. Providing practice problems and exercises
4. Encouraging critical thinking and questions
5. Breaking down complex topics into manageable steps

Always assess the learner's current understanding and adjust your teaching style accordingly.""",
                tags=["education", "tutoring", "learning"],
                is_builtin=True
            ),
            
            ConfigurationTemplate(
                name="Creative Assistant",
                description="AI assistant for creative projects and brainstorming",
                category="creative",
                instructions="""You are a creative assistant AI. You specialize in:

1. Brainstorming creative ideas and concepts
2. Helping with artistic and design projects
3. Story development and creative writing
4. Problem-solving through creative thinking
5. Inspiration and motivation for creative work

Encourage experimentation, think outside the box, and help users explore unconventional approaches.""",
                tags=["creative", "brainstorming", "art"],
                is_builtin=True
            )
        ]
        
        # Save built-in templates if they don't exist
        for template in builtin_templates:
            if not self._template_exists(template.name):
                self.save_template(template)
                logger.info(f"Initialized built-in template: {template.name}")
    
    def save_template(self, template: ConfigurationTemplate) -> bool:
        """Save a template to file."""
        try:
            template_file = self.templates_dir / f"{template.name.replace(' ', '_').lower()}.json"
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template.model_dump(), f, indent=2, default=str)
            logger.info(f"Template '{template.name}' saved")
            return True
        except Exception as e:
            logger.error(f"Failed to save template: {e}")
            return False
    
    def load_template(self, name: str) -> Optional[ConfigurationTemplate]:
        """Load a template by name."""
        try:
            template_file = self.templates_dir / f"{name.replace(' ', '_').lower()}.json"
            if template_file.exists():
                with open(template_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return ConfigurationTemplate(**data)
            else:
                logger.warning(f"Template '{name}' not found")
                return None
        except Exception as e:
            logger.error(f"Failed to load template '{name}': {e}")
            return None
    
    def list_templates(self, category: Optional[str] = None) -> List[ConfigurationTemplate]:
        """List all available templates."""
        templates = []
        
        try:
            template_files = list(self.templates_dir.glob("*.json"))
            
            for template_file in template_files:
                try:
                    with open(template_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    template = ConfigurationTemplate(**data)
                    
                    # Filter by category if specified
                    if category is None or template.category == category:
                        templates.append(template)
                        
                except Exception as e:
                    logger.error(f"Failed to load template file {template_file}: {e}")
                    continue
            
            # Sort by name
            templates.sort(key=lambda t: t.name)
            
        except Exception as e:
            logger.error(f"Failed to list templates: {e}")
        
        return templates
    
    def get_categories(self) -> List[str]:
        """Get all template categories."""
        templates = self.list_templates()
        categories = list(set(template.category for template in templates))
        categories.sort()
        return categories
    
    def delete_template(self, name: str) -> bool:
        """Delete a template."""
        try:
            # Check if it's a built-in template
            template = self.load_template(name)
            if template and template.is_builtin:
                logger.warning(f"Cannot delete built-in template: {name}")
                return False
            
            template_file = self.templates_dir / f"{name.replace(' ', '_').lower()}.json"
            if template_file.exists():
                template_file.unlink()
                logger.info(f"Template '{name}' deleted")
                return True
            else:
                logger.warning(f"Template '{name}' not found")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete template '{name}': {e}")
            return False
    
    def create_template_from_configuration(self, config, name: str, description: str = "", 
                                         category: str = "custom") -> Optional[ConfigurationTemplate]:
        """Create a template from an existing configuration."""
        try:
            template = ConfigurationTemplate(
                name=name,
                description=description,
                category=category,
                instructions=config.instructions,
                default_knowledge_sources=config.knowledge_sources,
                settings=getattr(config, 'settings', {}),
                tags=getattr(config, 'tags', [])
            )
            
            if self.save_template(template):
                logger.info(f"Created template '{name}' from configuration")
                return template
            else:
                return None
                
        except Exception as e:
            logger.error(f"Failed to create template from configuration: {e}")
            return None
    
    def apply_template(self, template_name: str, config_name: str) -> Optional[Dict[str, Any]]:
        """Apply a template to create a new configuration."""
        try:
            template = self.load_template(template_name)
            if not template:
                return None
            
            # Create configuration data from template
            config_data = {
                "name": config_name,
                "instructions": template.instructions,
                "knowledge_sources": template.default_knowledge_sources.copy(),
                "description": f"Created from template: {template.name}",
                "category": template.category,
                "tags": template.tags.copy(),
                "template_id": template.id,
                "template_version": template.version,
                "settings": template.settings.copy()
            }
            
            logger.info(f"Applied template '{template_name}' to create configuration '{config_name}'")
            return config_data
            
        except Exception as e:
            logger.error(f"Failed to apply template: {e}")
            return None
    
    def search_templates(self, query: str) -> List[ConfigurationTemplate]:
        """Search templates by name, description, or tags."""
        templates = self.list_templates()
        query_lower = query.lower()
        
        matching_templates = []
        
        for template in templates:
            # Search in name, description, and tags
            if (query_lower in template.name.lower() or
                query_lower in template.description.lower() or
                any(query_lower in tag.lower() for tag in template.tags)):
                matching_templates.append(template)
        
        return matching_templates
    
    def _template_exists(self, name: str) -> bool:
        """Check if a template exists."""
        template_file = self.templates_dir / f"{name.replace(' ', '_').lower()}.json"
        return template_file.exists()
    
    def export_templates(self, template_names: List[str]) -> Optional[Dict[str, Any]]:
        """Export templates to a dictionary for sharing."""
        try:
            exported_templates = []
            
            for name in template_names:
                template = self.load_template(name)
                if template:
                    exported_templates.append(template.model_dump())
            
            export_data = {
                "version": "1.0.0",
                "export_type": "templates",
                "templates": exported_templates
            }
            
            return export_data
            
        except Exception as e:
            logger.error(f"Failed to export templates: {e}")
            return None
    
    def import_templates(self, import_data: Dict[str, Any]) -> bool:
        """Import templates from exported data."""
        try:
            if import_data.get("export_type") != "templates":
                logger.error("Invalid import data: not a template export")
                return False
            
            templates_data = import_data.get("templates", [])
            imported_count = 0
            
            for template_data in templates_data:
                try:
                    template = ConfigurationTemplate(**template_data)
                    
                    # Check if template already exists
                    if self._template_exists(template.name):
                        logger.warning(f"Template '{template.name}' already exists, skipping")
                        continue
                    
                    if self.save_template(template):
                        imported_count += 1
                        
                except Exception as e:
                    logger.error(f"Failed to import template: {e}")
                    continue
            
            logger.info(f"Imported {imported_count} templates")
            return imported_count > 0
            
        except Exception as e:
            logger.error(f"Failed to import templates: {e}")
            return False
