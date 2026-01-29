# Deep Research Assistant

A comprehensive research assistant that transforms user topics into structured IEEE-format research reports using local LLM inference, web search, RAG, and real-time data agents.

## Features

- 🤖 **Local LLM Integration** - Uses Ollama for query generation and synthesis
- 🔍 **Web Search** - Tavily API for comprehensive web searches
- 📚 **RAG System** - ChromaDB vector database for recent data retrieval
- 🌐 **Real-time Agents** - Fetch data from arXiv, Wikipedia, and news sources
- 📄 **IEEE Formatting** - Generate professional PDF and DOCX reports
- 🎨 **Scientific UI** - Modern, knowledge-focused interface
- ⚡ **Real-time Progress** - Live updates during research

## Prerequisites

1. **Ollama** - Local LLM inference engine
   ```bash
   # Install Ollama from https://ollama.ai
   # Pull a model (e.g., llama3.2)
   ollama pull llama3.2
   ```

2. **Python 3.8+**

3. **Tavily API Key** - Get free API key from https://tavily.com

## Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd X:\MSRIT\Py_project\deep-research-assistant
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   # Copy example env file
   copy .env.example .env
   
   # Edit .env and add your Tavily API key
   # TAVILY_API_KEY=your-api-key-here
   ```

## Configuration

Edit `.env` file to configure:

- `OLLAMA_MODEL` - LLM model to use (default: llama3.2)
- `TAVILY_API_KEY` - Your Tavily API key
- `RESEARCH_DEPTH` - Default research depth (quick/standard/deep)
- `MAX_QUERIES` - Maximum search queries per research
- `OUTPUT_DIR` - Directory for generated files

## Usage

1. **Start Ollama** (if not running)
   ```bash
   ollama serve
   ```

2. **Run the application**
   ```bash
   python main.py
   ```

3. **Open browser**
   ```
   http://localhost:5000
   ```

4. **Conduct research**
   - Enter your research topic
   - Select output format (Screen/PDF/DOCX/Both)
   - Choose research depth
   - Click "Start Research"
   - Watch real-time progress
   - View results or download files

## Project Structure

```
deep-research-assistant/
├── backend/
│   ├── llm/              # LLM integration (Ollama)
│   ├── search/           # Web search (Tavily)
│   ├── rag/              # Vector database (ChromaDB)
│   ├── agents/           # Real-time data agents
│   ├── synthesis/        # Research engine & citations
│   └── export/           # PDF/DOCX generators
├── frontend/
│   ├── static/
│   │   ├── css/          # Scientific theme
│   │   └── js/           # Frontend logic
│   └── templates/        # HTML templates
├── templates/
│   └── ieee_format/      # IEEE specifications
├── config.py             # Configuration
├── main.py               # Flask application
└── requirements.txt      # Dependencies
```

## API Endpoints

- `GET /` - Main application
- `GET /api/research/stream` - SSE stream for research progress
- `POST /api/download/<format>` - Download generated files
- `GET /api/health` - Health check
- `GET /api/stats` - RAG statistics

## Research Process

1. **Query Generation** - LLM generates search queries from topic
2. **Web Search** - Multi-query search using Tavily
3. **Real-time Data** - Fetch from arXiv, Wikipedia, news
4. **Source Scoring** - Rank by relevance and credibility
5. **RAG Indexing** - Store in vector database
6. **Content Analysis** - LLM analyzes each source
7. **Synthesis** - Generate coherent research report
8. **Citation** - Add IEEE-format citations
9. **Export** - Generate PDF/DOCX with IEEE formatting

## Output Formats

### PDF
- IEEE two-column format (configurable)
- Proper section numbering
- Bibliography with citations
- Professional typography

### DOCX
- IEEE-compliant styling
- Editable format
- Compatible with Microsoft Word
- Easy to customize

### On-Screen
- Formatted HTML display
- Interactive citations
- Responsive design
- Copy-paste friendly

## Troubleshooting

### Ollama not available
```bash
# Check if Ollama is running
ollama list

# Start Ollama service
ollama serve
```

### Tavily API errors
- Verify API key in `.env`
- Check API quota at https://tavily.com
- Try with fewer queries (quick mode)

### Import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### ChromaDB issues
```bash
# Clear vector database
rm -rf data/chromadb
```

## Advanced Configuration

### Custom LLM Model
```env
OLLAMA_MODEL=mistral
# or
OLLAMA_MODEL=llama2
```

### Research Depth
- **Quick**: 3 queries, ~1 minute
- **Standard**: 5 queries, ~2 minutes
- **Deep**: 8 queries, ~3 minutes

### Vector Database
- Automatic document chunking
- Semantic search
- Persistent storage
- Configurable embedding model

## Contributing

This is a demonstration project. Feel free to:
- Add more data sources
- Improve synthesis prompts
- Enhance UI design
- Add export formats
- Optimize performance

## License

MIT License - Feel free to use and modify

## Credits

Built with:
- Ollama - Local LLM inference
- Tavily - AI-powered search
- ChromaDB - Vector database
- Flask - Web framework
- ReportLab - PDF generation
- python-docx - DOCX generation

---

**Happy Researching! 🔬**
