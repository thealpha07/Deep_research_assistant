"""
Real-time Data Fetching Agents
"""
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET


class RealtimeAgent:
    """Base class for real-time data agents"""
    
    def fetch(self, topic: str) -> List[Dict]:
        """Fetch data for topic"""
        raise NotImplementedError


class ArxivAgent(RealtimeAgent):
    """Fetch recent papers from arXiv"""
    
    def __init__(self):
        self.base_url = "http://export.arxiv.org/api/query"
    
    def fetch(self, topic: str, max_results: int = 5) -> List[Dict]:
        """Fetch recent arXiv papers"""
        try:
            params = {
                'search_query': f'all:{topic}',
                'start': 0,
                'max_results': max_results,
                'sortBy': 'submittedDate',
                'sortOrder': 'descending'
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                return self._parse_arxiv_response(response.text)
            
            return []
            
        except Exception as e:
            print(f"ArXiv fetch error: {e}")
            return []
    
    def _parse_arxiv_response(self, xml_text: str) -> List[Dict]:
        """Parse arXiv API XML response"""
        results = []
        
        try:
            root = ET.fromstring(xml_text)
            namespace = {'atom': 'http://www.w3.org/2005/Atom'}
            
            for entry in root.findall('atom:entry', namespace):
                title = entry.find('atom:title', namespace)
                summary = entry.find('atom:summary', namespace)
                published = entry.find('atom:published', namespace)
                link = entry.find('atom:id', namespace)
                
                authors = []
                for author in entry.findall('atom:author', namespace):
                    name = author.find('atom:name', namespace)
                    if name is not None:
                        authors.append(name.text)
                
                results.append({
                    'title': title.text.strip() if title is not None else 'Untitled',
                    'content': summary.text.strip() if summary is not None else '',
                    'url': link.text if link is not None else '',
                    'published_date': published.text if published is not None else '',
                    'authors': authors,
                    'source': 'arXiv',
                    'type': 'academic_paper'
                })
        
        except Exception as e:
            print(f"Error parsing arXiv response: {e}")
        
        return results


class NewsAgent(RealtimeAgent):
    """Fetch recent news articles"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        # Using NewsAPI as example - can be replaced with other news APIs
        self.base_url = "https://newsapi.org/v2/everything"
    
    def fetch(self, topic: str, days: int = 7, max_results: int = 5) -> List[Dict]:
        """Fetch recent news articles"""
        if not self.api_key:
            print("NewsAPI key not configured, skipping news fetch")
            return []
        
        try:
            from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            params = {
                'q': topic,
                'from': from_date,
                'sortBy': 'publishedAt',
                'language': 'en',
                'pageSize': max_results,
                'apiKey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_news_response(data)
            
            return []
            
        except Exception as e:
            print(f"News fetch error: {e}")
            return []
    
    def _parse_news_response(self, data: Dict) -> List[Dict]:
        """Parse NewsAPI response"""
        results = []
        
        for article in data.get('articles', []):
            results.append({
                'title': article.get('title', 'Untitled'),
                'content': article.get('description', '') + '\n\n' + article.get('content', ''),
                'url': article.get('url', ''),
                'published_date': article.get('publishedAt', ''),
                'source': article.get('source', {}).get('name', 'Unknown'),
                'author': article.get('author', ''),
                'type': 'news_article'
            })
        
        return results


class WikipediaAgent(RealtimeAgent):
    """Fetch Wikipedia content"""
    
    def __init__(self):
        self.base_url = "https://en.wikipedia.org/w/api.php"
    
    def fetch(self, topic: str, max_results: int = 3) -> List[Dict]:
        """Fetch Wikipedia articles"""
        try:
            # Search for relevant pages
            search_params = {
                'action': 'opensearch',
                'search': topic,
                'limit': max_results,
                'format': 'json'
            }
            
            response = requests.get(self.base_url, params=search_params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                titles = data[1] if len(data) > 1 else []
                urls = data[3] if len(data) > 3 else []
                
                results = []
                for title, url in zip(titles, urls):
                    content = self._fetch_page_content(title)
                    if content:
                        results.append({
                            'title': title,
                            'content': content,
                            'url': url,
                            'published_date': datetime.now().isoformat(),
                            'source': 'Wikipedia',
                            'type': 'encyclopedia'
                        })
                
                return results
            
            return []
            
        except Exception as e:
            print(f"Wikipedia fetch error: {e}")
            return []
    
    def _fetch_page_content(self, title: str) -> Optional[str]:
        """Fetch content of a Wikipedia page"""
        try:
            params = {
                'action': 'query',
                'prop': 'extracts',
                'exintro': True,
                'explaintext': True,
                'titles': title,
                'format': 'json'
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                pages = data.get('query', {}).get('pages', {})
                
                for page_id, page_data in pages.items():
                    return page_data.get('extract', '')
            
            return None
            
        except Exception as e:
            print(f"Error fetching Wikipedia page: {e}")
            return None


class DataSourceAggregator:
    """Aggregate data from multiple real-time sources"""
    
    def __init__(self, news_api_key: str = None):
        self.agents = {
            'arxiv': ArxivAgent(),
            'wikipedia': WikipediaAgent(),
        }
        
        if news_api_key:
            self.agents['news'] = NewsAgent(news_api_key)
    
    def fetch_all(self, topic: str, sources: List[str] = None) -> Dict[str, List[Dict]]:
        """
        Fetch from all or specified sources
        
        Args:
            topic: Research topic
            sources: List of source names to use (None = all)
        
        Returns:
            Dict mapping source name to results
        """
        if sources is None:
            sources = list(self.agents.keys())
        
        results = {}
        
        for source in sources:
            if source in self.agents:
                print(f"Fetching from {source}...")
                results[source] = self.agents[source].fetch(topic)
            else:
                print(f"Unknown source: {source}")
        
        return results
    
    def aggregate_results(self, multi_source_results: Dict[str, List[Dict]]) -> List[Dict]:
        """Aggregate results from multiple sources"""
        all_results = []
        
        for source, results in multi_source_results.items():
            for result in results:
                result['data_source'] = source
                all_results.append(result)
        
        # Sort by date (most recent first)
        all_results.sort(
            key=lambda x: x.get('published_date', ''),
            reverse=True
        )
        
        return all_results
    
    def get_academic_sources(self, topic: str) -> List[Dict]:
        """Get only academic sources"""
        return self.fetch_all(topic, sources=['arxiv'])
    
    def get_current_events(self, topic: str) -> List[Dict]:
        """Get current events and news"""
        sources = ['news'] if 'news' in self.agents else []
        if sources:
            return self.fetch_all(topic, sources=sources)
        return {}
