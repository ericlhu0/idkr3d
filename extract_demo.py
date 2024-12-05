import h5py

# Original HDF5 file path
input_file = "/home/eric/r3d/datasets/pick_place_mug/overfit1_ppmug/demo.hdf5"

# New HDF5 file path
output_file = "extracted_key_file.h5"

# Key to extract
key_to_extract = "data/demo_0"

# Desired path in the new file
new_path_in_file = "data/demo_0"

# Open the original HDF5 file in read mode
with h5py.File(input_file, 'r') as original_file:
    # Check if the key exists
    if key_to_extract in original_file:
        # Access the dataset or group
        data = original_file[key_to_extract]
        print(original_file['data'].keys())
        input()
        
        # Open a new HDF5 file in write mode
        with h5py.File(output_file, 'w') as new_file:
            # Create any intermediate groups in the new path
            group_path = "/".join(new_path_in_file.split("/")[:-1])
            if group_path:
                new_file.require_group(group_path)
                
            # Copy the dataset or group to the specified path in the new file
            original_file.copy(key_to_extract, new_file, name=new_path_in_file)
        print(f"Key '{key_to_extract}' successfully extracted to '{new_path_in_file}' in '{output_file}'.")
    else:
        print(f"Key '{key_to_extract}' not found in the file.")