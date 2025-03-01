from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
from process_audio import process_audio

app = Flask(__name__, static_folder='../frontend', template_folder='../frontend')

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'audio' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['audio']
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    result = process_audio()
    return jsonify({'result': f'/{result}/'})

if __name__ == '__main__':
    app.run(debug=True)
