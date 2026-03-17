from meshes.general_checks import *
from meshes.general_fixes import *
from meshes.simplification import *
from meshes.smoothing.main_smoothing import main_smoothing
import trimesh
import pymeshlab
import numpy as np
import shutil

def main_revision(mesh_path, output_path, target_faces, simplification=False, smoothing=False, smooth_method='diffusion', smooth_iters=1):

    run_report(mesh_path)
    
    # 1. Cleaning: Read raw mesh_path, save to output_path
    clean_pipeline(mesh_path, output_path)
    
    # 2. Simplification
    if simplification:
        mesh_simplification(output_path, target_faces, output_path)
    
    # 3. Smoothing
    if smoothing:
        main_smoothing(
            input_path=output_path, 
            output_path=output_path, 
            method=smooth_method,
            iterations=smooth_iters
        )

    print("Full process completed")

