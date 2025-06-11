"""
Web Scraping Service

Handles web content extraction and processing for knowledge ingestion.
"""

import re
import time
from urllib.parse import urljoin, urlparse, parse_qs
from typing import List, Dict, Any, Optional, Set
from pathlib import Path
from loguru import logger

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    REQUESTS_AVAILABLE = True
except ImportError:
    logger.warning("requests library not available")
    REQUESTS_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    logger.warning("beautifulsoup4 not available")
    BEAUTIFULSOUP_AVAILABLE = False

try:
    import trafilatura
    TRAFILATURA_AVAILABLE = True
except ImportError:
    logger.warning("trafilatura not available")
    TRAFILATURA_AVAILABLE = False


class WebScrapingService:
    """Service for web content extraction."""
    
    def __init__(self):
        self.session = None
        self.user_agent = "Custom Gemini Agent GUI/1.0 (Educational/Research Purpose)"
        
        if REQUESTS_AVAILABLE:
            self._setup_session()
    
    def _setup_session(self):
        """Setup requests session with retry strategy."""
        self.session = requests.Session()
        
        # Setup retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set headers
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def is_available(self) -> bool:
        """Check if web scraping is available."""
        return REQUESTS_AVAILABLE and (BEAUTIFULSOUP_AVAILABLE or TRAFILATURA_AVAILABLE)
    
    def extract_content_from_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract content from a single URL."""
        if not self.is_available():
            logger.error("Web scraping dependencies not available")
            return None
        
        try:
            logger.info(f"Extracting content from: {url}")
            
            # Fetch the page
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Extract content using available method
            if TRAFILATURA_AVAILABLE:
                content = self._extract_with_trafilatura(response.text, url)
            elif BEAUTIFULSOUP_AVAILABLE:
                content = self._extract_with_beautifulsoup(response.text, url)
            else:
                logger.error("No content extraction method available")
                return None
            
            if content:
                return {
                    "content": content["text"],
                    "metadata": {
                        "source": url,
                        "title": content.get("title", ""),
                        "url": url,
                        "content_length": len(content["text"]),
                        "extraction_method": content.get("method", "unknown"),
                        "file_type": ".html"
                    }
                }
            
            return None
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch URL {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to extract content from {url}: {e}")
            return None
    
    def _extract_with_trafilatura(self, html: str, url: str) -> Optional[Dict[str, str]]:
        """Extract content using trafilatura."""
        try:
            # Extract main content
            text = trafilatura.extract(html, include_comments=False, include_tables=True)
            
            if not text:
                return None
            
            # Extract metadata
            metadata = trafilatura.extract_metadata(html)
            title = metadata.title if metadata else ""
            
            return {
                "text": text,
                "title": title,
                "method": "trafilatura"
            }
            
        except Exception as e:
            logger.error(f"Trafilatura extraction failed: {e}")
            return None
    
    def _extract_with_beautifulsoup(self, html: str, url: str) -> Optional[Dict[str, str]]:
        """Extract content using BeautifulSoup."""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract title
            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else ""
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                script.decompose()
            
            # Extract main content
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main|article'))
            
            if main_content:
                text = main_content.get_text()
            else:
                # Fallback to body
                body = soup.find('body')
                text = body.get_text() if body else soup.get_text()
            
            # Clean up text
            text = re.sub(r'\s+', ' ', text).strip()
            
            if len(text) < 100:  # Too short, probably not useful
                return None
            
            return {
                "text": text,
                "title": title,
                "method": "beautifulsoup"
            }
            
        except Exception as e:
            logger.error(f"BeautifulSoup extraction failed: {e}")
            return None
    
    def extract_links_from_page(self, url: str, same_domain_only: bool = True) -> List[str]:
        """Extract links from a webpage."""
        if not BEAUTIFULSOUP_AVAILABLE or not REQUESTS_AVAILABLE:
            logger.error("Dependencies not available for link extraction")
            return []
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            links = []
            
            base_domain = urlparse(url).netloc
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                # Convert relative URLs to absolute
                absolute_url = urljoin(url, href)
                
                # Filter by domain if requested
                if same_domain_only:
                    link_domain = urlparse(absolute_url).netloc
                    if link_domain != base_domain:
                        continue
                
                # Skip non-HTTP URLs
                if not absolute_url.startswith(('http://', 'https://')):
                    continue
                
                # Skip common non-content URLs
                if any(skip in absolute_url.lower() for skip in [
                    'javascript:', 'mailto:', '#', '.pdf', '.jpg', '.png', '.gif',
                    '.css', '.js', 'login', 'register', 'cart', 'checkout'
                ]):
                    continue
                
                links.append(absolute_url)
            
            # Remove duplicates while preserving order
            unique_links = list(dict.fromkeys(links))
            logger.info(f"Found {len(unique_links)} links on {url}")
            
            return unique_links
            
        except Exception as e:
            logger.error(f"Failed to extract links from {url}: {e}")
            return []
    
    def crawl_website(self, start_url: str, max_pages: int = 10, same_domain_only: bool = True) -> List[Dict[str, Any]]:
        """Crawl a website starting from a URL."""
        if not self.is_available():
            logger.error("Web scraping not available")
            return []
        
        documents = []
        visited_urls: Set[str] = set()
        urls_to_visit = [start_url]
        
        logger.info(f"Starting website crawl from: {start_url} (max {max_pages} pages)")
        
        while urls_to_visit and len(documents) < max_pages:
            current_url = urls_to_visit.pop(0)
            
            if current_url in visited_urls:
                continue
            
            visited_urls.add(current_url)
            
            # Extract content from current page
            content = self.extract_content_from_url(current_url)
            if content:
                documents.append(content)
                logger.info(f"Extracted content from: {current_url}")
            
            # Find more links if we haven't reached the limit
            if len(documents) < max_pages:
                try:
                    links = self.extract_links_from_page(current_url, same_domain_only)
                    
                    # Add new links to visit
                    for link in links:
                        if link not in visited_urls and link not in urls_to_visit:
                            urls_to_visit.append(link)
                    
                    # Rate limiting
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Failed to extract links from {current_url}: {e}")
        
        logger.info(f"Website crawl completed. Extracted {len(documents)} documents.")
        return documents
    
    def extract_from_sitemap(self, sitemap_url: str, max_urls: int = 50) -> List[Dict[str, Any]]:
        """Extract content from URLs listed in a sitemap."""
        if not self.is_available():
            logger.error("Web scraping not available")
            return []
        
        try:
            logger.info(f"Processing sitemap: {sitemap_url}")
            
            # Fetch sitemap
            response = self.session.get(sitemap_url, timeout=30)
            response.raise_for_status()
            
            # Parse sitemap XML
            soup = BeautifulSoup(response.text, 'xml')
            urls = []
            
            # Extract URLs from sitemap
            for loc in soup.find_all('loc'):
                url = loc.get_text().strip()
                if url.startswith(('http://', 'https://')):
                    urls.append(url)
            
            logger.info(f"Found {len(urls)} URLs in sitemap")
            
            # Limit URLs
            urls = urls[:max_urls]
            
            # Extract content from each URL
            documents = []
            for url in urls:
                try:
                    content = self.extract_content_from_url(url)
                    if content:
                        documents.append(content)
                    
                    # Rate limiting
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Failed to extract from {url}: {e}")
                    continue
            
            logger.info(f"Extracted {len(documents)} documents from sitemap")
            return documents
            
        except Exception as e:
            logger.error(f"Failed to process sitemap {sitemap_url}: {e}")
            return []
    
    def validate_url(self, url: str) -> bool:
        """Validate if a URL is accessible."""
        if not REQUESTS_AVAILABLE:
            return False
        
        try:
            response = self.session.head(url, timeout=10)
            return response.status_code == 200
        except:
            return False
