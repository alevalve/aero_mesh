import trimesh
from .diffusion import diffusion_smoothing
from .laplacian import laplacian_smoothing_implicit
from .fairing import fairing_smoothing

def main_smoothing(input_path, output_path, method='diffusion', lambda_steps=0.5, iterations=1):
    """
    Loads a mesh, applies a chosen smoothing algorithm, and saves the output.
    """
    # Load the mesh
    mesh = trimesh.load(input_path, process=False, force='mesh')
    vertices = mesh.vertices
    faces = mesh.faces

    print(f"Applying {method} smoothing...")

    # Route to the chosen smoothing method
    if method == 'laplacian':
        new_vertices = laplacian_smoothing_implicit(vertices, faces, lambda_steps, iterations)
    elif method == 'fairing':
        new_vertices = fairing_smoothing(vertices, faces, lambda_steps, iterations)
    elif method == 'diffusion':
        new_vertices = diffusion_smoothing(vertices, faces, lambda_steps, iterations)
    else:
        raise ValueError(f"Unknown smoothing method: {method}. Choose 'laplacian', 'fairing', or 'diffusion'.")

    mesh.vertices = new_vertices
    mesh.export(output_path)