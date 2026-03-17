import numpy as np
import igl
from scipy.sparse.linalg import factorized

def fairing_smoothing(vertices, faces, lambda_steps=0.5, iterations=1):
    """"Minimizes surface area via mean curvature flow just in the interior"""

    v = vertices.copy()
    
    # identify boundary vertices
    boundary = igl.boundary_facets(faces).flatten()
    boundary = np.unique(boundary)
    interior = np.setdiff1d(np.arange(len(v)), boundary)

    for _ in range(iterations):
        L = igl.cotmatrix(v, faces)
        M = igl.massmatrix(v, faces, igl.MASSMATRIX_TYPE_VORONOI)
        
        # impllcit fairing system (M - λL) v_new = M v
        A = M - lambda_steps * L
        b = M.dot(v)
        A_csc = A.tocsc()  
        A_int = A_csc[np.ix_(interior, interior)]
        b_int = b[interior] - A_csc[np.ix_(interior, boundary)].dot(v[boundary])
        
        # solve
        solve = factorized(A_int)

        v_new = v.copy()  # boundary preserved
        v_new[interior, 0] = solve(b_int[:,0])
        v_new[interior, 1] = solve(b_int[:,1])
        v_new[interior, 2] = solve(b_int[:,2])
        
        v = v_new
    
    return v

