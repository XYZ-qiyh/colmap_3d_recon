import os
import sys
import numpy as np
from read_write_model import read_model, qvec2rotmat

import trimesh
import pyrender
import matplotlib.pyplot as plt

import cv2

def write_sparse_depth_img(filename, depth_image):
    d_min = 425.0
    d_max = 935.0
    depth_image[(depth_image < d_min) & (depth_image>0)] = d_min
    depth_image[depth_image > d_max] = d_max
    depth_n = 255.0 * (depth_image - d_min) / (d_max - d_min) # depth map normalize
    depth_n = depth_n.astype(np.uint8)
    out_depth_image = cv2.applyColorMap(depth_n, cv2.COLORMAP_JET) # applyColorMap
    out_depth_image[depth_image==0] = (255, 255, 255)
    # draw bounding box
    # print(depth_image.shape)
    #end_x, end_y = depth_image.shape[0], depth_image.shape[1]
    #print("end_x: {}, end_y: {}".format(end_x, end_y))
    #out_depth_image = cv2.rectangle(out_depth_image, (0, 0), (end_y-1, end_x-1), color = (0, 0, 0), thickness=1)
    
    cv2.imwrite(filename, out_depth_image)    


# save depth map as pfm file
# provided by MVSNet (Yao et al)
def save_pfm(filename, image, scale=1):
    file = open(filename, "wb")
    color = None

    image = np.flipud(image)

    if image.dtype.name != 'float32':
        raise Exception('Image dtype must be float32.')

    if len(image.shape) == 3 and image.shape[2] == 3:  # color image
        color = True
    elif len(image.shape) == 2 or len(image.shape) == 3 and image.shape[2] == 1:  # greyscale
        color = False
    else:
        raise Exception('Image must have H x W x 3, H x W x 1 or H x W dimensions.')

    file.write('PF\n'.encode('utf-8') if color else 'Pf\n'.encode('utf-8'))
    file.write('{} {}\n'.format(image.shape[1], image.shape[0]).encode('utf-8'))

    endian = image.dtype.byteorder

    if endian == '<' or endian == '=' and sys.byteorder == 'little':
        scale = -scale

    file.write(('%f\n' % scale).encode('utf-8'))

    image.tofile(file)
    file.close()

def pyrender_mesh_to_depth(scan_folder, mesh_path):
    cameras, images, points3D = read_model(path=scan_folder, ext='.bin')

    print('====================================')
    print('num_cameras: {}'.format(len(cameras)))
    print('num_images: {}'.format(len(images)))
    print('num_points3d: {}'.format(len(points3D)))
    print('====================================')

    # Load Mesh
    mesh = trimesh.load(mesh_path)
    pyrender_mesh = pyrender.Mesh.from_trimesh(mesh, smooth=False)

    scene = pyrender.Scene()
    scene.add(pyrender_mesh)
    renderer = pyrender.OffscreenRenderer(1600, 1200)


    for image_id, image in images.items():
        print("image_id: {}".format(image_id))
        #print("image info: {}".format(image))

        # 1. remove invisible points
        # xys_v = image.xys[image.point3D_ids > -1]
        # point3D_ids_v = image.point3D_ids[image.point3D_ids > -1]

        # # 2. get corresoponding 3D points
        # XYZ_world = []
        # for idx in point3D_ids_v:
        #     XYZ_world.append(points3D[idx].xyz)

        # XYZ_world = np.array(XYZ_world)

        # 3. [R|t] transform XYZ_world to XYZ_cam
        #    colmap pose: from world to camera
        # R = qvec2rotmat(image.qvec)
        # t = image.tvec
        # print("camera Rt: \n{}, {}".format(R, t))

        R = np.asmatrix(qvec2rotmat(image.qvec)).transpose()
        T = np.identity(4)
        T[0:3,0:3] = R
        T[0:3,3] = -R.dot(image.tvec)   # t = -R*C

        # Takes into account that colmap uses the computer vision
        # camera coordinate system (x = right, y = down, z = front)
        # while pyrender uses the computer graphics conventions
        # (x = right, y = up, -z = front).
        T[:, 1:3] *= -1

        # XYZ_cam = np.matmul(R, XYZ_world.transpose()) + t[:, np.newaxis]
        # XYZ_cam = XYZ_cam.transpose()

        # 4. get the depth value
        # depth_values = XYZ_cam[:, 2] # 3rd component

        # 5. project the 3d points to 2d pixel coordinate
        #    2D normalized + multiply the intrinsic matrix (K)
        # x_norm = XYZ_cam[:, 0] / XYZ_cam[:, 2]
        # y_norm = XYZ_cam[:, 1] / XYZ_cam[:, 2]
        params = cameras[image.camera_id].params
        assert len(params) == 4, "{}".format(params)
        #print("cam: {}".format(cameras[image.camera_id]))

        w = cameras[image.camera_id].width
        h = cameras[image.camera_id].height
        fx = params[0]
        fy = params[1]
        cx = params[2]
        cy = params[3]

        #print("dataset: {}".format(DATASET))
        #print("h: {}, w: {}".format(h, w))
        K = np.array([[fx, 0, cx],
                      [0, fy, cy],
                      [0, 0, 1]], dtype=np.float32)
        print("Camera K: \n {}".format(K))

        # Sets up the camera with the intrinsics and extrinsics.
        pyrender_camera = pyrender.IntrinsicsCamera(fx, fy, cx, cy,
                                                    zfar=800.0)
        cam_node = scene.add(pyrender_camera, pose=T)

        # render
        # depth rendering
        color, depth = renderer.render(scene)#, flags=flags
        print(depth.shape)
        print(depth.mean())
        scene.remove_node(cam_node)

        # if DATASET == "tanks":
        #     # resized image and cam params
        #     # for tanks and temples benchmark
        #     new_w = w//4
        #     new_h = 1056//4
        # elif DATASET == 'dtu':
        #     # for dtu dataset
        #     # crop for dtu, not resized
        #     new_w = 1600//4
        #     new_h = 1200//4
        # new_fx = fx * (new_w/w)
        # new_fy = fy * (new_h/h)
        # new_cx = cx * (new_w/w)
        # new_cy = cy * (new_h/h)

        # x_2d = x_norm * new_fx + new_cx
        # y_2d = y_norm * new_fy + new_cy

        # # save sparse depth map
        # depth_map = np.zeros((new_h, new_w), dtype=np.float32)
        # x_2d = np.round(x_2d).astype(np.int32)
        # y_2d = np.round(y_2d).astype(np.int32)

        # for x, y, z in zip(x_2d, y_2d, depth_values):
        #     if (x < 0) or (y < 0) or (x >= new_w) or (y >= new_h):
        #         continue

        #     depth_map[(y, x)] = z
            # print("depth: {}".format(z))

        # print("depth_map: {}".format(depth_map))

        '''save_pfm'''
        #out_filename = "{0:08d}".format(image_id-1) + "_sparse.pfm"
        out_filename = image.name.replace(".jpg", ".pfm").replace(".png", ".pfm")
        # out_dir = os.path.join(dataset_path, )
        out_dir = '{}/render_depth'.format(scan)
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)

        save_pfm(os.path.join(out_dir, out_filename), depth)
        out_filename = out_filename.replace(".pfm", ".png")

        write_sparse_depth_img(out_filename, depth)

        # report density
        print("pct: {:.2f}%".format(100*(depth>0).mean()))

        # break


if __name__ == "__main__":
    DATASET = "dtu"
    #DATASET = "tanks"
    
    if DATASET == "dtu":
        dataset_path = "/mnt/B/MVS_GT/dtu/"
        testlist = "./lists/dtu/test.txt"
    # elif DATASET == "tanks":
    #     dataset_path = "/mnt/B/MVS_GT/tankandtemples/intermediate/"
    #     testlist = "./lists/tanks/intermediate.txt"
        
   
    # with open(testlist) as f:
    #     scans = f.readlines()
    #     scans = [line.rstrip() for line in scans]

    scans = ["scan4"]

    print("len of scans: {}".format(len(scans)))
    print("scans: {}".format(scans))

    for scan in scans:
        # scan_folder = os.path.join(dataset_path, )
        scan_folder = '{}/sparse_colmap/triangulator/'.format(scan) # camera parameters
        # mesh_path = os.path.join(dataset_path, "Surface/{}_surf_trim.ply".format(scan))    # in mesh
        mesh_path = "E:/2021/20210723_实习分享/DTU_scan4/3_surface_trimmed.ply"

        print("scan_folder: {}".format(scan_folder))
        print("mesh_path: {}".format(mesh_path))

        pyrender_mesh_to_depth(scan_folder, mesh_path)
