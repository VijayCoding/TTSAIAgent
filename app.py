from flask import Flask, request, jsonify
import base64
from flask_cors import CORS
import os
from main import run_agent

app = Flask(__name__)
CORS(app)

@app.route('/generate', methods=['POST'])
def generate_audio():
    data = request.json
    story_text = data.get('story', None)
    output_file = data.get('output', 'story_with_sounds.mp3')
    sample_voice = data.get('sample_voice', None)
    run_agent(story_text=story_text, output_file=output_file, sample_voice_path=sample_voice)


    # Use the same Downloads folder path as in main.py
    from pathlib import Path
    downloads_folder = str(Path.home() / "Downloads")
    os.makedirs(downloads_folder, exist_ok=True)
    output_path = os.path.join(downloads_folder, output_file)
    file_data_b64 = None
    try:
        with open(output_path, 'rb') as f:
            file_data_b64 = base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        file_data_b64 = None

    # Prepare response
    response_data = {
        "status": "success",
        "output_file": output_file,
        # "output_path": output_path,
        "file_data": file_data_b64
    }

    # Delete the file after reading it
    try:
        if os.path.exists(output_path):
            os.remove(output_path)
            print(f"Deleted file: {output_path}")
    except Exception as e:
        print(f"Warning: Could not delete file {output_path}: {e}")

    return jsonify(response_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)