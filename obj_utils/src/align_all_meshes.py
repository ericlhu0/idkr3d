import numpy as np
import trimesh
import os
import align_meshes

## NOTE: The mug in "ref_mug" is the one used to crop out the handle as that one
## is the one that was translated so that its handle is also at y=0. Use that one
## when importing into blender to crop.

# read in the reference mesh of the original mug; this is the reference orientation
ref_mesh_path = "/home/eric/r3d/robosuite/robosuite/models/assets/objects/meshes/mug"


# the folder with all the raw generated objects
gen_folder_path = "/home/eric/r3d/gen_objects_sudoai/objswithtex"

# output path for aligned orientation objects
output_folder_path = "/home/eric/r3d/pleaseplease/"

obj_file_paths = []

obj_files_no_ext = [
    os.path.splitext(f)[0]
    for f in os.listdir(gen_folder_path)
    if f.lower().endswith('.obj')
]

for file in obj_files_no_ext:
  file_path = os.path.join(gen_folder_path, file)
  output_path = os.path.join(output_folder_path, file)
  obj_file_paths.append((file_path, output_path))

aligned_meshes = []

for file, output_path in obj_file_paths:
  print(file)  
  align_meshes.rotate_meshes(ref_mesh_path, file, output_path)

