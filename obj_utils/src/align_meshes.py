import numpy as np
import trimesh

def rotate_meshes(og_mesh_filename, new_mesh_filename, output_path):
  """
  Reads these two meshes and creates a 3rd mesh that is 'new_mesh' with its orientation rotated to match 'og_mesh'
  The file name EXCLUDES the .obj

  Parameters:
    - og_mesh_filename: str - Name of the og_mesh file
    - new_mesh_filename: str - Name of the new_mesh file

  Returns:
    None
  """

  def translate_mesh(mesh):
    """
    Centers the mesh so that that base of the object is at 0, 0
    (Objects start with the center of the object at 0, 0)
    Assumes z axis movement

    Parameters:
      - mesh: mesh Obj

    Returns:
      - trans_mesh: mesh Obj
    """
    vertices = mesh.vertices
    z_coords = vertices[:, 2]
    z_min = np.min(z_coords)
    mesh.vertices[:, 2] = mesh.vertices[:, 2] - z_min

    return mesh

  def planar_direction(mesh):
    vertices = mesh.vertices
    z_coords = vertices[:, 2]
    z_min,z_max =np.min(z_coords), np.max(z_coords)
    height = z_max-z_min
    body_mask = (z_coords>z_min+ 0.1*height) & (z_coords<z_max-0.2*height) # top and bottom excluded
    body_vertices = vertices[body_mask]

    body_center_xy = np.mean(body_vertices[:, :2], axis=0)

    body_radial_distances = np.linalg.norm(body_vertices[:, :2] - body_center_xy, axis=1)
    mean_radius = np.mean(body_radial_distances)
    radius_std = np.std(body_radial_distances)

    radial_distances = np.linalg.norm(vertices[:, :2] - body_center_xy, axis=1)
    height_mask = (z_coords > z_min + 0.1 * height) & (z_coords < z_max - 0.2 * height)
    handle_mask = (radial_distances > mean_radius + 1.5 * radius_std) & height_mask & (vertices[:, 0] > 0) #added last boolean for handle detection; handle is on the positive x axis
    handle_vertices = vertices[handle_mask]
    mug_centroid_3d = np.mean(body_vertices, axis=0)  # use body centroid (not full mug)
    handle_centroid_3d = np.mean(handle_vertices, axis=0)
    direction_3d = handle_centroid_3d - mug_centroid_3d
    planar_direction = np.array([direction_3d[0], direction_3d[1], 0])
    planar_direction = planar_direction / np.linalg.norm(planar_direction[:2])

    return planar_direction
  
  def get_handle_centroid(mesh):
    vertices = mesh.vertices
    z_coords = vertices[:, 2]
    z_min,z_max =np.min(z_coords), np.max(z_coords)
    height = z_max-z_min
    body_mask = (z_coords>z_min+ 0.1*height) & (z_coords<z_max-0.2*height) # top and bottom excluded
    body_vertices = vertices[body_mask]

    body_center_xy = np.mean(body_vertices[:, :2], axis=0)

    body_radial_distances = np.linalg.norm(body_vertices[:, :2] - body_center_xy, axis=1)
    mean_radius = np.mean(body_radial_distances)
    radius_std = np.std(body_radial_distances)

    radial_distances = np.linalg.norm(vertices[:, :2] - body_center_xy, axis=1)
    height_mask = (z_coords > z_min + 0.1 * height) & (z_coords < z_max - 0.2 * height)
    handle_mask = (radial_distances > mean_radius + 1.5 * radius_std) & height_mask
    handle_vertices = vertices[handle_mask]
    handle_centroid_3d = np.mean(handle_vertices, axis=0)
    return handle_centroid_3d

  def compute_transformation(new_vec, og_vec):
    """
    Compute the transformation matrix from new_vec to og_vec
    """
    norm_new_vec = new_vec / np.linalg.norm(new_vec)
    norm_og_vec = og_vec / np.linalg.norm(og_vec)

    # find the axis of rotation
    axis = np.cross(norm_new_vec, norm_og_vec)
    axis = axis / np.linalg.norm(axis)
    a_x = axis[0]
    a_y = axis[1]
    a_z = axis[2]

    # angle of rotation in radians
    theta = np.arccos(np.dot(norm_new_vec, norm_og_vec))

    k = np.asarray([
      [0, -a_z, a_y],
      [a_z, 0, -a_x],
      [-a_y, a_x, 0]
    ])

    iden = np.eye(3)

    rot = iden + np.sin(theta)*k + (1 - np.cos(theta))*(np.dot(k, k))

    return rot
  
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


  og_mesh = trimesh.load_mesh(og_mesh_filename + '.obj')
  new_mesh = trimesh.load_mesh(new_mesh_filename + '.obj')

  # scale the new mesh to match the bounding box of the og mesh
  new_mesh = scale_mesh_to_match_bounding_box(new_mesh, og_mesh)

  # rotate mesh 90 degrees along x
  x_rot = trimesh.transformations.rotation_matrix(np.radians(90), [1, 0, 0])
  new_mesh.apply_transform(x_rot)

  # translate the base of the object up so that the base starts at 0, 0
  new_mesh = translate_mesh(new_mesh)

  og_normal = planar_direction(og_mesh)
  new_normal = planar_direction(new_mesh)

  rot = compute_transformation(new_normal, og_normal)

  new_mesh.vertices = new_mesh.vertices.dot(rot.T)

  ## THIS FAILS B/C HANDLE CENTROIDS ARE INCORRECT
  # translate the new mesh so that the handle centroids match
  # og_mesh_handle_centroid = get_handle_centroid(og_mesh)
  # new_mesh_handle_centroid = get_handle_centroid(new_mesh)
  # new_mesh.vertices += (og_mesh_handle_centroid - new_mesh_handle_centroid)

  # Translate the mesh so that the handle is at y = 0 to align for cropping
  max_y = new_mesh.vertices[np.argmax(new_mesh.vertices[:, 1]), 1]
  new_mesh.vertices[:, 1] -= max_y
  translate_mesh(new_mesh) ## put the base at z=0

  new_mesh.export(output_path + 'Rotated.obj', file_type='obj')
  

if __name__ == '__main__':
  rotate_meshes('mug', 'kettle')