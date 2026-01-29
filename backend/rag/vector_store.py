"""
RAG (Retrieval-Augmented Generation) System using ChromaDB
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
from config import Config
import hashlib
from datetime import datetime


class VectorStore:
    """Vector database for RAG using ChromaDB"""
    
    def __init__(self, persist_dir: str = None, collection_name: str = "research_docs"):
        self.persist_dir = persist_dir or Config.CHROMA_PERSIST_DIR
        self.collection_name = collection_name
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(Config.EMBEDDING_MODEL)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Research documents and web content"}
        )
    
    def add_documents(self, documents: List[Dict]) -> int:
        """
        Add documents to the vector store
        
        Each document should have:
        - content: Text content
        - metadata: Dict with title, url, date, etc.
        
        Returns number of documents added
        """
        if not documents:
            return 0
        
        ids = []
        texts = []
        metadatas = []
        
        for doc in documents:
            content = doc.get('content', '')
            if not content or len(content.strip()) < 50:
                continue
            
            # Generate unique ID
            doc_id = self._generate_id(doc)
            
            # Prepare metadata
            metadata = doc.get('metadata', {})
            metadata['added_at'] = datetime.now().isoformat()
            
            ids.append(doc_id)
            texts.append(content)
            metadatas.append(metadata)
        
        if not ids:
            return 0
        
        # Chunk long documents
        chunked_ids, chunked_texts, chunked_metadatas = self._chunk_documents(
            ids, texts, metadatas
        )
        
        # Add to collection
        try:
            self.collection.add(
                ids=chunked_ids,
                documents=chunked_texts,
                metadatas=chunked_metadatas
            )
            return len(chunked_ids)
        except Exception as e:
            print(f"Error adding documents: {e}")
            return 0
    
    def search(self, query: str, n_results: int = 10, 
               filter_metadata: Dict = None) -> List[Dict]:
        """
        Search for relevant documents
        
        Returns list of results with content and metadata
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filter_metadata
            )
            
            # Format results
            formatted_results = []
            
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        'content': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 0,
                        'id': results['ids'][0][i] if results['ids'] else ''
                    })
            
            return formatted_results
            
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def search_by_topic(self, topic: str, n_results: int = 20) -> List[Dict]:
        """Search for documents relevant to a research topic"""
        return self.search(topic, n_results=n_results)
    
    def get_recent_documents(self, n_results: int = 10, days: int = 30) -> List[Dict]:
        """Get recently added documents"""
        try:
            # Calculate date threshold
            from datetime import timedelta
            threshold = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Query with date filter
            results = self.collection.query(
                query_texts=["recent research"],
                n_results=n_results,
                where={"added_at": {"$gte": threshold}}
            )
            
            return self._format_results(results)
            
        except Exception as e:
            print(f"Error getting recent documents: {e}")
            return []
    
    def delete_old_documents(self, days: int = 90) -> int:
        """Delete documents older than specified days"""
        try:
            from datetime import timedelta
            threshold = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Get old documents
            results = self.collection.get(
                where={"added_at": {"$lt": threshold}}
            )
            
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                return len(results['ids'])
            
            return 0
            
        except Exception as e:
            print(f"Error deleting old documents: {e}")
            return 0
    
    def clear_collection(self):
        """Clear all documents from collection"""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Research documents and web content"}
            )
        except Exception as e:
            print(f"Error clearing collection: {e}")
    
    def get_stats(self) -> Dict:
        """Get collection statistics"""
        try:
            count = self.collection.count()
            return {
                'total_documents': count,
                'collection_name': self.collection_name,
                'embedding_model': Config.EMBEDDING_MODEL
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}
    
    def _chunk_documents(self, ids: List[str], texts: List[str], 
                        metadatas: List[Dict]) -> tuple:
        """Chunk long documents into smaller pieces"""
        chunked_ids = []
        chunked_texts = []
        chunked_metadatas = []
        
        chunk_size = Config.CHUNK_SIZE
        chunk_overlap = Config.CHUNK_OVERLAP
        
        for doc_id, text, metadata in zip(ids, texts, metadatas):
            if len(text) <= chunk_size:
                chunked_ids.append(doc_id)
                chunked_texts.append(text)
                chunked_metadatas.append(metadata)
            else:
                # Split into chunks
                chunks = self._split_text(text, chunk_size, chunk_overlap)
                
                for i, chunk in enumerate(chunks):
                    chunk_id = f"{doc_id}_chunk_{i}"
                    chunk_metadata = metadata.copy()
                    chunk_metadata['chunk_index'] = i
                    chunk_metadata['total_chunks'] = len(chunks)
                    
                    chunked_ids.append(chunk_id)
                    chunked_texts.append(chunk)
                    chunked_metadatas.append(chunk_metadata)
        
        return chunked_ids, chunked_texts, chunked_metadatas
    
    def _split_text(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > chunk_size * 0.5:  # At least 50% of chunk
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1
            
            chunks.append(chunk.strip())
            start = end - overlap
        
        return chunks
    
    def _generate_id(self, doc: Dict) -> str:
        """Generate unique ID for document"""
        # Use URL if available, otherwise hash content
        url = doc.get('metadata', {}).get('url', '')
        if url:
            return hashlib.md5(url.encode()).hexdigest()
        
        content = doc.get('content', '')[:200]
        return hashlib.md5(content.encode()).hexdigest()
    
    def _format_results(self, results: Dict) -> List[Dict]:
        """Format ChromaDB results"""
        formatted = []
        
        if results.get('documents') and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                formatted.append({
                    'content': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results.get('distances') else 0,
                    'id': results['ids'][0][i] if results['ids'] else ''
                })
        
        return formatted
