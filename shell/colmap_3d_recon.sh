#!/bin/sh

# command line interface to run colmap reconstruction
# Link: https://colmap.github.io/cli.html#command-line-interface
# Author: XYZ-qiyh (2021-12-04)
# Another example: https://github.com/isl-org/TanksAndTemples/blob/master/python_toolbox/get_colmap_reconstruction.sh

EXE_PATH="/mnt/A/qiyh/2021/3rd_party_lib/colmap-3.6/build/src/exe/colmap"

export CUDA_VISIBLE_DEVICES=1

DATASET_PATH="/mnt/B/qiyh/tankandtemples/Family/"

#########################################
# feature extractor
#########################################
$EXE_PATH feature_extractor \
    --database_path $DATASET_PATH/database.db \
    --image_path $DATASET_PATH/images \
    #--ImageReader.camera_model SIMPLE_PINHOLE \
    #--ImageReader.single_camera 1 \
    #--SiftExtraction.max_num_features 32768

#########################################
# feature matching
#########################################
$EXE_PATH exhaustive_matcher \
    --database_path $DATASET_PATH/database.db \
    #--SiftMatching.guided_matching 1

#########################################
# Structure-from-Motion
#########################################
mkdir $DATASET_PATH/sparse

$EXE_PATH mapper \
    --database_path $DATASET_PATH/database.db \
    --image_path $DATASET_PATH/images \
    --output_path $DATASET_PATH/sparse

# model_converter [optional]
$EXE_PATH model_converter \
    --input_path $DATASET_PATH/sparse/0 \
    --output_path $DATASET_PATH/sparse/0 \
    --output_type TXT

#########################################
# images undistorting
#########################################
$EXE_PATH image_undistorter \
    --image_path $DATASET_PATH/images \
    --input_path $DATASET_PATH/sparse/0 \
    --output_path $DATASET_PATH/dense \
    --output_type COLMAP \
    --max_image_size 3200

#########################################
# Multi-view Stereo
#########################################
$EXE_PATH patch_match_stereo \
   --workspace_path $DATASET_PATH/dense \
   --workspace_format COLMAP \
   --PatchMatchStereo.geom_consistency true

#########################################
# Depth-map Fusion
#########################################
$EXE_PATH stereo_fusion \
   --workspace_path $DATASET_PATH/dense \
   --workspace_format COLMAP \
   --input_type geometric \
   --output_path $DATASET_PATH/dense/fused.ply

#########################################
# Poisson Surface Recon
#########################################
# $EXE_PATH poisson_mesher \
#     --input_path $DATASET_PATH/dense/fused.ply \
#     --output_path $DATASET_PATH/dense/meshed-poisson.ply

#########################################
# Delaunay Surface Recon
#########################################
# $EXE_PATH delaunay_mesher \
#     --input_path $DATASET_PATH/dense \
#     --output_path $DATASET_PATH/dense/meshed-delaunay.ply
