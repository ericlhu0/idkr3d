import trimesh

# Load the mesh
mesh = trimesh.load('/Users/eric/Documents/r3d/robosuite/robosuite/models/assets/objects/meshes/mug_small.obj')

# Check and fix inconsistent normals
mesh.fix_normals()

# Export the fixed mesh
mesh.export('/Users/eric/Documents/r3d/robosuite/robosuite/models/assets/objects/meshes/mug_small.obj')

