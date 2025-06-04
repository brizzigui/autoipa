from flask import Flask, request, jsonify, render_template
from werkzeug import exceptions 
import os
from transcribe.run import Runner
from process_audio import process_raw_audio, process_file_audio
import uuid, time

app = Flask(__name__, static_folder='../frontend', template_folder='../frontend')
runner = Runner()

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# sets max file size of 16mb for protection
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about/index.html')

@app.route('/upload_file', methods=['POST'])
def upload_file():
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['audio']
        filename = f"{int(time.time() * 1000)}_{uuid.uuid4().hex}"
        filepath = os.path.join("outputs", f"{filename}.wav")
        file.save(filepath)
        
        result = process_file_audio(runner, filename)
        return jsonify(result)
    
    except exceptions.RequestEntityTooLarge:
        print("Aborting: file too large")
        return jsonify({'error': 'File too large'}), 413


@app.route('/upload', methods=['POST'])
def upload_voice():
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['audio']

        # creates a random filename to avoid colisions from simultaneous requests
        filename = f"{int(time.time() * 1000)}_{uuid.uuid4().hex}"

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{filename}.webm")
        file.save(filepath)
        
        result = process_raw_audio(runner, filename)
        return jsonify(result)
    
    except exceptions.RequestEntityTooLarge:
        print("Aborting: file too large")
        return jsonify({'error': 'File too large'}), 413

if __name__ == '__main__':
    app.run()
