import os
from dotenv import load_dotenv
from types import SimpleNamespace
import time

# Import your custom modules
from generation.generation_main import call_3d_generation
from mesh_revisions.mesh_main import main_revision
from ar_display.feature_extractor import generate_mind_file

def run_ar_pipeline(image_list=None, multiview=False, use_target=False):
    """
    Triggers the full 3D -> AR process
    """
    # Setup Configuration
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

    # Generate MindAR Targets
    if use_target:
        generate_mind_file(marker_image, "targets", cfg.files_dir)

    # Step 4: Update the HTML Template
    update_ar_html(cfg, use_target=use_target)

    print("Pipeline Complete")
    return True


def update_ar_html(cfg, use_target=False):
    """
    Selects the template and performs string replacement.
    """
    # Choose which template to read
    template_name = "target.html" if use_target else "no_target.html"
    template_path = os.path.join(os.path.dirname(cfg.template), template_name)
    
    with open(template_path, 'r') as f:
        content = f.read()

    # Shared replacements
    content = content.replace("{{MODEL_FILE}}", "files/current_model.glb")
    content = content.replace("{{TIMESTAMP}}", str(int(time.time())))

    # Target-only replacements
    if use_target:
        content = content.replace("{{MIND_FILE}}", "files/targets.mind")
        content = content.replace("{{IMAGE_FILE}}", "files/image_0.jpeg")

    with open(cfg.output_html, 'w') as f:
        f.write(content)

if __name__ == "__main__":
    run_ar_pipeline()