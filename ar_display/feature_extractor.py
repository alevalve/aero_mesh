import subprocess
import os

# Your existing constants
BASE_DIR = "/Users/alexandervalverde/Documents/AR_App/AR_Display"
NODE_BRIDGE = os.path.join(BASE_DIR, "compiler.js")

def generate_mind_file(image_path: str, output_name: str, output_dir: str):
    """
    Compiles a target image into a .mind file and saves it to output_dir.
    """
    # 1. Ensure the directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    # 2. Ensure the filename ends with .mind
    if not output_name.endswith(".mind"):
        output_name += ".mind"
        
    # 3. Construct the full path in the NEW directory
    output_file = os.path.join(output_dir, output_name)
    
    print(f"--- Compiling AR Target: {image_path} ---")
    
    # Run the Node.js bridge
    
    result = subprocess.run(
        ["node", NODE_BRIDGE, image_path, output_file],
        capture_output=True,
        text=True,
        cwd=BASE_DIR 
    )
    
    if result.returncode != 0:
        print("Error during compilation:")
        print(result.stderr)
        return None

    print(f"Successfully generated: {output_file}")
    return output_file