from flask import Flask, request, jsonify
import base64
from flask_cors import CORS
import os
from main import run_agent
import logging
from pathlib import Path

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "TTSAIAgent server is running"})

@app.route('/generate', methods=['POST'])
def generate_audio():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        story_text = data.get('story', None)
        if not story_text:
            return jsonify({"error": "No story text provided"}), 400
            
        output_file = data.get('output', 'story_with_sounds.mp3')
        sample_voice = data.get('sample_voice', None)
        
        logger.info(f"Processing story with output file: {output_file}")
        
        # Run the AI agent
        run_agent(story_text=story_text, output_file=output_file, sample_voice_path=sample_voice)

        # Use Downloads folder in home directory
        downloads_folder = str(Path.home() / "Downloads")
        os.makedirs(downloads_folder, exist_ok=True)
        output_path = os.path.join(downloads_folder, output_file)
        
        file_data_b64 = None
        try:
            with open(output_path, 'rb') as f:
                file_data_b64 = base64.b64encode(f.read()).decode('utf-8')
            logger.info(f"Successfully generated audio file: {output_path}")
        except Exception as e:
            logger.error(f"Error reading output file: {e}")
            return jsonify({"error": f"Could not read output file: {str(e)}"}), 500

        return jsonify({
            "status": "success",
            "output_file": output_file,
            "output_path": output_path,
            "file_data": file_data_b64
        })
        
    except Exception as e:
        logger.error(f"Error in generate_audio: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

if __name__ == '__main__':
    # Get host from environment or default to all interfaces for server deployment
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting TTSAIAgent server on {host}:{port}")
    app.run(host=host, port=port, debug=debug)
