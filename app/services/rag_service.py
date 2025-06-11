"""
RAG Service

Handles the Retrieval-Augmented Generation system including document processing,
vector storage, and similarity search.
"""

import os
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from loguru import logger

# Try to import optional dependencies
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    logger.warning("ChromaDB not available")
    CHROMADB_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.warning("sentence-transformers not available")
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.document_loaders import (
        TextLoader, PyPDFLoader, Docx2txtLoader,
        DirectoryLoader, GitLoader
    )
    LANGCHAIN_AVAILABLE = True
except ImportError:
    logger.warning("langchain not available")
    LANGCHAIN_AVAILABLE = False

from models.knowledge_source import KnowledgeSource, SourceType, SourceStatus
from services.config_service import ConfigService
from services.google_drive_service import GoogleDriveService
from services.web_scraping_service import WebScrapingService


class RAGService:
    """Service for managing the RAG system."""
    
    def __init__(self, config_service: ConfigService):
        self.config_service = config_service
        self.embedding_model = None
        self.chroma_client = None
        self.collection = None
        self.text_splitter = None

        # Initialize advanced ingestion services
        self.google_drive_service = GoogleDriveService(config_service)
        self.web_scraping_service = WebScrapingService()

        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize RAG components."""
        try:
            # Check if required dependencies are available
            if not SENTENCE_TRANSFORMERS_AVAILABLE:
                logger.warning("sentence-transformers not available, RAG functionality limited")
                return

            if not CHROMADB_AVAILABLE:
                logger.warning("ChromaDB not available, RAG functionality limited")
                return

            if not LANGCHAIN_AVAILABLE:
                logger.warning("langchain not available, document processing limited")
                return

            # Initialize embedding model
            model_name = self.config_service.settings.embedding_model
            logger.info(f"Loading embedding model: {model_name}")
            self.embedding_model = SentenceTransformer(model_name)

            # Initialize ChromaDB
            db_path = self.config_service.get_app_directory() / "chroma_db"
            db_path.mkdir(exist_ok=True)

            self.chroma_client = chromadb.PersistentClient(
                path=str(db_path),
                settings=Settings(anonymized_telemetry=False)
            )

            # Get or create collection
            self.collection = self.chroma_client.get_or_create_collection(
                name="knowledge_base",
                metadata={"description": "Main knowledge base collection"}
            )

            # Initialize text splitters for different content types
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.config_service.settings.chunk_size,
                chunk_overlap=self.config_service.settings.chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )

            # Code-specific splitter
            self.code_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.config_service.settings.chunk_size,
                chunk_overlap=50,  # Smaller overlap for code
                length_function=len,
                separators=["\n\nclass ", "\n\ndef ", "\n\nfunction ", "\n\n", "\n", " ", ""]
            )

            # Markdown-specific splitter
            self.markdown_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.config_service.settings.chunk_size,
                chunk_overlap=self.config_service.settings.chunk_overlap,
                length_function=len,
                separators=["\n## ", "\n### ", "\n#### ", "\n\n", "\n", " ", ""]
            )

            logger.info("RAG service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {e}")
            # Don't raise exception, just log it so app can continue without RAG
    
    def process_knowledge_source(self, source: KnowledgeSource) -> bool:
        """Process a knowledge source and add it to the vector database."""
        try:
            if not self._is_rag_available():
                logger.warning("RAG components not available, skipping processing")
                source.update_status(SourceStatus.ERROR, "RAG components not available")
                return False

            logger.info(f"Processing knowledge source: {source.get_display_name()}")
            source.update_status(SourceStatus.PROCESSING)

            # Load documents based on source type
            documents = self._load_documents(source)
            if not documents:
                source.update_status(SourceStatus.ERROR, "No documents loaded")
                return False

            # Split documents into chunks with smart chunking
            chunks = []
            for doc in documents:
                doc_chunks = self._smart_chunk_document(doc)
                for i, chunk in enumerate(doc_chunks):
                    chunks.append({
                        "content": chunk,
                        "metadata": {
                            **doc["metadata"],
                            "chunk_index": i,
                            "source_id": source.id,
                            "chunk_type": self._determine_chunk_type(doc["metadata"].get("file_type", ""))
                        }
                    })

            if not chunks:
                source.update_status(SourceStatus.ERROR, "No chunks created")
                return False

            # Generate embeddings and store in ChromaDB
            self._store_chunks(chunks, source.id)

            # Update source status
            source.file_count = len(documents)
            source.chunk_count = len(chunks)
            source.update_status(SourceStatus.INDEXED)

            logger.info(f"Successfully processed {len(documents)} documents, {len(chunks)} chunks")
            return True

        except Exception as e:
            logger.error(f"Failed to process knowledge source: {e}")
            source.update_status(SourceStatus.ERROR, str(e))
            return False

    def _is_rag_available(self) -> bool:
        """Check if RAG components are available."""
        return (CHROMADB_AVAILABLE and SENTENCE_TRANSFORMERS_AVAILABLE and
                LANGCHAIN_AVAILABLE and self.embedding_model is not None)

    def _smart_chunk_document(self, doc: Dict[str, Any]) -> List[str]:
        """Apply smart chunking based on document type."""
        content = doc["content"]
        file_type = doc["metadata"].get("file_type", "").lower()

        # Choose appropriate splitter based on file type
        if file_type in ['.py', '.js', '.java', '.cpp', '.c', '.h', '.php', '.rb', '.go', '.rs']:
            return self.code_splitter.split_text(content)
        elif file_type in ['.md', '.rst']:
            return self.markdown_splitter.split_text(content)
        else:
            return self.text_splitter.split_text(content)

    def _determine_chunk_type(self, file_type: str) -> str:
        """Determine the type of content for better retrieval."""
        file_type = file_type.lower()

        if file_type in ['.py', '.js', '.java', '.cpp', '.c', '.h', '.php', '.rb', '.go', '.rs']:
            return "code"
        elif file_type in ['.md', '.rst', '.txt']:
            return "documentation"
        elif file_type in ['.pdf', '.docx', '.doc']:
            return "document"
        elif file_type in ['.json', '.xml', '.yml', '.yaml']:
            return "data"
        else:
            return "text"
    
    def _load_documents(self, source: KnowledgeSource) -> List[Dict[str, Any]]:
        """Load documents from a knowledge source."""
        documents = []
        
        try:
            if source.source_type == SourceType.FILE:
                doc = self._load_single_file(source.path)
                if doc:
                    documents.append(doc)
                    
            elif source.source_type == SourceType.FOLDER:
                documents = self._load_directory(source.path)
                
            elif source.source_type == SourceType.GITHUB:
                documents = self._load_github_repo(source.path)

            elif source.source_type == SourceType.GOOGLE_DRIVE:
                documents = self._load_google_drive(source.path)

            elif source.source_type == SourceType.URL:
                documents = self._load_url(source.path, source.config)

            else:
                logger.warning(f"Unsupported source type: {source.source_type}")
                
        except Exception as e:
            logger.error(f"Failed to load documents from {source.path}: {e}")
            
        return documents
    
    def _load_single_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Load a single file."""
        try:
            path = Path(file_path)
            if not path.exists():
                logger.warning(f"File not found: {file_path}")
                return None
            
            # Choose loader based on file extension
            loader = None
            if path.suffix.lower() == '.pdf':
                loader = PyPDFLoader(file_path)
            elif path.suffix.lower() in ['.docx', '.doc']:
                loader = Docx2txtLoader(file_path)
            else:
                loader = TextLoader(file_path, encoding='utf-8')
            
            docs = loader.load()
            if docs:
                return {
                    "content": docs[0].page_content,
                    "metadata": {
                        "source": file_path,
                        "filename": path.name,
                        "file_type": path.suffix.lower(),
                        "file_size": path.stat().st_size
                    }
                }
                
        except Exception as e:
            logger.error(f"Failed to load file {file_path}: {e}")
            
        return None
    
    def _load_directory(self, dir_path: str) -> List[Dict[str, Any]]:
        """Load all supported files from a directory."""
        documents = []
        
        try:
            path = Path(dir_path)
            if not path.exists():
                logger.warning(f"Directory not found: {dir_path}")
                return documents
            
            # Supported file extensions (expanded)
            supported_extensions = [
                '.txt', '.md', '.pdf', '.docx', '.doc', '.rtf',
                '.py', '.js', '.html', '.css', '.json', '.xml',
                '.csv', '.tsv', '.rst', '.tex', '.log',
                '.cpp', '.c', '.h', '.java', '.php', '.rb',
                '.go', '.rs', '.swift', '.kt', '.scala',
                '.yml', '.yaml', '.toml', '.ini', '.cfg'
            ]
            
            for file_path in path.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                    doc = self._load_single_file(str(file_path))
                    if doc:
                        documents.append(doc)
                        
        except Exception as e:
            logger.error(f"Failed to load directory {dir_path}: {e}")
            
        return documents
    
    def _load_github_repo(self, repo_url: str) -> List[Dict[str, Any]]:
        """Load files from a GitHub repository."""
        documents = []
        
        try:
            # Create temporary directory for cloning
            temp_dir = self.config_service.get_app_directory() / "temp" / "github_repos"
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate unique directory name based on repo URL
            repo_hash = hashlib.md5(repo_url.encode()).hexdigest()[:8]
            clone_dir = temp_dir / f"repo_{repo_hash}"
            
            # Use GitLoader from langchain
            loader = GitLoader(
                clone_url=repo_url,
                repo_path=str(clone_dir),
                branch="main"  # or "master"
            )
            
            docs = loader.load()
            for doc in docs:
                documents.append({
                    "content": doc.page_content,
                    "metadata": {
                        "source": repo_url,
                        "filename": doc.metadata.get("file_name", "unknown"),
                        "file_path": doc.metadata.get("file_path", ""),
                        "file_type": Path(doc.metadata.get("file_name", "")).suffix.lower()
                    }
                })
                
        except Exception as e:
            logger.error(f"Failed to load GitHub repo {repo_url}: {e}")

        return documents

    def _load_google_drive(self, folder_url: str) -> List[Dict[str, Any]]:
        """Load files from a Google Drive folder."""
        try:
            if not self.google_drive_service.is_authenticated():
                logger.warning("Google Drive not authenticated")
                return []

            documents = self.google_drive_service.process_folder(folder_url)
            logger.info(f"Loaded {len(documents)} documents from Google Drive")
            return documents

        except Exception as e:
            logger.error(f"Failed to load Google Drive folder {folder_url}: {e}")
            return []

    def _load_url(self, url: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Load content from a URL or website."""
        try:
            if not self.web_scraping_service.is_available():
                logger.warning("Web scraping not available")
                return []

            # Check configuration for crawling options
            crawl_mode = config.get("crawl_mode", "single")
            max_pages = config.get("max_pages", 10)
            same_domain = config.get("same_domain_only", True)

            documents = []

            if crawl_mode == "single":
                # Extract content from single URL
                content = self.web_scraping_service.extract_content_from_url(url)
                if content:
                    documents.append(content)

            elif crawl_mode == "crawl":
                # Crawl website starting from URL
                documents = self.web_scraping_service.crawl_website(
                    url, max_pages=max_pages, same_domain_only=same_domain
                )

            elif crawl_mode == "sitemap":
                # Extract from sitemap
                documents = self.web_scraping_service.extract_from_sitemap(
                    url, max_urls=max_pages
                )

            logger.info(f"Loaded {len(documents)} documents from URL: {url}")
            return documents

        except Exception as e:
            logger.error(f"Failed to load URL {url}: {e}")
            return []
    
    def _store_chunks(self, chunks: List[Dict[str, Any]], source_id: str):
        """Store text chunks in ChromaDB with batch processing."""
        try:
            if not chunks:
                return

            # Process in batches for better performance
            batch_size = 100
            total_chunks = len(chunks)

            for i in range(0, total_chunks, batch_size):
                batch = chunks[i:i + batch_size]

                # Prepare batch data
                texts = [chunk["content"] for chunk in batch]
                metadatas = [chunk["metadata"] for chunk in batch]
                ids = [f"{source_id}_{i + j}" for j in range(len(batch))]

                # Generate embeddings for batch
                embeddings = self.embedding_model.encode(texts, show_progress_bar=False).tolist()

                # Store batch in ChromaDB
                self.collection.add(
                    embeddings=embeddings,
                    documents=texts,
                    metadatas=metadatas,
                    ids=ids
                )

                logger.debug(f"Stored batch {i//batch_size + 1}/{(total_chunks + batch_size - 1)//batch_size}")

            logger.info(f"Stored {total_chunks} chunks in vector database")

        except Exception as e:
            logger.error(f"Failed to store chunks: {e}")
            raise
    
    def search_similar(self, query: str, n_results: int = 5,
                      content_type: Optional[str] = None,
                      source_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for similar content in the knowledge base with advanced filtering."""
        try:
            if not self._is_rag_available():
                logger.warning("RAG components not available")
                return []

            if not self.collection:
                logger.warning("Collection not initialized")
                return []

            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()[0]

            # Build where clause for filtering
            where_clause = {}
            if content_type:
                where_clause["chunk_type"] = content_type
            if source_filter:
                where_clause["source_id"] = source_filter

            # Search in ChromaDB
            search_kwargs = {
                "query_embeddings": [query_embedding],
                "n_results": min(n_results * 2, 20),  # Get more results for better ranking
                "include": ["documents", "metadatas", "distances"]
            }

            if where_clause:
                search_kwargs["where"] = where_clause

            results = self.collection.query(**search_kwargs)

            # Format and rank results
            formatted_results = []
            if results["documents"] and results["documents"][0]:
                for i in range(len(results["documents"][0])):
                    similarity = 1 - results["distances"][0][i]

                    # Apply additional ranking factors
                    score = self._calculate_relevance_score(
                        query,
                        results["documents"][0][i],
                        results["metadatas"][0][i],
                        similarity
                    )

                    formatted_results.append({
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "similarity": similarity,
                        "relevance_score": score
                    })

            # Sort by relevance score and return top results
            formatted_results.sort(key=lambda x: x["relevance_score"], reverse=True)
            final_results = formatted_results[:n_results]

            logger.debug(f"Found {len(final_results)} similar chunks (from {len(formatted_results)} candidates)")
            return final_results

        except Exception as e:
            logger.error(f"Failed to search similar content: {e}")
            return []

    def _calculate_relevance_score(self, query: str, content: str, metadata: Dict,
                                 base_similarity: float) -> float:
        """Calculate enhanced relevance score."""
        score = base_similarity

        # Boost score for exact keyword matches
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        keyword_overlap = len(query_words.intersection(content_words)) / len(query_words)
        score += keyword_overlap * 0.2

        # Boost score for recent content
        if "indexed_at" in metadata:
            # This would need proper date handling
            pass

        # Boost score based on content type relevance
        chunk_type = metadata.get("chunk_type", "text")
        if "code" in query.lower() and chunk_type == "code":
            score += 0.1
        elif "documentation" in query.lower() and chunk_type == "documentation":
            score += 0.1

        return min(score, 1.0)  # Cap at 1.0
    
    def remove_source(self, source_id: str) -> bool:
        """Remove all chunks from a specific source."""
        try:
            if not self.collection:
                return False
            
            # Get all IDs for this source
            results = self.collection.get(
                where={"source_id": source_id},
                include=["metadatas"]
            )
            
            if results["ids"]:
                self.collection.delete(ids=results["ids"])
                logger.info(f"Removed {len(results['ids'])} chunks for source {source_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove source {source_id}: {e}")
            return False
    
    def update_source(self, source: KnowledgeSource) -> bool:
        """Update an existing knowledge source by reprocessing it."""
        try:
            # Remove existing chunks
            if not self.remove_source(source.id):
                logger.warning(f"Failed to remove existing chunks for {source.id}")

            # Reprocess the source
            return self.process_knowledge_source(source)

        except Exception as e:
            logger.error(f"Failed to update source {source.id}: {e}")
            return False

    def reindex_all_sources(self, sources: List[KnowledgeSource]) -> Dict[str, bool]:
        """Reindex all knowledge sources."""
        results = {}

        try:
            # Clear the entire collection
            if self.collection:
                self.collection.delete()
                logger.info("Cleared existing collection for reindexing")

            # Recreate collection
            if self.chroma_client:
                self.collection = self.chroma_client.get_or_create_collection(
                    name="knowledge_base",
                    metadata={"description": "Main knowledge base collection"}
                )

            # Reprocess all sources
            for source in sources:
                try:
                    success = self.process_knowledge_source(source)
                    results[source.id] = success
                    logger.info(f"Reindexed {source.get_display_name()}: {'success' if success else 'failed'}")
                except Exception as e:
                    logger.error(f"Failed to reindex {source.get_display_name()}: {e}")
                    results[source.id] = False

            return results

        except Exception as e:
            logger.error(f"Failed to reindex sources: {e}")
            return {source.id: False for source in sources}

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get detailed statistics about the knowledge base collection."""
        try:
            if not self._is_rag_available():
                return {"error": "RAG components not available"}

            if not self.collection:
                return {"error": "Collection not initialized"}

            # Get basic count
            count = self.collection.count()

            # Get sample of metadata to analyze content types
            sample_results = self.collection.get(limit=min(count, 1000), include=["metadatas"])

            # Analyze content types
            content_types = {}
            source_counts = {}

            if sample_results["metadatas"]:
                for metadata in sample_results["metadatas"]:
                    chunk_type = metadata.get("chunk_type", "unknown")
                    source_id = metadata.get("source_id", "unknown")

                    content_types[chunk_type] = content_types.get(chunk_type, 0) + 1
                    source_counts[source_id] = source_counts.get(source_id, 0) + 1

            return {
                "total_chunks": count,
                "collection_name": self.collection.name,
                "content_types": content_types,
                "sources_count": len(source_counts),
                "embedding_model": self.config_service.settings.embedding_model,
                "chunk_size": self.config_service.settings.chunk_size,
                "chunk_overlap": self.config_service.settings.chunk_overlap
            }

        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {"error": str(e)}

    def optimize_collection(self) -> bool:
        """Optimize the collection for better performance."""
        try:
            if not self._is_rag_available():
                logger.warning("RAG components not available")
                return False

            # This would implement collection optimization
            # For now, just log that optimization was requested
            logger.info("Collection optimization requested (not yet implemented)")
            return True

        except Exception as e:
            logger.error(f"Failed to optimize collection: {e}")
            return False
