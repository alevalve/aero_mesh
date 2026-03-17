import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import factorized
import igl

def diffusion_smoothing(vertices, faces, lambda_steps=0.5, iterations=1):
    """Performs diffusion smoothing on a mesh using the cotangent Laplacian."""

    v_current = vertices.copy()

    for _ in range(iterations):
        # Compute cotangent laplacian 
        l_c = igl.cotmatrix(v_current, faces)
        # compute the mass matrix 
        m_vec = igl.massmatrix(v_current, faces, igl.MASSMATRIX_TYPE_VORONOI)
        s_matrix = m_vec
        # System matrix for diffusion smoothing
        a_sys = s_matrix - lambda_steps * l_c
        # Set the RHS
        b = s_matrix.dot(v_current)
        # Solve the linear system for each coordinate
        a_sys_csc = a_sys.tocsc()
        solve_func = factorized(a_sys_csc)

        v_new = np.zeros_like(v_current)
        v_new[:,0] = solve_func(b[:,0])
        v_new[:,1] = solve_func(b[:,1])
        v_new[:,2] = solve_func(b[:,2])

        v_current = v_new

    return v_current


