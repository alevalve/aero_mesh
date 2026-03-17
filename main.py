from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import shutil
from main_pipeline import run_ar_pipeline 
import time
from PIL import Image
import numpy as np
import json
from computer_vision.depth import DepthEstimator

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
    

depth_estimator = DepthEstimator()


@app.route('/estimate-placement', methods=['POST'])
def estimate_placement():

    img = Image.open(request.files['frame']).convert("RGB")
    rgb = np.array(img)
    video_h, video_w = rgb.shape[:2] 

    depth_estimator.update_frame(rgb)

    touches = json.loads(request.form.get('touches'))

    metrics = depth_estimator.metrics_from_touches(touches, display_w=video_w, display_h=video_h)

    with depth_estimator._lock:
        depth_map = depth_estimator._depth_map
        focal_px = depth_estimator._focal_px
        dh, dw = depth_map.shape
        
        pts = []
        for t in touches:
            scaled_x = t["x"] * dw / video_w
            scaled_y = t["y"] * dh / video_h
            pts.append(depth_estimator.get_3d_point(scaled_x, scaled_y, depth_map, focal_px))
            
    midpoint = (pts[0] + pts[1]) / 2.0

    return jsonify({
        "x": float(midpoint[0]),
        "y": float(midpoint[1]),
        "z": float(midpoint[2]),
        "metrics": metrics 
    })

@app.route('/index.html')
def serve_index():
    return send_from_directory(BASE_DIR, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555, use_reloader=False)