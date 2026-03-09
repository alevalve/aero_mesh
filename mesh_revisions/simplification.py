import trimesh
import pymeshlab
import numpy as np

def mesh_simplification(mesh_path, target_faces, output_path):
    # Load mesh
    ms = pymeshlab.MeshSet()
    ms.load_new_mesh(mesh_path)

    # Apply mesh decimation with quadric edge collapse
    ms.meshing_decimation_quadric_edge_collapse(targetfacenum=target_faces, 
                                                preservenormal=True,
                                                preserveboundary=True,
                                                optimalplacement=True
                                                )
    cleaned = ms.current_mesh()
    vertices = cleaned.vertex_matrix()
    faces = cleaned.face_matrix()
    
    # Convert to trimesh for final cleanup
    clean_trimesh = trimesh.Trimesh(vertices=vertices, faces=faces)

    # Final cleanup
    clean_trimesh.remove_duplicate_faces()
    clean_trimesh.remove_unreferenced_vertices()
    clean_trimesh.remove_degenerate_faces()

    clean_trimesh.export(output_path)

    print("Mesh simplified")



