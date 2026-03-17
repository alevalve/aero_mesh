import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import spsolve
import trimesh
from scipy.sparse.linalg import factorized

import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import factorized
import igl

def laplacian_smoothing_implicit(vertices, faces, lambda_steps=0.5, iterations=1):
    """Performs implicit Laplacian smoothing on a mesh without Trimesh overhead."""
    
    # Get Adjacency matrix 
    A = igl.adjacency_matrix(faces)
    # Degree matrix
    degrees = np.array(A.sum(axis=1)).flatten()
    D = sp.diags(degrees)
    # Laplacian matrix (Uniform)
    L = D - A
    # Identity matrix
    I = sp.eye(len(vertices))
    # System matrix for implicit smoothing
    A_sys = I + lambda_steps * L
    # Convert to CSC and pre-factor
    A_sys_csc = A_sys.tocsc()
    solve_func = factorized(A_sys_csc)
    v_current = vertices.copy()
    # Solve the linear system iteratively
    for _ in range(iterations):
        v_current[:, 0] = solve_func(v_current[:, 0])
        v_current[:, 1] = solve_func(v_current[:, 1])
        v_current[:, 2] = solve_func(v_current[:, 2])
    
    return v_current

