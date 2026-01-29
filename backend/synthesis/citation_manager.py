"""
Citation Manager for IEEE Format
"""
from typing import List, Dict, Optional
from datetime import datetime
import re


class CitationManager:
    """Manage citations and bibliography in IEEE format"""
    
    def __init__(self):
        self.citations = []
        self.citation_map = {}  # URL -> citation number
    
    def add_citation(self, source: Dict) -> int:
        """
        Add a citation and return its number
        
        Source should contain:
        - url: Source URL
        - title: Document title
        - authors: List of authors (optional)
        - date: Publication date (optional)
        - publisher: Publisher/website name (optional)
        """
        url = source.get('url', '')
        
        # Check if already cited
        if url and url in self.citation_map:
            return self.citation_map[url]
        
        # Add new citation
        citation_num = len(self.citations) + 1
        self.citations.append(source)
        
        if url:
            self.citation_map[url] = citation_num
        
        return citation_num
    
    def format_citation(self, source: Dict, citation_num: int) -> str:
        """Format a single citation in IEEE style"""
        
        # Extract information
        authors = source.get('authors', [])
        title = source.get('title', 'Untitled')
        url = source.get('url', '')
        date = source.get('date', source.get('published_date', ''))
        publisher = source.get('publisher', source.get('source', ''))
        
        # Format authors
        if authors:
            if isinstance(authors, list):
                if len(authors) == 1:
                    author_str = self._format_author_name(authors[0])
                elif len(authors) == 2:
                    author_str = f"{self._format_author_name(authors[0])} and {self._format_author_name(authors[1])}"
                else:
                    author_str = f"{self._format_author_name(authors[0])} et al."
            else:
                author_str = str(authors)
        else:
            author_str = "Anonymous"
        
        # Format date
        date_str = self._format_date(date)
        
        # Build citation
        citation_parts = [f"[{citation_num}]", author_str]
        
        # Add title in quotes
        citation_parts.append(f'"{title},"')
        
        # Add publisher/website
        if publisher:
            citation_parts.append(f"{publisher},")
        
        # Add date
        if date_str:
            citation_parts.append(f"{date_str}.")
        
        # Add URL
        if url:
            citation_parts.append(f"[Online]. Available: {url}")
        
        return ' '.join(citation_parts)
    
    def generate_bibliography(self) -> str:
        """Generate complete bibliography in IEEE format"""
        if not self.citations:
            return ""
        
        bib_lines = ["REFERENCES\n"]
        
        for i, citation in enumerate(self.citations, 1):
            formatted = self.format_citation(citation, i)
            bib_lines.append(formatted)
        
        return '\n'.join(bib_lines)
    
    def get_inline_citation(self, url: str) -> str:
        """Get inline citation marker [X] for a URL"""
        if url in self.citation_map:
            return f"[{self.citation_map[url]}]"
        return ""
    
    def insert_citations(self, text: str, sources: List[Dict]) -> str:
        """
        Insert citation markers into text
        
        Looks for source references and replaces with [X] markers
        """
        modified_text = text
        
        for source in sources:
            citation_num = self.add_citation(source)
            
            # Look for references to this source in text
            title = source.get('title', '')
            if title and len(title) > 10:
                # Replace title mentions with citation
                pattern = re.escape(title[:50])  # Use first 50 chars
                modified_text = re.sub(
                    f"({pattern}[^\\[]*)",
                    f"\\1 [{citation_num}]",
                    modified_text,
                    count=1
                )
        
        return modified_text
    
    def _format_author_name(self, name: str) -> str:
        """Format author name as 'F. Lastname'"""
        if not name:
            return "Anonymous"
        
        parts = name.strip().split()
        
        if len(parts) == 1:
            return parts[0]
        elif len(parts) == 2:
            # First Last -> F. Last
            return f"{parts[0][0]}. {parts[1]}"
        else:
            # First Middle Last -> F. M. Last
            initials = ' '.join([p[0] + '.' for p in parts[:-1]])
            return f"{initials} {parts[-1]}"
    
    def _format_date(self, date_str: str) -> str:
        """Format date for citation"""
        if not date_str:
            return ""
        
        try:
            # Try to parse ISO format
            if 'T' in date_str:
                date_str = date_str.split('T')[0]
            
            # Parse date
            date_obj = datetime.fromisoformat(date_str.replace('Z', ''))
            
            # Format as "Month Year"
            return date_obj.strftime("%b. %Y")
            
        except Exception:
            # Return as-is if parsing fails
            return date_str
    
    def get_citation_count(self) -> int:
        """Get total number of citations"""
        return len(self.citations)
    
    def clear(self):
        """Clear all citations"""
        self.citations = []
        self.citation_map = {}
    
    def export_citations(self) -> List[Dict]:
        """Export all citations as list"""
        return self.citations.copy()
    
    def import_citations(self, citations: List[Dict]):
        """Import citations from list"""
        self.clear()
        for citation in citations:
            self.add_citation(citation)
