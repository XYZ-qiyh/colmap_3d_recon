# Reconstruct sparse/dense model from known camera poses
# https://colmap.github.io/faq.html#reconstruct-sparse-dense-model-from-known-camera-poses
# Date: 2021-05-21
# Use for sparse reconstruction of DTU dataset

# Increase number of matches / sparse 3D points
# https://colmap.github.io/faq.html#increase-number-of-matches-sparse-3d-points
# Date: 2021-06-09
# Increasing the number of sparse 3d points (Use DSP-SIFT features and enable guided mathching)

import os
import numpy as np

from python.read_write_model import * # use for write cameras&images.txt
from python.database_v2 import *

os.environ["CUDA_VISIBLE_DEVICES"]='2'
colmap_exe_path = "/mnt/A/qiyh/2021/3rd_party_lib/colmap-3.6/build/src/exe/colmap"


def check_database(scan):
    database_file = os.path.join(scan, "database.db")
    if os.path.exists(database_file):
        cmd = "rm {}".format(database_file)
        print(cmd)
        os.system(cmd)

# read camera file
# provided by MVSNet(Yao et al)
def read_cam_file(filename):
    with open(filename) as f:
        lines = f.readlines()
        lines = [line.rstrip() for line in lines]
    # extrinsics: line [1,5), 4x4 matrix
    extrinsics = np.fromstring(' '.join(lines[1:5]), dtype=np.float32, sep=' ').reshape((4, 4))
    # intrinsics: line [7-10), 3x3 matrix
    intrinsics = np.fromstring(' '.join(lines[7:10]), dtype=np.float32, sep=' ').reshape((3, 3))
    
    return intrinsics, extrinsics


def prepare_cameras(scan):        
    # camera intrinsics
    cameras = {}
    for vid in range(49): # dtu evaluation set
        cam_filename = os.path.join(scan, "cams", "{0:08}_cam.txt".format(vid))
        intrinsics, _ = read_cam_file(cam_filename)

        camera_id = vid + 1
        model = "PINHOLE"
        width = 1600
        height = 1200
        fx = float(intrinsics[0][0])
        fy = float(intrinsics[1][1])
        cx = float(intrinsics[0][2])
        cy = float(intrinsics[1][2])
        params = np.array([fx, fy, cx, cy])
        cameras[camera_id] = Camera(id=camera_id, model=model, width=width, height=height, params=params)
        
    # write cameras txt
    cameras_txt = os.path.join(scan, "sparse_colmap/manually_created", "cameras.txt")
    write_cameras_text(cameras, cameras_txt)


def prepare_images(scan, metas):        
    # camera extrinsics
    images = {}
    
    for _, meta in enumerate(metas): # unordered image sets
        #print(meta)
        image_id, image_name, camera_id = meta
        #print("image_id: {}, image_name: {}, camera_id: {}".format(image_id, image_name, camera_id))
        cam_filename = os.path.join(scan, "cams", image_name.replace(".jpg", "_cam.txt"))
        _, extrinsic = read_cam_file(cam_filename)
        R = extrinsic[:3, :3]
        t = extrinsic[:3, 3]
        qvec = rotmat2qvec(R)
        tvec = t
        xys = np.array([])
        point3D_ids = np.array([])
        images[image_id] = Image(id=image_id, qvec=qvec, tvec=tvec, camera_id=camera_id, name=image_name, 
                                 xys=xys, point3D_ids=point3D_ids)
                                 
    # write images txt
    images_txt = os.path.join(scan, "sparse_colmap/manually_created", "images.txt")
    write_images_text(images, images_txt)


def prepare_points3D(scan):
    points3D_txt = os.path.join(scan, "sparse_colmap/manually_created", "points3D.txt")
    if not os.path.exists(points3D_txt):
        f = open(points3D_txt, 'w')
        f.close()


# colmap sparse recon while camera posed is known
def colmap_feature_extractor(scan):
    cmd = colmap_exe_path + ' feature_extractor '
    cmd = cmd + ' --database_path ' + '{}/database.db'.format(scan)
    cmd = cmd + ' --image_path ' + '{}/images '.format(scan)
    # cmd = cmd + ' --SiftExtraction.estimate_affine_shape=true '
    # cmd = cmd + ' --SiftExtraction.domain_size_pooling=true '
    print(cmd)
    os.system(cmd)


def colmap_exhaustive_matcher(scan):
    cmd = colmap_exe_path + ' exhaustive_matcher '
    cmd = cmd + ' --database_path ' + '{}/database.db'.format(scan)
    # cmd = cmd + ' --SiftMatching.guided_matching=true'
    print(cmd)
    os.system(cmd)


def colmap_point_triangulator(scan):
    sparse_folder = os.path.join(scan, "sparse_colmap/triangulator")
    if not os.path.exists(sparse_folder):
        os.mkdir(sparse_folder)

    cmd = colmap_exe_path + ' point_triangulator '
    cmd = cmd + ' --database_path ' + '{}/database.db'.format(scan)
    cmd = cmd + ' --image_path ' + '{}/images '.format(scan)
    cmd = cmd + ' --input_path ' + '{}/sparse_colmap/manually_created'.format(scan)
    cmd = cmd + ' --output_path ' + '{}/sparse_colmap/triangulator'.format(scan)
    print(cmd)
    os.system(cmd)


if __name__ == "__main__":
    dataset_path = "/mnt/B/MVS_GT/dtu/"
    testlist = "./lists/dtu/test.txt"
   
    with open(testlist) as f:
        scans = f.readlines()
        scans = [line.rstrip() for line in scans]
        
    print("len of scans: {}".format(len(scans)))
    print("scans: {}".format(scans))


    for scan in scans:
        scan = os.path.join(dataset_path, scan)
        check_database(scan) # check whether the database.db file exists, remove it if exists
        
        # mkdir sparse folder
        sparse_folder = os.path.join(scan, "sparse_colmap")
        if not os.path.exists(sparse_folder):
            os.mkdir(sparse_folder)
          
        sparse_folder_1 = os.path.join(scan, "sparse_colmap/manually_created")
        if not os.path.exists(sparse_folder_1):
            os.mkdir(sparse_folder_1)            
            
        prepare_cameras(scan)
        prepare_points3D(scan)            

        colmap_feature_extractor(scan) # colmap feat extract give one camera params
     
        metas = update_cameras_in_dataset(scan)
        prepare_images(scan, metas)
        
        colmap_exhaustive_matcher(scan) # colmap feat match
        colmap_point_triangulator(scan) # colmap point triangulator
