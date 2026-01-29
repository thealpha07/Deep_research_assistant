import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # LLM Configuration
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.2')
    
    # Search Configuration
    TAVILY_API_KEY = os.getenv('TAVILY_API_KEY', '')
    MAX_SEARCH_RESULTS = int(os.getenv('MAX_SEARCH_RESULTS', 10))
    
    # RAG Configuration
    CHROMA_PERSIST_DIR = os.getenv('CHROMA_PERSIST_DIR', './data/chromadb')
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
    CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', 1000))
    CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', 200))
    
    # Research Configuration
    MAX_QUERIES = int(os.getenv('MAX_QUERIES', 5))
    RESEARCH_DEPTH = os.getenv('RESEARCH_DEPTH', 'standard')  # quick, standard, deep
    
    # Export Configuration
    OUTPUT_DIR = os.getenv('OUTPUT_DIR', './outputs')
    TEMP_DIR = os.getenv('TEMP_DIR', './temp')
    
    # IEEE Format Configuration
    IEEE_FONT_SIZE = 10
    IEEE_COLUMN_COUNT = 2
    IEEE_PAPER_SIZE = 'letter'
    
    @staticmethod
    def validate():
        """Validate critical configuration"""
        if not Config.TAVILY_API_KEY:
            print("WARNING: TAVILY_API_KEY not set. Web search will not work.")
        
        # Create necessary directories
        os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
        os.makedirs(Config.TEMP_DIR, exist_ok=True)
        os.makedirs(Config.CHROMA_PERSIST_DIR, exist_ok=True)
