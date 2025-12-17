"""
WebsiteConnector - Data Source Layer
Handles raw HTTP requests to websites (Data Source in architecture)
"""
import httpx
from typing import Dict, Any, Optional
from pathlib import Path
import sys

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from components.base import BaseComponent


class WebsiteConnector(BaseComponent):
    """
    Connector for fetching raw HTML from websites
    This is a Data Source - it only fetches, doesn't process
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, mock_mode: bool = False):
        super().__init__(config, mock_mode)
        self.timeout = self.config.get('timeout', 30)
        self.user_agent = self.config.get('user_agent', 'TeamAI-Bot/1.0')
        self.follow_redirects = self.config.get('follow_redirects', True)
        self.max_retries = self.config.get('max_retries', 3)
    
    def validate_config(self) -> bool:
        """Validate connector configuration"""
        if self.timeout < 1:
            return False
        if self.max_retries < 0:
            return False
        return True
    
    async def execute(self, url: str) -> Dict[str, Any]:
        """
        Fetch raw HTML content from URL
        
        Args:
            url: Target URL to fetch
            
        Returns:
            Dict with raw HTML and metadata
        """
        if self.mock_mode:
            return self._mock_fetch(url)
        
        if not self.validate_config():
            raise ValueError("Invalid connector configuration")
        
        async with httpx.AsyncClient(
            timeout=self.timeout,
            headers={'User-Agent': self.user_agent},
            follow_redirects=self.follow_redirects
        ) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                
                return {
                    'url': str(response.url),  # Final URL after redirects
                    'status_code': response.status_code,
                    'html': response.text,
                    'headers': dict(response.headers),
                    'encoding': response.encoding,
                    'elapsed_ms': int(response.elapsed.total_seconds() * 1000)
                }
            except httpx.HTTPStatusError as e:
                return {
                    'url': url,
                    'status_code': e.response.status_code,
                    'error': f'HTTP {e.response.status_code}',
                    'html': None
                }
            except Exception as e:
                return {
                    'url': url,
                    'status_code': 0,
                    'error': str(e),
                    'html': None
                }
    
    def _mock_fetch(self, url: str) -> Dict[str, Any]:
        """Return mock HTML for testing"""
        return {
            'url': url,
            'status_code': 200,
            'html': '''
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Example Domain - SEO Test</title>
                    <meta name="description" content="This is a test page for SEO analysis">
                    <meta name="keywords" content="test, seo, example">
                </head>
                <body>
                    <h1>Welcome to Example Domain</h1>
                    <h2>About Us</h2>
                    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
                    <h2>Our Services</h2>
                    <p>We provide excellent services for your business needs.</p>
                    <a href="/page1">Page 1</a>
                    <a href="/page2">Page 2</a>
                    <img src="/logo.png" alt="Logo">
                    <img src="/banner.jpg" alt="Banner">
                </body>
                </html>
            ''',
            'headers': {
                'content-type': 'text/html; charset=utf-8',
                'server': 'MockServer/1.0'
            },
            'encoding': 'utf-8',
            'elapsed_ms': 150
        }
