# colmap_sparse_recon
<img src="images/sfm_castle.png">

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
     `python colmap_sparse_recon_posed.py`. 
     You can download the triangulated sparse point cloud for DTU via [BaiduNetDisk](https://pan.baidu.com/s/1FOtDwFgo8CZzNn1_PTBjjw), Fetch Code: `3puk`

2. convert sparse points to sparse depth map
   `python colmap_sparse_to_depth.py`

## Visualization
1. Visualize the sparse points
   + Use COLMAP GUI --> File --> Import model --> Select the sparse folder which contains cameras, images and points3D files (.bin/.txt)

2. Visualize the sparse depthmap
   + `python visualize_sparse.py xxx.pfm`


 <table align="center">
  <tr>
    <td><img src="images/scan4_vid11.jpg" width="400" height="300"></td>
    <td><img src="images/scan4_sparse_points.png" width="400"></td>
  </tr>
  <tr>
    <td>RGB image</td>
    <td>structure-from-motion</td>
  </tr>  <tr>
    <td><img src="images/scan4_vid11_sparse_depth.jpg" width="400" height="300"></td>
    <td><img src="images/scan4_fused_ply.png" width="400"></td>
  </tr>
  <tr>
    <td>sparse depth map</td>
    <td>dense point cloud</td>
  </tr>
</table>

## Acknowledgement
   + The image set of [SceauxCastle](https://github.com/openMVG/ImageDataset_SceauxCastle) is provided by the author of OpenMVG.
