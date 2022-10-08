import os
import numpy as np
from python.read_write_model import *

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

def colmap_sparse_to_depth(scan_folder):
    cameras, images, points3D = read_model(path=scan_folder, ext='.bin')

    print('====================================')
    print('num_cameras: {}'.format(len(cameras)))
    print('num_images: {}'.format(len(images)))
    print('num_points3d: {}'.format(len(points3D)))
    print('====================================')

    for image_id, image in images.items():
        print("image_id: {}".format(image_id))
        #print("image info: {}".format(image))

        # 1. remove invisible points
        xys_v = image.xys[image.point3D_ids > -1]
        point3D_ids_v = image.point3D_ids[image.point3D_ids > -1]

        # 2. get corresoponding 3D points
        XYZ_world = []
        for idx in point3D_ids_v:
            XYZ_world.append(points3D[idx].xyz)

        XYZ_world = np.array(XYZ_world)

        # 3. [R|t] transform XYZ_world to XYZ_cam
        #    colmap pose: from world to camera
        R = qvec2rotmat(image.qvec)
        t = image.tvec

        XYZ_cam = np.matmul(R, XYZ_world.transpose()) + t[:, np.newaxis]
        XYZ_cam = XYZ_cam.transpose()

        # 4. get the depth value
        depth_values = XYZ_cam[:, 2] # 3rd component

        # 5. project the 3d points to 2d pixel coordinate
        #    2D normalized + multiply the intrinsic matrix (K)
        x_norm = XYZ_cam[:, 0] / XYZ_cam[:, 2]
        y_norm = XYZ_cam[:, 1] / XYZ_cam[:, 2]
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

        if DATASET == "tanks":
            # resized image and cam params
            # for tanks and temples benchmark
            new_w = w//4
            new_h = 1056//4
        elif DATASET == 'dtu':
            # for dtu dataset
            # crop for dtu, not resized
            new_w = 1600//4
            new_h = 1200//4
        new_fx = fx * (new_w/w)
        new_fy = fy * (new_h/h)
        new_cx = cx * (new_w/w)
        new_cy = cy * (new_h/h)

        x_2d = x_norm * new_fx + new_cx
        y_2d = y_norm * new_fy + new_cy

        # save sparse depth map
        depth_map = np.zeros((new_h, new_w), dtype=np.float32)
        x_2d = np.round(x_2d).astype(np.int32)
        y_2d = np.round(y_2d).astype(np.int32)

        for x, y, z in zip(x_2d, y_2d, depth_values):
            if (x < 0) or (y < 0) or (x >= new_w) or (y >= new_h):
                continue

            depth_map[(y, x)] = z
            # print("depth: {}".format(z))

        # print("depth_map: {}".format(depth_map))

        '''save_pfm'''
        #out_filename = "{0:08d}".format(image_id-1) + "_sparse.pfm"
        out_filename = image.name.replace(".jpg", ".pfm").replace(".png", ".pfm")
        out_dir = os.path.join(dataset_path, '{}/sparse_colmap/sparse_depth'.format(scan))
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)

        save_pfm(os.path.join(out_dir, out_filename), depth_map)

        # report density
        print("pct: {:.2f}%".format(100*(depth_map>0).mean()))


if __name__ == "__main__":
    DATASET = "dtu"
    #DATASET = "tanks"
    
    if DATASET == "dtu":
        dataset_path = "/mnt/B/MVS_GT/dtu/"
        testlist = "./lists/dtu/test.txt"
    elif DATASET == "tanks":
        dataset_path = "/mnt/B/MVS_GT/tankandtemples/intermediate/"
        testlist = "./lists/tanks/intermediate.txt"
        
   
    with open(testlist) as f:
        scans = f.readlines()
        scans = [line.rstrip() for line in scans]

    print("len of scans: {}".format(len(scans)))
    print("scans: {}".format(scans))


    for scan in scans:
        scan_folder = os.path.join(dataset_path, '{}/sparse_colmap/triangulator/'.format(scan))

        print("scan_folder: {}".format(scan_folder))

        colmap_sparse_to_depth(scan_folder)
