import os
import shutil
from generation.generation_main import call_3d_generation, download_model
from mesh_revisions.mesh_main import main_revision
from ar_display.feature_extractor import generate_mind_file
from dotenv import load_dotenv

# Set Meshy Key
load_dotenv()
api_key = os.getenv("MESHY_API_KEY")

if not api_key:
    raise ValueError("MESHY_API_KEY not found. Did you create the .env file?")

print("Meshy API Key loaded successfully.")

# Configurations
BASE_DIR = "/Users/alexandervalverde/Documents/AR_App"
FILES_DIR = os.path.join(BASE_DIR, "files")
TEMPLATE_PATH = os.path.join(BASE_DIR, "ar_display/index.html")
FINAL_HTML_PATH = os.path.join(BASE_DIR, "index.html")

# Define assets
input_img_name = "image.jpeg"
input_img_path = os.path.join(FILES_DIR, input_img_name)
temp_glb = os.path.join(FILES_DIR, "raw_model.glb")
final_glb = os.path.join(FILES_DIR, "current_model.glb")

def run_ar_pipeline():
    print("Starting AR Pipeline...")

    # Step 1: Generate 3D model from image
    mesh_url = call_3d_generation(input_img_path, api_key=api_key, output_dir=FILES_DIR, multiview=False)
    if not mesh_url:
        print("Failed to get mesh URL.")
        return
    
    # Step 2: Download the raw model
    download_model(mesh_url, temp_glb)
    print("Raw model downloaded.")

    # Step 3: Refine Mesh
    target_face_count = 5000
    main_revision(temp_glb, final_glb, target_face_count, simplification=False)
    
    # Cleanup
    if os.path.exists(temp_glb):
        os.remove(temp_glb)
    print("Mesh refined and cleaned up.")

    # Step 4: Generate MindAR Targets
    generate_mind_file(input_img_path, "targets", FILES_DIR)
    print("MindAR targets generated.")

    # Step 5: Update HTML
    update_ar_html(
        mind_rel="files/targets.mind",
        img_rel=f"files/{input_img_name}",
        model_rel="files/current_model.glb"
    )

def update_ar_html(mind_rel, img_rel, model_rel):
    if not os.path.exists(TEMPLATE_PATH):
        print(f"Template not found at {TEMPLATE_PATH}")
        return

    with open(TEMPLATE_PATH, 'r') as f:
        content = f.read()

    content = content.replace("{{MIND_FILE}}", mind_rel)
    content = content.replace("{{IMAGE_FILE}}", img_rel)
    content = content.replace("{{MODEL_FILE}}", model_rel)

    with open(FINAL_HTML_PATH, 'w') as f:
        f.write(content)
    

if __name__ == "__main__":
    run_ar_pipeline()