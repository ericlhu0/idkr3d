import h5py

file_path = "/Users/eric/r3d/robosuite/robosuite/models/assets/demonstrations/ppmugr_real-12-02-2am/pick_place_mug.hdf5"
key_to_delete = "demo_8"

with h5py.File(file_path, 'r+') as hdf_file:
    # Navigate to the "data" group
    data_group = hdf_file['data']
    
    # Check if key to delete exists
    if key_to_delete in data_group:
        del data_group[key_to_delete]  # Delete the dataset/group
        print(f"{key_to_delete} has been deleted successfully.")
    else:
        print(f"{key_to_delete}  does not exist in the file.")
