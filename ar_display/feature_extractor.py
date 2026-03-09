import subprocess
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NODE_BRIDGE = os.path.join(BASE_DIR, "compiler.js")

def generate_mind_file(image_path: str, output_name: str, output_dir: str):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    NODE_BRIDGE = os.path.join(BASE_DIR, "compiler.js")

    abs_image_path = os.path.abspath(image_path)
    
    if not output_name.endswith(".mind"):
        output_name += ".mind"
    abs_output_file = os.path.abspath(os.path.join(output_dir, output_name))
    
    print(f"--- Compiling AR Target: {abs_image_path} ---")
    
    result = subprocess.run(
        ["node", NODE_BRIDGE, abs_image_path, abs_output_file],
        capture_output=True,
        text=True,
        cwd=BASE_DIR 
    )
    if result.returncode != 0:
        print("Error during compilation:")
        print(result.stderr)
        return None

    print(f"Successfully generated: {abs_output_file}")
    return abs_output_file