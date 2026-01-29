"""
Flask Application - Main Entry Point
"""
from flask import Flask, render_template, request, jsonify, Response, send_file
from flask_cors import CORS
import json
import queue
import threading
from datetime import datetime
import os

from config import Config
from backend.synthesis import ResearchEngine
from backend.export import IEEEPDFGenerator, IEEEDOCXGenerator


app = Flask(__name__, 
           template_folder='frontend/templates',
           static_folder='frontend/static')
CORS(app)
app.config.from_object(Config)

# Validate configuration
Config.validate()

# Initialize components
research_engine = ResearchEngine(
    tavily_api_key=Config.TAVILY_API_KEY
)
pdf_generator = IEEEPDFGenerator()
docx_generator = IEEEDOCXGenerator()

# Store for current research results
research_results = {}


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/research/stream')
def research_stream():
    """Stream research progress using Server-Sent Events"""
    topic = request.args.get('topic', '')
    format_type = request.args.get('format', 'screen')
    depth = request.args.get('depth', 'standard')
    
    if not topic:
        return jsonify({'error': 'Topic is required'}), 400
    
    def generate():
        """Generator for SSE"""
        progress_queue = queue.Queue()
        result_container = {}
        
        def progress_callback(progress, message):
            """Callback for progress updates"""
            progress_queue.put({
                'event': 'progress',
                'data': {
                    'progress': progress,
                    'message': message
                }
            })
        
        def run_research():
            """Run research in background thread"""
            try:
                research_engine.set_progress_callback(progress_callback)
                
                # Conduct research based on depth
                if depth == 'quick':
                    result = research_engine.quick_research(topic)
                elif depth == 'deep':
                    result = research_engine.deep_research(topic)
                else:
                    result = research_engine.conduct_research(topic)
                
                result['format'] = format_type
                result_container['data'] = result
                
                # Generate files if requested
                if format_type in ['pdf', 'both']:
                    pdf_path = pdf_generator.generate(result)
                    result['pdf_path'] = pdf_path
                
                if format_type in ['docx', 'both']:
                    docx_path = docx_generator.generate(result)
                    result['docx_path'] = docx_path
                
                # Store results
                research_id = f"{topic}_{datetime.now().timestamp()}"
                research_results[research_id] = result
                result['research_id'] = research_id
                
                progress_queue.put({
                    'event': 'complete',
                    'data': result
                })
                
            except Exception as e:
                progress_queue.put({
                    'event': 'error',
                    'data': {'error': str(e)}
                })
        
        # Start research in background
        thread = threading.Thread(target=run_research)
        thread.start()
        
        # Stream progress updates
        while True:
            try:
                update = progress_queue.get(timeout=30)
                
                event = update['event']
                data = json.dumps(update['data'])
                
                yield f"event: {event}\ndata: {data}\n\n"
                
                if event in ['complete', 'error']:
                    break
                    
            except queue.Empty:
                # Send keepalive
                yield f": keepalive\n\n"
    
    return Response(generate(), mimetype='text/event-stream')


@app.route('/api/download/<format_type>', methods=['POST'])
def download_file(format_type):
    """Download generated file"""
    data = request.json
    
    if format_type == 'pdf':
        if 'pdf_path' in data:
            return send_file(data['pdf_path'], as_attachment=True)
        else:
            # Generate on-demand
            pdf_path = pdf_generator.generate(data)
            return send_file(pdf_path, as_attachment=True)
    
    elif format_type == 'docx':
        if 'docx_path' in data:
            return send_file(data['docx_path'], as_attachment=True)
        else:
            # Generate on-demand
            docx_path = docx_generator.generate(data)
            return send_file(docx_path, as_attachment=True)
    
    return jsonify({'error': 'Invalid format'}), 400


@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    # Check Ollama availability
    ollama_available = research_engine.llm.check_availability()
    
    return jsonify({
        'status': 'healthy',
        'ollama_available': ollama_available,
        'model': Config.OLLAMA_MODEL,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/stats')
def get_stats():
    """Get RAG statistics"""
    stats = research_engine.vector_store.get_stats()
    return jsonify(stats)


if __name__ == '__main__':
    print("=" * 60)
    print("🔬 Deep Research Assistant")
    print("=" * 60)
    print(f"Server starting on http://{Config.HOST}:{Config.PORT}")
    print(f"LLM Model: {Config.OLLAMA_MODEL}")
    print(f"Search API: Tavily")
    print("=" * 60)
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG,
        threaded=True
    )
