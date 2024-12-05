import trimesh
import numpy as np
import matplotlib.pyplot as plt

def center_mesh(mesh):
    """
    Centers the mesh at the origin (0, 0, 0).
    """
    centroid = mesh.centroid
    mesh.vertices -= centroid
    return mesh

def scale_mesh_to_match_bounding_box(mesh1, mesh2):
    """
    Scales mesh1 to match the bounding box of mesh2.
    """
    # Get the bounding boxes of both meshes
    min1, max1 = mesh1.bounding_box.bounds
    min2, max2 = mesh2.bounding_box.bounds
    
    # Calculate the scale factor based on the largest dimension of the bounding boxes
    scale_factor = max(max2 - min2) / max(max1 - min1)
    
    # Scale mesh1
    mesh1.vertices *= scale_factor
    return mesh1

def compute_sdf_at_points(mesh, points):
    """
    Computes the signed distance function (SDF) for a mesh at a set of points.
    Returns an array of signed distances for each point.
    """
    points = np.array(points)  # Ensure points is a (n, 3) array
    distances = mesh.nearest.signed_distance(points)
    """
    Find the signed distance from a mesh to a list of points.

    Points OUTSIDE the mesh will have NEGATIVE distance
    Points within tol.merge of the surface will have POSITIVE distance
    Points INSIDE the mesh will have POSITIVE distance
    """
    return distances

def compute_sdf_error(mesh1, mesh2):
    """
    Computes the error metric between the proposed mesh (mesh1) and the ground truth mesh (mesh2).
    The error is defined as the absolute difference of the SDF values at each point on the surface of mesh1.

    Returns:
      - error
      - sample_points (from proposed mesh)
      - closest_points (from gt)
    """
    # Sample points on the surface of mesh1 (proposed mesh)
    sample_points = mesh1.sample(10000)  # You can change 10000 for more/less samples

    # Compute the SDF of the ground truth mesh (mesh2) at these points
    sdf_gt = compute_sdf_at_points(mesh2, sample_points)

    closest_points, _, _ = mesh2.nearest.on_surface(sample_points)

    return np.mean(sdf_gt), sample_points, closest_points

def align_and_compare_meshes(mesh1, mesh2):
    """
    Align mesh1 to mesh2 by scaling mesh1 to match the bounding box of mesh2.
    Then, compute the SDF error to compare the meshes.
    """
    # Step 1: Center meshes
    # mesh1 = center_mesh(mesh1)
    # mesh2 = center_mesh(mesh2)

    # Step 2: Scale mesh1 to match the bounding box of mesh2
    mesh1 = scale_mesh_to_match_bounding_box(mesh1, mesh2)

    # Step 3: Compute the SDF error between the meshes
    sdf_error = compute_sdf_error(mesh1, mesh2)
    
    return sdf_error

def visualize_meshes(mesh1, mesh2, sdf_error):
    """
    Visualize the meshes with mesh2 (ground truth) in black and mesh1 (proposed) in light green,
    and display the SDF error in the scene.
    """
    # Create a scene and add the meshes
    scene = trimesh.Scene()

    # Set mesh2 (ground truth) to black and mesh1 (proposed) to light green
    mesh2.visual.vertex_colors = [0, 0, 0, 255]  # Black color
    mesh1.visual.vertex_colors = [144, 238, 144, 255]  # Light green color

    # Add meshes to the scene
    scene.add_geometry(mesh2)
    scene.add_geometry(mesh1)

    # Display the SDF error in the visualization (as a text label)
    text = f"SDF Error: {sdf_error:.4f}"
    scene.show(title="Mesh Comparison", caption=text)

# Load the meshes
mesh1 = trimesh.load("gen_mug_handle.obj")  # Replace with your mesh file
# mesh1 = trimesh.load("mug.obj")
# mesh1 = trimesh.load("gen_rotated.obj")
mesh2 = trimesh.load("og_mug_handle.obj")  # Replace with your mesh file

min_bound, max_bound = mesh2.bounding_box.bounds
bbox_size = np.linalg.norm(max_bound - min_bound) 

# Align and compare the meshes
sdf_error, sampled_points_mesh1, nearest_points_mesh2 = align_and_compare_meshes(mesh1, mesh2)
sdf_error = sdf_error / bbox_size
print(f"SDF error: {sdf_error}")

# Visualize the meshes and the error
visualize_meshes(mesh1, mesh2, sdf_error)

# # Visualize only the sampled points
# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')

# # Plot sampled points from mesh1 (in red)
# ax.scatter(sampled_points_mesh1[:, 0], sampled_points_mesh1[:, 1], sampled_points_mesh1[:, 2], c='r', label='Mesh1 Sampled Points', s=1)

# # Plot corresponding nearest points on mesh2 (in blue)
# ax.scatter(nearest_points_mesh2[:, 0], nearest_points_mesh2[:, 1], nearest_points_mesh2[:, 2], c='b', label='Mesh2 Nearest Points', s=1)

# ax.set_xlabel('X')
# ax.set_ylabel('Y')
# ax.set_zlabel('Z')

# ax.legend()

# plt.show()
