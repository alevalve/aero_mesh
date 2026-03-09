import pymeshlab
import os

ms = pymeshlab.MeshSet()

def import_mesh(mesh_path):
    ms.load_new_mesh(mesh_path)
    return ms.current_mesh()

def basic_stats(mesh):
    geom = ms.get_geometric_measures()
    topo = ms.get_topological_measures()
    return geom, topo

def manifoldness(out_dict):
    nm_edges = out_dict.get('non_manifold_edges', 0)
    nm_verts = out_dict.get('non_manifold_vertices', 0)
    
    is_manifold = (nm_edges == 0 and nm_verts == 0)
    return is_manifold, nm_edges, nm_verts

def self_intersections():
    ms.compute_selection_by_self_intersections_per_face()
    intersecting_faces = ms.current_mesh().selected_face_number()
    return intersecting_faces

def degenerate_faces():
    ms.compute_selection_bad_faces()
    small_faces = ms.current_mesh().selected_face_number()
    return small_faces

# --- MAIN EXECUTION ---
def run_report(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return

    mesh = import_mesh(file_path)
    geom, topo = basic_stats(mesh)

    is_manifold, nm_e, nm_v = manifoldness(topo) 
    intersect_count = self_intersections()
    small_faces = degenerate_faces()
    

    print("-" * 60)
    print(f"MESH REPORT: {os.path.basename(file_path)}")
    print("-" * 60)
    
    print("\nSECTION 2: TOPOLOGY AND MESH HEALTH")
    print(f"Vertices: {mesh.vertex_number()}")
    print(f"Faces:    {mesh.face_number()}")
    
    manifold_status = "PASSED" if is_manifold else f"FAILED (Edges: {nm_e}, Vertices: {nm_v})"
    print(f"Manifold Status: {manifold_status}")
    
    print("\nSECTION 3: GEOMETRIC ERRORS")
    intersect_status = "NONE" if intersect_count == 0 else f"WARNING: {intersect_count} faces"
    degenerate_status = "NONE" if small_faces == 0 else f"WARNING: {small_faces} faces"
    
    print(f"Self-Intersections: {intersect_status}")
    print(f"Degenerate Faces:   {degenerate_status}")
    
    print("\nSECTION 4: SYSTEM RECOMMENDATIONS")
    if intersect_count > 1000:
        print("Note: High intersection count detected. Remeshing is advised for specific tasks")
    if mesh.face_number() > 50000:
        print("Note: High polygon count. Consider decimation for mobile AR performance.")
        
    print("\n" + "-" * 60)
