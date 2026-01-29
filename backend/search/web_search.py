"""
Web Search Integration using Tavily API
"""
import requests
from typing import List, Dict, Optional
from datetime import datetime
from tavily import TavilyClient
from config import Config
import time


class WebSearcher:
    """Web search using Tavily API"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or Config.TAVILY_API_KEY
        if not self.api_key:
            raise ValueError("Tavily API key not provided")
        
        self.client = TavilyClient(api_key=self.api_key)
        self.max_results = Config.MAX_SEARCH_RESULTS
    
    def search(self, query: str, max_results: int = None) -> List[Dict]:
        """
        Perform web search for a query
        
        Returns list of results with:
        - title: Page title
        - url: Page URL
        - content: Extracted content
        - score: Relevance score
        - published_date: Publication date if available
        """
        max_results = max_results or self.max_results
        
        try:
            response = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results,
                include_domains=[],
                exclude_domains=[],
                include_answer=True,
                include_raw_content=False
            )
            
            results = []
            for item in response.get('results', []):
                results.append({
                    'title': item.get('title', 'Untitled'),
                    'url': item.get('url', ''),
                    'content': item.get('content', ''),
                    'score': item.get('score', 0.5),
                    'published_date': self._extract_date(item),
                    'raw_content': item.get('raw_content', ''),
                })
            
            # Add answer summary if available
            if response.get('answer'):
                results.insert(0, {
                    'title': 'AI Summary',
                    'url': '',
                    'content': response['answer'],
                    'score': 1.0,
                    'published_date': datetime.now().isoformat(),
                    'is_summary': True
                })
            
            return results
            
        except Exception as e:
            print(f"Search error for query '{query}': {e}")
            return []
    
    def multi_search(self, queries: List[str], delay: float = 0.5) -> Dict[str, List[Dict]]:
        """
        Perform multiple searches with rate limiting
        
        Returns dict mapping query -> results
        """
        all_results = {}
        
        for query in queries:
            results = self.search(query)
            all_results[query] = results
            
            # Rate limiting
            if delay > 0:
                time.sleep(delay)
        
        return all_results
    
    def aggregate_results(self, multi_results: Dict[str, List[Dict]]) -> List[Dict]:
        """
        Aggregate and deduplicate results from multiple queries
        
        Returns sorted list of unique results
        """
        seen_urls = set()
        aggregated = []
        
        # Flatten all results
        for query, results in multi_results.items():
            for result in results:
                url = result.get('url', '')
                
                # Skip duplicates and summaries
                if url and url not in seen_urls and not result.get('is_summary'):
                    seen_urls.add(url)
                    result['source_query'] = query
                    aggregated.append(result)
        
        # Sort by relevance score
        aggregated.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return aggregated
    
    def extract_content(self, url: str) -> Optional[str]:
        """Extract content from a URL"""
        try:
            # Use Tavily's extract endpoint if available
            # Otherwise fall back to basic extraction
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.decompose()
                
                # Get text
                text = soup.get_text(separator='\n', strip=True)
                
                # Clean up whitespace
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                return '\n'.join(lines)
            
            return None
            
        except Exception as e:
            print(f"Error extracting content from {url}: {e}")
            return None
    
    def score_credibility(self, result: Dict) -> float:
        """
        Score source credibility based on various factors
        
        Returns score 0.0 to 1.0
        """
        score = 0.5  # Base score
        
        url = result.get('url', '').lower()
        title = result.get('title', '').lower()
        
        # Academic and authoritative domains
        authoritative_domains = [
            '.edu', '.gov', '.org',
            'scholar.google', 'arxiv.org', 'pubmed',
            'ieee.org', 'acm.org', 'springer',
            'nature.com', 'science.org', 'sciencedirect'
        ]
        
        for domain in authoritative_domains:
            if domain in url:
                score += 0.3
                break
        
        # News and reputable sources
        reputable_sources = [
            'bbc.', 'reuters.', 'apnews.', 'npr.org',
            'economist.', 'scientificamerican.', 'newscientist.'
        ]
        
        for source in reputable_sources:
            if source in url:
                score += 0.2
                break
        
        # Penalize certain domains
        low_credibility = ['pinterest.', 'quora.', 'reddit.', 'facebook.', 'twitter.']
        for domain in low_credibility:
            if domain in url:
                score -= 0.2
                break
        
        # Boost for research-related keywords
        research_keywords = ['research', 'study', 'analysis', 'journal', 'paper']
        for keyword in research_keywords:
            if keyword in title:
                score += 0.1
                break
        
        return max(0.0, min(1.0, score))
    
    def _extract_date(self, item: Dict) -> str:
        """Extract publication date from search result"""
        # Try various date fields
        date_fields = ['published_date', 'date', 'published', 'timestamp']
        
        for field in date_fields:
            if field in item and item[field]:
                return item[field]
        
        # Default to current date
        return datetime.now().isoformat()
    
    def get_recent_news(self, topic: str, days: int = 30) -> List[Dict]:
        """Get recent news articles about a topic"""
        try:
            response = self.client.search(
                query=f"{topic} news",
                search_depth="advanced",
                max_results=5,
                days=days
            )
            
            return response.get('results', [])
            
        except Exception as e:
            print(f"Error fetching recent news: {e}")
            return []
