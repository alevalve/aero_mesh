import trimesh
import pymeshlab
import numpy as np


# Trimesh Basic Cleaning

def load_mesh(input_path):

    print("Loading mesh...")

    mesh = trimesh.load(input_path, process=False)

    # If file loads as a Scene, merge all geometries
    if isinstance(mesh, trimesh.Scene):
        mesh = trimesh.util.concatenate(tuple(mesh.geometry.values()))
    return mesh

def remove_duplicates(mesh):
    mesh.merge_vertices()
    mesh.remove_duplicate_faces()
    return mesh


def remove_degenerate(mesh):
    mesh.remove_degenerate_faces()
    return mesh


def remove_unreferenced(mesh):
    mesh.remove_unreferenced_vertices()
    return mesh


def fix_normals(mesh):
    mesh.fix_normals()
    return mesh


def remove_area_zero(mesh):
    area = mesh.area_faces
    mask = area > 1e-12
    mesh.update_faces(mask)
    mesh.remove_unreferenced_vertices()
    return mesh


# Convert to PyMeshLab

def pymesh_load(mesh):

    ms = pymeshlab.MeshSet()

    m = pymeshlab.Mesh(
        vertex_matrix=mesh.vertices,
        face_matrix=mesh.faces
    )

    ms.add_mesh(m, "mesh")

    return ms


# PyMeshLab cleaning

def remove_nullfaces(ms):
    ms.meshing_remove_null_faces()
    return ms


def non_manifold_edges(ms):
    ms.meshing_repair_non_manifold_edges()
    return ms


def non_manifold_vertices(ms):
    ms.meshing_repair_non_manifold_vertices()
    return ms


def remove_duplicate_vertices(ms):
    ms.meshing_remove_duplicate_vertices()
    return ms


def remove_duplicate_faces(ms):
    ms.meshing_remove_duplicate_faces()
    return ms


# Convert back to Trimesh

def convert_back(ms):

    m = ms.current_mesh()

    vertices = m.vertex_matrix()
    faces = m.face_matrix()

    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

    return mesh


# Save mesh


def save_mesh(mesh, output_path):
    mesh.export(output_path)
    print("Mesh saved:", output_path)


# Full pipeline

def clean_pipeline(input_path, output_path):

    mesh = load_mesh(input_path)

    mesh = remove_duplicates(mesh)
    mesh = remove_degenerate(mesh)
    mesh = remove_area_zero(mesh)
    mesh = remove_unreferenced(mesh)
    mesh = fix_normals(mesh)

    ms = pymesh_load(mesh)

    ms = remove_nullfaces(ms)
    ms = remove_duplicate_vertices(ms)
    ms = remove_duplicate_faces(ms)
    ms = non_manifold_edges(ms)
    ms = non_manifold_vertices(ms)

    mesh = convert_back(ms)

    save_mesh(mesh, output_path)