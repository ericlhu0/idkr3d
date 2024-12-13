import numpy as np
import trimesh
import logging

def rotate_meshes(og_mesh_filename, new_mesh_filename, output_path):
    """
    Reads two meshes and creates a 3rd mesh that is 'new_mesh' with its orientation rotated to match 'og_mesh'
    
    Parameters:
        og_mesh_filename (str): Name of the original mesh file (without .obj)
        new_mesh_filename (str): Name of the new mesh file (without .obj)
        output_path (str): Path for the output mesh
    """
    def translate_mesh(mesh):
        """Centers the mesh so the base is at z=0"""
        z_coords = mesh.vertices[:, 2]
        z_min = np.min(z_coords)
        mesh.vertices[:, 2] -= z_min
        return mesh

    def planar_direction(mesh):
        """Calculate the planar direction vector of the handle"""
        vertices = mesh.vertices
        z_coords = vertices[:, 2]
        z_min, z_max = np.min(z_coords), np.max(z_coords)
        height = z_max - z_min
        
        # More permissive body mask
        body_mask = (z_coords > z_min + 0.05*height) & (z_coords < z_max - 0.1*height)
        body_vertices = vertices[body_mask]
        
        if len(body_vertices) == 0:
            logging.warning("No vertices found in body mask")
            return np.array([1, 0, 0])  # Default direction if detection fails
            
        body_center_xy = np.mean(body_vertices[:, :2], axis=0)
        
        # Calculate radial distances with error checking
        body_radial_distances = np.maximum(
            np.linalg.norm(body_vertices[:, :2] - body_center_xy, axis=1),
            1e-6  # Prevent zero distances
        )
        
        mean_radius = np.mean(body_radial_distances)
        radius_std = np.std(body_radial_distances)
        
        # More permissive handle detection
        radial_distances = np.linalg.norm(vertices[:, :2] - body_center_xy, axis=1)
        height_mask = (z_coords > z_min + 0.05 * height) & (z_coords < z_max - 0.1 * height)
        handle_mask = (radial_distances > mean_radius + radius_std) & height_mask
        
        handle_vertices = vertices[handle_mask]
        
        if len(handle_vertices) == 0:
            logging.warning("No handle vertices detected")
            return np.array([1, 0, 0])  # Default direction if handle detection fails
            
        handle_centroid = np.mean(handle_vertices, axis=0)
        body_centroid = np.mean(body_vertices, axis=0)
        
        direction = handle_centroid - body_centroid
        planar_direction = np.array([direction[0], direction[1], 0])
        
        # Safe normalization
        norm = np.linalg.norm(planar_direction[:2])
        if norm < 1e-6:
            return np.array([1, 0, 0])  # Default direction if normalization would fail
            
        return planar_direction / norm

    def compute_transformation(new_vec, og_vec):
        """Compute the rotation matrix to align new_vec with og_vec"""
        # Ensure vectors are normalized and non-zero
        new_norm = np.linalg.norm(new_vec)
        og_norm = np.linalg.norm(og_vec)
        
        if new_norm < 1e-6 or og_norm < 1e-6:
            logging.warning("Zero magnitude vector encountered")
            return np.eye(3)  # Return identity matrix if vectors are too small
            
        norm_new_vec = new_vec / new_norm
        norm_og_vec = og_vec / og_norm
        
        # Compute rotation axis
        axis = np.cross(norm_new_vec, norm_og_vec)
        axis_norm = np.linalg.norm(axis)
        
        if axis_norm < 1e-6:
            # Vectors are parallel or anti-parallel
            dot_product = np.dot(norm_new_vec, norm_og_vec)
            if dot_product > 0:
                return np.eye(3)  # Already aligned
            else:
                # Need 180-degree rotation
                return -np.eye(3)
                
        axis = axis / axis_norm
        
        # Compute rotation angle
        theta = np.arccos(np.clip(np.dot(norm_new_vec, norm_og_vec), -1.0, 1.0))
        
        # Rodrigues rotation formula
        k = np.array([
            [0, -axis[2], axis[1]],
            [axis[2], 0, -axis[0]],
            [-axis[1], axis[0], 0]
        ])
        
        return np.eye(3) + np.sin(theta)*k + (1 - np.cos(theta))*(k @ k)

    def scale_mesh_to_match_bounding_box(mesh1, mesh2):
        """
        Scales mesh1 to match the bounding box height of mesh2.
        """
        # Get the bounding boxes of both meshes
        min1, max1 = mesh1.bounding_box.bounds
        min2, max2 = mesh2.bounding_box.bounds

        # Calculate the scale factor based on the largest dimension of the bounding boxes
        scale_factor_y = (max2[1] - min2[1]) / (max1[1] - min1[1])

        print('scale factor y: ', scale_factor_y)

        # Scale mesh1
        mesh1.vertices *= scale_factor_y

        return mesh1

    try:
        # Load meshes
        og_mesh = trimesh.load_mesh(og_mesh_filename + '.obj')
        new_mesh = trimesh.load_mesh(new_mesh_filename + '.obj')
        new_mesh = scale_mesh_to_match_bounding_box(new_mesh, og_mesh)
        if og_mesh is None or new_mesh is None:
            raise ValueError("Failed to load one or both meshes")
            
        # Initial rotation
        x_rot = trimesh.transformations.rotation_matrix(np.radians(90), [1, 0, 0])
        new_mesh.apply_transform(x_rot)
        
        # Center meshes
        new_mesh = translate_mesh(new_mesh)
        og_mesh = translate_mesh(og_mesh)
        
        # Calculate and apply rotation
        og_normal = planar_direction(og_mesh)
        new_normal = planar_direction(new_mesh)
        
        rot = compute_transformation(new_normal, og_normal)
        new_mesh.vertices = new_mesh.vertices @ rot.T
        
        # Final positioning
        max_y = np.max(new_mesh.vertices[:, 1])
        new_mesh.vertices[:, 1] -= max_y
        new_mesh = translate_mesh(new_mesh)
        
        # Simple export with minimal parameters
        new_mesh.export(
            output_path + '.obj',
            file_type='obj'
        )
        
        return True
        
    except Exception as e:
        logging.error(f"Error processing meshes: {str(e)}")
        return False

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    success = rotate_meshes('mug', 'kettle', 'output_kettle')
    print("Processing completed successfully" if success else "Processing failed")

