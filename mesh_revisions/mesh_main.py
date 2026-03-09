from mesh_revisions.general_checks import *
from mesh_revisions.general_fixes import *
from mesh_revisions.simplification import *
import trimesh
import pymeshlab
import numpy as np


def main_revision(mesh_path, output_path, target_faces, simplification=False):

    run_report(mesh_path)
    clean_pipeline(mesh_path, output_path)
    if simplification == True:
        mesh_simplification(mesh_path, target_faces, output_path)

    print("Full process completed")


