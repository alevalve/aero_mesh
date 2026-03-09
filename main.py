from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import shutil
from main_pipeline import run_ar_pipeline 

app = Flask(__name__, static_url_path='', static_folder='.')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'files')

@app.route('/')
def index():
    return render_template('capture.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'images' not in request.files:
        return jsonify({"status": "error", "message": "No images provided"}), 400
    
    if os.path.exists(UPLOAD_FOLDER):
        shutil.rmtree(UPLOAD_FOLDER)
    os.makedirs(UPLOAD_FOLDER)

    uploaded_files = request.files.getlist('images')
    saved_paths = []
    
    for i, file in enumerate(uploaded_files):
        filename = f"image_{i}.jpeg"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        saved_paths.append(os.path.abspath(file_path))
    
    is_multiview = len(saved_paths) > 1
    
    # Trigger the pipeline

    use_target_str = request.form.get('use_target', 'true')
    use_target = use_target_str.lower() == 'true'

    success = run_ar_pipeline(image_list=saved_paths, multiview=is_multiview, use_target=use_target)

    if success:
        return jsonify({"status": "success", "message": "3D Model Generated!"})
    else:
        return jsonify({"status": "error", "message": "Pipeline failed"}), 500
    

@app.route('/index.html')
def serve_index():
    return send_from_directory(BASE_DIR, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555, ssl_context='adhoc')