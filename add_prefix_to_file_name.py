import os

# Define the folder path
folder_path = '/home/eric/r3d/core_datasets5/demo_src_pick_place_mug_task_base/tmp'

# Define the prefix
prefix = '5_'

# Loop through all files in the folder
for filename in os.listdir(folder_path):
    # Get the full path of the file
    old_file_path = os.path.join(folder_path, filename)

    # Check if it is a file (not a directory)
    if os.path.isfile(old_file_path):
        # Create the new filename
        new_file_path = os.path.join(folder_path, prefix + filename)

        # Rename the file
        os.rename(old_file_path, new_file_path)