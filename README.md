# colmap-sparse-recon
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
   + For Tanks and Temples 
     `python colmap_sparse_recon.py`

   + For DTU (images with known camera poses)
     `python colmap_sparse_recon_posed.py`

2. convert sparse points to sparse depth map
   `python colmap_sparse_to_depth.py`

## Visualize
 <table align="center">
  <tr>
    <td><img src="https://github.com/Todd-Qi/GMapping-ROS-Navigation/blob/master/map/lab-map.jpg" width="480" height="270"></td>
    <td><img src="https://github.com/Todd-Qi/GMapping-ROS-Navigation/blob/master/map/lab-2d-grid-map.png" width="480" height="270"></td>
  </tr>
  <tr>
    <td>laboratory environment</td>
    <td>2d grid map</td>
  </tr>
</table>
