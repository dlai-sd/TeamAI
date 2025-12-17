"""
WebCrawler Processor
Orchestrates web crawling using WebsiteConnector and parses HTML
Separation of concerns: WebsiteConnector (Data Source) → WebCrawler (Processor)
"""
import sys
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin, urlparse
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from components.base import BaseComponent
from components.connectors.website_connector import WebsiteConnector


class WebCrawler(BaseComponent):
    """Crawls websites and extracts SEO data (Processor layer)"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, mock_mode: bool = False):
        super().__init__(config, mock_mode)
        self.max_pages = self.config.get('max_pages', 10)
        self.respect_robots = self.config.get('respect_robots', True)
        self.rate_limit_delay = self.config.get('rate_limit_delay', 0.5)
        
        # Initialize WebsiteConnector (Data Source)
        connector_config = {
            'timeout': self.config.get('timeout', 30),
            'user_agent': self.config.get('user_agent', 'TeamAI-Bot/1.0'),
            'follow_redirects': True
        }
        self.connector = WebsiteConnector(connector_config, mock_mode=mock_mode)
    
    def validate_config(self) -> bool:
        """Validate crawler configuration"""
        if self.max_pages < 1:
            return False
        if self.rate_limit_delay < 0:
            return False
        return True
    
    async def execute(self, url: str, max_depth: int = 2) -> Dict[str, Any]:
        """
        Crawl website starting from URL
        
        Args:
            url: Starting URL
            max_depth: Maximum crawl depth
            
        Returns:
            Dict with pages data
        """
        if self.mock_mode:
            return self._mock_crawl(url)
        
        if not self.validate_config():
            raise ValueError("Invalid crawler configuration")
        
        visited = set()
        pages = []
        to_visit = [(url, 0)]  # (url, depth)
        
        while to_visit and len(pages) < self.max_pages:
            current_url, depth = to_visit.pop(0)
            
            if current_url in visited or depth > max_depth:
                continue
            
            try:
                # Use WebsiteConnector to fetch HTML (Data Source layer)
                fetch_result = await self.connector.execute(current_url)
                
                # Check for errors
                if fetch_result.get('error') or not fetch_result.get('html'):
                    print(f"Error fetching {current_url}: {fetch_result.get('error', 'No HTML')}")
                    continue
                
                visited.add(current_url)
                
                # Parse HTML (Processor layer responsibility)
                soup = BeautifulSoup(fetch_result['html'], 'lxml')
                
                # Extract structured data
                page_data = {
                    'url': current_url,
                    'status_code': fetch_result['status_code'],
                    'title': soup.title.string if soup.title else '',
                    'meta_description': self._extract_meta(soup, 'description'),
                    'meta_keywords': self._extract_meta(soup, 'keywords'),
                    'h1_tags': [h1.get_text(strip=True) for h1 in soup.find_all('h1')],
                    'h2_tags': [h2.get_text(strip=True) for h2 in soup.find_all('h2')],
                    'word_count': len(soup.get_text().split()),
                    'links': self._extract_links(soup, current_url),
                    'images': len(soup.find_all('img')),
                    'depth': depth,
                    'elapsed_ms': fetch_result.get('elapsed_ms', 0)
                }
                
                pages.append(page_data)
                
                # Add internal links to queue (only if we haven't reached max depth)
                if depth < max_depth:
                    base_domain = urlparse(current_url).netloc
                    for link in page_data['links']:
                        if urlparse(link).netloc == base_domain:
                            to_visit.append((link, depth + 1))
                
                # Rate limiting
                await self._async_sleep(self.rate_limit_delay)
            
            except Exception as e:
                print(f"Error processing {current_url}: {str(e)}")
                continue
        
        return {
            'pages': pages,
            'total_pages': len(pages),
            'visited_urls': list(visited),
            'base_url': url
        }
    
    def _extract_meta(self, soup: BeautifulSoup, name: str) -> str:
        """Extract meta tag content"""
        tag = soup.find('meta', attrs={'name': name}) or soup.find('meta', attrs={'property': f'og:{name}'})
        return tag.get('content', '') if tag else ''
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract all links from page"""
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Convert relative URLs to absolute
            absolute_url = urljoin(base_url, href)
            if absolute_url.startswith('http'):
                links.append(absolute_url)
        return links
    
    async def _async_sleep(self, seconds: float):
        """Async sleep helper"""
        import asyncio
        await asyncio.sleep(seconds)
    
    def _mock_crawl(self, url: str) -> Dict[str, Any]:
        """Return mock data for testing"""
        return {
            'pages': [
                {
                    'url': url,
                    'status_code': 200,
                    'title': 'Example Domain - SEO Test',
                    'meta_description': 'This is a test page for SEO analysis',
                    'meta_keywords': 'test, seo, example',
                    'h1_tags': ['Welcome to Example Domain'],
                    'h2_tags': ['About Us', 'Our Services'],
                    'word_count': 250,
                    'links': [f'{url}/page1', f'{url}/page2'],
                    'images': 5,
                    'depth': 0
                },
                {
                    'url': f'{url}/page1',
                    'status_code': 200,
                    'title': 'Page 1 - Example Domain',
                    'meta_description': 'First subpage',
                    'meta_keywords': '',
                    'h1_tags': ['Page 1'],
                    'h2_tags': ['Section 1', 'Section 2'],
                    'word_count': 180,
                    'links': [url],
                    'images': 3,
                    'depth': 1
                }
            ],
            'total_pages': 2,
            'visited_urls': [url, f'{url}/page1'],
            'base_url': url
        }
