"""
Research Engine - Orchestrates the entire research pipeline
"""
from typing import List, Dict, Optional, Callable
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

from backend.llm import OllamaClient
from backend.search import WebSearcher
from backend.rag import VectorStore
from backend.agents import DataSourceAggregator
from backend.synthesis.citation_manager import CitationManager
from config import Config


class ResearchEngine:
    """Main research orchestration engine"""
    
    def __init__(self, tavily_api_key: str = None, news_api_key: str = None):
        # Initialize components
        self.llm = OllamaClient()
        self.searcher = WebSearcher(api_key=tavily_api_key)
        self.vector_store = VectorStore()
        self.data_aggregator = DataSourceAggregator(news_api_key=news_api_key)
        self.citation_manager = CitationManager()
        
        # Configuration
        self.max_queries = Config.MAX_QUERIES
        self.research_depth = Config.RESEARCH_DEPTH
        
        # Progress tracking
        self.progress_callback = None
        self.current_progress = 0
    
    def set_progress_callback(self, callback: Callable[[int, str], None]):
        """Set callback for progress updates"""
        self.progress_callback = callback
    
    def _update_progress(self, progress: int, message: str):
        """Update progress"""
        self.current_progress = progress
        if self.progress_callback:
            self.progress_callback(progress, message)
        print(f"[{progress}%] {message}")
    
    def conduct_research(self, topic: str, depth: str = "standard") -> Dict:
        """
        Conduct complete research on a topic
        
        Returns:
            Dict with:
            - topic: Research topic
            - queries: Generated queries
            - sources: All sources found
            - synthesis: Synthesized report
            - citations: Citation list
            - metadata: Research metadata
        """
        self._update_progress(0, "Starting research...")
        
        # Step 1: Generate initial queries
        self._update_progress(10, "Generating search queries...")
        queries = self.llm.generate_queries(topic, num_queries=self.max_queries)
        
        # Step 2: Web search
        self._update_progress(20, "Performing web searches...")
        search_results = self.searcher.multi_search(queries)
        aggregated_results = self.searcher.aggregate_results(search_results)
        
        # Step 3: Fetch real-time data
        self._update_progress(35, "Fetching real-time data from academic sources...")
        realtime_data = self.data_aggregator.fetch_all(topic)
        realtime_results = self.data_aggregator.aggregate_results(realtime_data)
        
        # Step 4: Combine and score sources
        self._update_progress(45, "Analyzing and scoring sources...")
        all_sources = self._combine_sources(aggregated_results, realtime_results)
        scored_sources = self._score_and_rank_sources(all_sources, topic)
        
        # Step 5: Store in RAG for context
        self._update_progress(55, "Indexing content for retrieval...")
        self._index_sources(scored_sources)
        
        # Step 6: Analyze content with LLM
        self._update_progress(65, "Analyzing content relevance...")
        analyzed_sources = self._analyze_sources(topic, scored_sources[:20])
        
        # Step 7: Retrieve relevant context from RAG
        self._update_progress(70, "Retrieving relevant context...")
        rag_context = self.vector_store.search_by_topic(topic, n_results=15)
        
        # Step 8: Synthesize research
        self._update_progress(75, "Synthesizing research findings...")
        synthesis = self._synthesize_research(topic, analyzed_sources, rag_context)
        
        # Step 9: Add citations
        self._update_progress(85, "Formatting citations...")
        cited_synthesis = self._add_citations(synthesis, analyzed_sources)
        
        # Step 10: Generate bibliography
        self._update_progress(90, "Generating bibliography...")
        bibliography = self.citation_manager.generate_bibliography()
        
        # Complete
        self._update_progress(100, "Research complete!")
        
        return {
            'topic': topic,
            'queries': queries,
            'sources': analyzed_sources,
            'synthesis': cited_synthesis,
            'bibliography': bibliography,
            'citations': self.citation_manager.export_citations(),
            'metadata': {
                'total_sources': len(all_sources),
                'analyzed_sources': len(analyzed_sources),
                'timestamp': datetime.now().isoformat(),
                'depth': depth
            }
        }
    
    def _combine_sources(self, web_results: List[Dict], 
                        realtime_results: List[Dict]) -> List[Dict]:
        """Combine sources from different channels"""
        all_sources = []
        
        # Add web search results
        for result in web_results:
            result['channel'] = 'web_search'
            all_sources.append(result)
        
        # Add real-time data
        for result in realtime_results:
            result['channel'] = 'realtime'
            all_sources.append(result)
        
        return all_sources
    
    def _score_and_rank_sources(self, sources: List[Dict], topic: str) -> List[Dict]:
        """Score and rank sources by relevance and credibility"""
        for source in sources:
            # Base score from search
            base_score = source.get('score', 0.5)
            
            # Credibility score
            credibility = self.searcher.score_credibility(source)
            
            # Recency score (prefer recent content)
            recency = self._calculate_recency_score(source.get('published_date', ''))
            
            # Channel bonus
            channel_bonus = 0.1 if source.get('channel') == 'realtime' else 0
            
            # Combined score
            final_score = (base_score * 0.4 + 
                          credibility * 0.4 + 
                          recency * 0.1 + 
                          channel_bonus)
            
            source['final_score'] = final_score
        
        # Sort by final score
        sources.sort(key=lambda x: x.get('final_score', 0), reverse=True)
        
        return sources
    
    def _calculate_recency_score(self, date_str: str) -> float:
        """Calculate recency score (1.0 = very recent, 0.0 = old)"""
        if not date_str:
            return 0.3  # Default for unknown dates
        
        try:
            if 'T' in date_str:
                date_str = date_str.split('T')[0]
            
            pub_date = datetime.fromisoformat(date_str.replace('Z', ''))
            days_old = (datetime.now() - pub_date).days
            
            # Score decreases with age
            if days_old < 30:
                return 1.0
            elif days_old < 90:
                return 0.8
            elif days_old < 180:
                return 0.6
            elif days_old < 365:
                return 0.4
            else:
                return 0.2
                
        except Exception:
            return 0.3
    
    def _index_sources(self, sources: List[Dict]):
        """Index sources in vector store"""
        documents = []
        
        for source in sources:
            documents.append({
                'content': source.get('content', ''),
                'metadata': {
                    'title': source.get('title', ''),
                    'url': source.get('url', ''),
                    'source': source.get('source', ''),
                    'date': source.get('published_date', ''),
                    'score': source.get('final_score', 0)
                }
            })
        
        self.vector_store.add_documents(documents)
    
    def _analyze_sources(self, topic: str, sources: List[Dict]) -> List[Dict]:
        """Analyze sources with LLM"""
        analyzed = []
        
        for source in sources:
            content = source.get('content', '')
            if not content or len(content) < 100:
                continue
            
            # Analyze with LLM
            analysis = self.llm.analyze_content(topic, content)
            
            source['analysis'] = analysis.get('summary', '')
            source['relevance'] = analysis.get('relevance_score', 0.5)
            
            analyzed.append(source)
        
        return analyzed
    
    def _synthesize_research(self, topic: str, sources: List[Dict], 
                           rag_context: List[Dict]) -> str:
        """Synthesize research into coherent report"""
        # Prepare information for synthesis
        information = sources + [
            {
                'title': 'Context',
                'content': ctx.get('content', ''),
                'metadata': ctx.get('metadata', {})
            }
            for ctx in rag_context
        ]
        
        # Generate synthesis
        synthesis = self.llm.synthesize_research(topic, information)
        
        return synthesis
    
    def _add_citations(self, text: str, sources: List[Dict]) -> str:
        """Add citations to synthesized text"""
        # Add citations for each source
        for source in sources:
            citation_info = {
                'url': source.get('url', ''),
                'title': source.get('title', ''),
                'authors': source.get('authors', []),
                'date': source.get('published_date', ''),
                'publisher': source.get('source', '')
            }
            
            self.citation_manager.add_citation(citation_info)
        
        # Insert citation markers
        cited_text = self.citation_manager.insert_citations(text, sources)
        
        return cited_text
    
    def quick_research(self, topic: str) -> Dict:
        """Quick research with fewer sources"""
        original_max = self.max_queries
        self.max_queries = 3
        
        result = self.conduct_research(topic, depth="quick")
        
        self.max_queries = original_max
        return result
    
    def deep_research(self, topic: str) -> Dict:
        """Deep research with more sources and refinement"""
        original_max = self.max_queries
        self.max_queries = 8
        
        result = self.conduct_research(topic, depth="deep")
        
        self.max_queries = original_max
        return result
