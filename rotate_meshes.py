import numpy as np
import trimesh

def rotate_meshes(og_mesh_filename, new_mesh_filename):
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
    handle_mask = (radial_distances > mean_radius + 1.5 * radius_std) & height_mask
    handle_vertices = vertices[handle_mask]
    mug_centroid_3d = np.mean(body_vertices, axis=0)  # use body centroid (not full mug)
    handle_centroid_3d = np.mean(handle_vertices, axis=0)
    direction_3d = handle_centroid_3d - mug_centroid_3d
    planar_direction = np.array([direction_3d[0], direction_3d[1], 0])
    planar_direction = planar_direction / np.linalg.norm(planar_direction[:2])

    return planar_direction

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
  og_mesh = trimesh.load_mesh(og_mesh_filename + '.obj')
  new_mesh = trimesh.load_mesh(new_mesh_filename + '.obj')

  # translate the base of the object up so that the base starts at 0, 0
  new_mesh = translate_mesh(new_mesh)

  og_normal = planar_direction(og_mesh)
  new_normal = planar_direction(new_mesh)

  rot = compute_transformation(new_normal, og_normal)

  new_mesh.vertices = new_mesh.vertices.dot(rot.T)
  new_mesh.export(new_mesh_filename + 'Rotated.obj', file_type = 'obj')
  