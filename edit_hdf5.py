import h5py

file_path = "/home/eric/r3d/datasets/pick_place_mug/overfit1_ppmug/demo.hdf5"
key_to_delete = "demo_8"
key_to_keep = "demo_0"

with h5py.File(file_path, 'r+') as hdf_file:
    # Navigate to the "data" group
    data_group = hdf_file['data']
    
    # # Check if key to delete exists
    # while len(data_group.keys()) > 0:
    #     if key_to_delete in data_group:
    #         del data_group[key_to_delete]  # Delete the dataset/group
    #         print(f"{key_to_delete} has been deleted successfully.")
    #     else:
    #         print(f"{key_to_delete}  does not exist in the file.")

    # delete all keys except key_to_keep
    print(data_group.keys())
    input()
    keys_to_delete = [key for key in data_group.keys() if key != key_to_keep]
    print(data_group.keys())
    for key in keys_to_delete:
        del data_group[key]
        print(f"{key} has been deleted successfully.")
