import os
from dotenv import load_dotenv
from types import SimpleNamespace

# Import your custom modules
from generation.generation_main import call_3d_generation
from mesh_revisions.mesh_main import main_revision
from ar_display.feature_extractor import generate_mind_file

def run_ar_pipeline(image_list=None, multiview=False):
    """
    Triggers the full 3D -> AR process
    """
    # 1. Setup Configuration
    load_dotenv()
    base = "/Users/alexandervalverde/Documents/AR_App/3d_ar_app"
    
    cfg = SimpleNamespace(
        api_key=os.getenv("MESHY_API_KEY"),
        files_dir=os.path.join(base, "files"),
        template=os.path.join(base, "ar_display/index.html"),
        output_html=os.path.join(base, "index.html"),
        temp_glb=os.path.join(base, "files/raw_model.glb"),
        final_glb=os.path.join(base, "files/current_model.glb")
    )
    
    if not multiview and isinstance(image_list, list):
        processing_input = image_list[0] 
    else:
        processing_input = image_list

    # The marker is always the first image provided
    marker_image = image_list[0] if isinstance(image_list, list) else image_list

    print(f"Starting AR Pipeline (Multiview: {multiview})")

    # Step 1: Generate & Download
    mesh_url = call_3d_generation(
        images=processing_input, 
        api_key=cfg.api_key, 
        output_dir=cfg.files_dir, 
        multiview=multiview
    )
    
    if not mesh_url:
        print("Failed to get mesh URL from Meshy.")
        return False

    # Step 2: Refine Mesh 
    main_revision(cfg.temp_glb, cfg.final_glb, target_faces=5000, simplification=False)
    
    # Cleanup temp file
    if os.path.exists(cfg.temp_glb):
        os.remove(cfg.temp_glb)

    # Step 3: Generate MindAR Targets
    generate_mind_file(marker_image, "targets", cfg.files_dir)

    # Step 4: Update the HTML Template
    update_ar_html(cfg)

    print("Pipeline Complete")
    return True


def update_ar_html(cfg):
    """Handles the string replacement for the AR view."""
    with open(cfg.template, 'r') as f:
        content = f.read()

    # Relative paths for the web browser
    content = content.replace("{{MIND_FILE}}", "files/targets.mind")
    content = content.replace("{{IMAGE_FILE}}", "files/image.jpeg")
    content = content.replace("{{MODEL_FILE}}", "files/current_model.glb")

    with open(cfg.output_html, 'w') as f:
        f.write(content)

if __name__ == "__main__":
    run_ar_pipeline()