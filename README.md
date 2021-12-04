# colmap_sparse_recon
<img src="figure/figure1_sfm.png">

Sturcture-from-Motion using [COLMAP](https://colmap.github.io/index.html)

* input: unordered images
* outputs: the pose estimates for registered images and the reconstructed scene structure as a set of points

## How to use
0. prepare data and build colmap
   + [Download data](https://github.com/YoYo000/MVSNet#download) preprocessed by MVSNet (Yao et al.)
   + Build [colmap](https://github.com/colmap/colmap/tree/3.6) (we use version 3.6)
   + modify the `dataset_path`, `colmap_exe_path` in `colmap_sparse_recon.py` and `colmap_sparse_recon_posed.py`

1. sparse recon using colmap
   + For Tanks and Temples training set
     `python colmap_sparse_recon.py`

   + For DTU (images with known camera poses)
     `python colmap_sparse_recon_posed.py`

2. convert sparse points to sparse depth map
   `python colmap_sparse_to_depth.py`

## Visualize
1. Visualize the sparse points
   + Use COLMAP GUI --> File --> Import model --> Select the sparse folder which contains cameras, images and points3D files (.bin/.txt)

2. Visualize the sparse depthmap
   + `python visualize_sparse.py xxx.pfm`

 <table align="center">
  <tr>
    <td><img width=640 height=520 src="https://github.com/XYZ-qiyh/colmap-sparse-recon/blob/main/figure/figure2_sfm_result.png"></td>
  </tr>
  <tr>
    <td>The result of sparse reconstruction</td>
  </tr>
</table>

 <table align="center">
  <tr>
    <td><img src="https://github.com/XYZ-qiyh/colmap-sparse-recon/blob/main/figure/figure3_rgb.jpg" width="400" height="300"></td>
    <td><img src="https://github.com/XYZ-qiyh/colmap-sparse-recon/blob/main/figure/figure4_sparse.jpg" width="400" height="300"></td>
  </tr>
  <tr>
    <td>RGB image</td>
    <td>sparse depth map</td>
  </tr>
</table>

## Acknowledgement
   + The image set of [SceauxCastle](https://github.com/openMVG/ImageDataset_SceauxCastle) is provided by the author of OpenMVG.
