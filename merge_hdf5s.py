import mimicgen.utils.file_utils as MG_FileUtils


MG_FileUtils.merge_all_hdf5(
        folder='/home/eric/r3d/core_datasets_all_temps',
        new_hdf5_path='/home/eric/r3d/datasets/1217_13_12_1000demos/demo.hdf5',
        delete_folder=False,
    )