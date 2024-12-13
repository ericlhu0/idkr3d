import trimesh
import numpy as np
from PIL import Image
import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


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
    min1, max1 = mesh1.bounding_box.bounds
    min2, max2 = mesh2.bounding_box.bounds
    scale_factor = max(max2 - min2) / max(max1 - min1)
    mesh1.vertices *= scale_factor
    return mesh1


def compute_sdf_at_points(mesh, points):
    """
    Computes the signed distance function (SDF) for a mesh at a set of points.
    Returns an array of signed distances for each point.
    """
    points = np.array(points)
    distances = mesh.nearest.signed_distance(points)
    return distances


def compute_sdf_error(mesh1, mesh2):
    """
    Computes the error metric between the proposed mesh and the ground truth mesh.
    """
    sample_points_m1 = mesh1.sample(10000)
    sample_points_gt = mesh2.sample(10000)

    sdf_gt = compute_sdf_at_points(mesh2, sample_points_m1)
    sdf_symmetric = compute_sdf_at_points(mesh1, sample_points_gt)

    sdf_gt = np.mean(np.abs(sdf_gt))
    sdf_symmetric = np.mean(np.abs(sdf_symmetric))

    return (sdf_gt + sdf_symmetric) / 2


def align_and_compare_meshes(mesh1, mesh2):
    """
    Align mesh1 to mesh2 and compute the SDF error.
    """
    mesh1 = center_mesh(mesh1)
    mesh2 = center_mesh(mesh2)
    mesh1 = scale_mesh_to_match_bounding_box(mesh1, mesh2)
    sdf_error = compute_sdf_error(mesh1, mesh2)
    return sdf_error


def visualize_meshes(mesh1, mesh2, sdf_error, output_path):
    """
    Create and save a visualization of the meshes using matplotlib.
    """
    plt.figure(figsize=(10, 10))
    ax = plt.axes(projection='3d')

    # Plot mesh1 (proposed) faces
    for face in mesh1.faces:
        vertices = mesh1.vertices[face]
        ax.plot_trisurf(vertices[:, 0], vertices[:, 1], vertices[:, 2],
                        color='red', alpha=0.5)

    # Plot mesh2 (ground truth) faces
    for face in mesh2.faces:
        vertices = mesh2.vertices[face]
        ax.plot_trisurf(vertices[:, 0], vertices[:, 1], vertices[:, 2],
                        color='black', alpha=0.5)

    # Set labels
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    # Set title with SDF error
    plt.title(f'SDF Error: {sdf_error:.4f}')

    # Make the plot look nice
    ax.view_init(elev=30, azim=45)

    # Set equal aspect ratio
    ax.set_box_aspect([1, 1, 1])

    # Save the plot
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


# Main execution
handles_folder_path = "/home/lifchrs/cut_handles_baseline"
output_file_path = "/home/lifchrs/r3d/sdf_data_method.txt"

# Get all OBJ files in the folder
obj_file_paths = [
    os.path.join(handles_folder_path, f)
    for f in os.listdir(handles_folder_path)
    if f.lower().endswith('.obj')
]

# Load ground truth mesh
gt_mesh = trimesh.load("../../gt_handle.obj")
alr_read = []
not_read = []
# print(sorted(obj_file_paths))

for file in obj_file_paths:
    # print(f"Processing: {file}")
    try:
        with open('baseline_sdfs.txt', 'r') as output_file:
            file_content = output_file.read()
            if "15" in file:
                print(file)
            # print(file_content)
            if file.split("/")[-1] in file_content:
                # print("alr read", file)
                alr_read.append(file)
                continue
            print("haven't read", file)
            not_read.append(file)
        # Load the proposed handle mesh
        mesh = trimesh.load(file)
        print('Mesh loaded')

        # Calculate bounding box size of ground truth for normalization
        min_bound, max_bound = gt_mesh.bounding_box.bounds
        bbox_size = np.linalg.norm(max_bound - min_bound)
        print('Bounding box size calculated')

        # Align and compare meshes
        sdf_error = align_and_compare_meshes(mesh, gt_mesh)
        sdf_error = sdf_error / bbox_size
        print(f"Normalized SDF error: {sdf_error}")
        with open("baseline_sdfs.txt", "a") as myfile:
            myfile.write(f"{file.split('/')[-1]} {sdf_error}\n")

        # Save visualization
        output_image_path = os.path.splitext(file)[0] + "_comparison.png"
        visualize_meshes(mesh, gt_mesh, sdf_error, output_image_path)
        print(f"Visualization saved to: {output_image_path}")

    except Exception as e:
        print(f"Error processing {file}: {str(e)}")
        # raise  # This will show the full error traceback
print(len(alr_read), len(not_read))