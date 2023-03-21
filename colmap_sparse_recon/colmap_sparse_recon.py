# Command-line Interface to structure-from-motion
# https://colmap.github.io/cli.html#example
# Date: 2021-05-16

import os

os.environ["CUDA_VISIBLE_DEVICES"]='1'

colmap_exe_path ="/mnt/A/qiyh/2021/3rd_party_lib/colmap-3.6/build/src/exe/colmap"
dataset_path = "/mnt/B/qiyh/tankandtemples/training/"

def colmap_sparse_recon(scan):
    colmap_feature_extractor(scan)
    colmap_exhaustive_matcher(scan)
    colmap_mapper(scan)
    colmap_image_undistorter(scan) # don't forget this
    #colmap_model_converter(scan)
    
    
def colmap_feature_extractor(scan):
    cmd = colmap_exe_path + ' feature_extractor '
    cmd = cmd + ' --database_path ' + '{}/database.db'.format(scan)
    cmd = cmd + ' --image_path ' + '{}/images '.format(scan)
    #cmd = cmd + ' --ImageReader.camera_model PINHOLE '
    #cmd = cmd + ' --ImageReader.single_camera 1 '
    #cmd = cmd + ' --SiftExtraction.max_num_features 10000 '
    print(cmd)
    os.system(cmd)


def colmap_exhaustive_matcher(scan):
    cmd = colmap_exe_path + ' exhaustive_matcher '
    cmd = cmd + ' --database_path ' + '{}/database.db'.format(scan)
    #cmd = cmd + ' --SiftMatching.guided_matching 1 '
    print(cmd)
    os.system(cmd)


def colmap_mapper(scan):
    sparse_path = os.path.join(scan, 'sparse')
    if not os.path.exists(sparse_path):
        os.mkdir(sparse_path)

    cmd = colmap_exe_path + ' mapper '
    cmd = cmd + ' --database_path ' + '{}/database.db'.format(scan)
    cmd = cmd + ' --image_path ' + '{}/images'.format(scan)
    cmd = cmd + ' --output_path ' + '{}/sparse'.format(scan)
    print(cmd)
    os.system(cmd)


def colmap_image_undistorter(scan):
    cmd = colmap_exe_path + ' image_undistorter '
    cmd = cmd + ' --image_path ' + '{}/images'.format(scan)
    cmd = cmd + ' --input_path ' + '{}/sparse/0'.format(scan)
    cmd = cmd + ' --output_path ' + '{}/dense'.format(scan)
    cmd = cmd + ' --output_type COLMAP '
    cmd = cmd + ' --max_image_size 2000 '
    print(cmd)
    os.system(cmd)
    

def colmap_model_converter(scan):
   cmd = colmap_exe_path + ' model_converter '
   cmd = cmd + ' --input_path ' + '{}/dense/sparse/'.format(scan)
   cmd = cmd + ' --output_path ' + '{}/dense/sparse/'.format(scan)
   cmd = cmd + ' --output_type TXT '
   print(cmd)
   os.system(cmd)


def colmap_to_mvsnet(scan):
    cmd = "python colmap2mvsnet.py "
    cmd = cmd + ' --dense_folder ' + ' {}/dense'.format(scan)
    cmd = cmd + ' --save_folder ' + scan.replace("training", "training_preproc")
    print(cmd)
    os.system(cmd)

def colmap_sfm2log(scan): # use for tanks and temples evaluation
    cmd = "python tanks/convert_to_logfile.py "
    cmd = cmd + ' {}/dense/sparse/'.format(scan) # filename
    cmd = cmd + ' {}/dense/sparse/{}.log'.format(scan, scan.split('/')[-1]) # logfile_out
    cmd = cmd + ' {}/dense/images/'.format(scan) # input_images
    cmd = cmd + ' COLMAP' # method
    cmd = cmd + ' jpg' # no dot(.) here
    print(cmd)
    os.system(cmd)


if __name__ == "__main__":
    # testlist = "./lists/tanks/intermediate.txt"   
    # with open(testlist) as f:
    #     scans = f.readlines()
    #     scans = [line.rstrip() for line in scans]
    
    scans = ["Barn", "Caterpillar", "Church", "Courthouse", "Ignatius", "Meetingroom", "Truck"]
    
    print("len of scans: {}".format(len(scans)))
    print("scans: {}".format(scans))

    for scan in scans:
        scan = os.path.join(dataset_path, scan)
        colmap_sparse_recon(scan)
        # colmap_to_mvsnet(scan)
        # colmap_model_converter(scan)
        # colmap_sfm2log(scan)

