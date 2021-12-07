# Reconstruct sparse/dense model from known camera poses
# https://colmap.github.io/faq.html#reconstruct-sparse-dense-model-from-known-camera-poses
# Date: 2021-06-16
# Use for dense reconstruction of DTU dataset

import os
import numpy as np
import time

os.environ["CUDA_VISIBLE_DEVICES"]='2'
colmap_exe_path = "/mnt/A/qiyh/2021/3rd_party_lib/colmap-3.6/build/src/exe/colmap"

def colmap_image_undistorter(scan):
    cmd = colmap_exe_path + ' image_undistorter '
    cmd = cmd + ' --image_path ' + '{}/images'.format(scan)
    cmd = cmd + ' --input_path ' + '{}/sparse_colmap/triangulator'.format(scan)
    cmd = cmd + ' --output_path ' + '{}/dense_colmap'.format(scan)
    cmd = cmd + ' --output_type COLMAP '
    cmd = cmd + ' --max_image_size 2000 '
    print(cmd)
    os.system(cmd)


def colmap_patch_match_stereo(scan):
    cmd = colmap_exe_path + ' patch_match_stereo '
    cmd = cmd + ' --workspace_path ' + '{}/dense_colmap'.format(scan)
    cmd = cmd + ' --workspace_format COLMAP '
    cmd = cmd + ' --PatchMatchStereo.geom_consistency true '
    cmd = cmd + ' --PatchMatchStereo.depth_min 425 '
    cmd = cmd + ' --PatchMatchStereo.depth_max 935 '
    print(cmd)
    os.system(cmd)

    
def colmap_stereo_fusion(scan):
    cmd = colmap_exe_path + ' stereo_fusion '
    cmd = cmd + ' --workspace_path ' + '{}/dense_colmap'.format(scan)
    cmd = cmd + ' --workspace_format COLMAP '
    cmd = cmd + ' --input_type geometric '
    cmd = cmd + ' --output_path ' + '{}/dense_colmap/fused.ply'.format(scan)
    print(cmd)
    os.system(cmd)
    

if __name__ == "__main__":
    dataset_path = "/mnt/B/MVS_GT/dtu/"
    testlist = "./lists/dtu/test.txt"
   
    with open(testlist) as f:
        scans = f.readlines()
        scans = [line.rstrip() for line in scans]
        
    #scans = ["scan1"]
    #scans = scans[1:]
    print("len of scans: {}".format(len(scans)))
    print("scans: {}".format(scans))
    
    runtime = {}
    for scan in scans:
        scan = os.path.join(dataset_path, scan)
        # print(scan)
        
        start_t = time.time()
        colmap_image_undistorter(scan)
        end_t1 = time.time()
        colmap_patch_match_stereo(scan)
        end_t2 = time.time()
        colmap_stereo_fusion(scan) # pull request: view selection same as MVSNet(Yao et al)
        end_t3 = time.time()
        runtime[scan.split('/')[-1]] = [(end_t1-start_t), (end_t2-end_t1), (end_t3-end_t2)]
        # break
        
    print(runtime)
