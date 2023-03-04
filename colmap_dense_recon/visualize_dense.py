import numpy as np
import cv2
import argparse

import matplotlib.pyplot as plt

#import sys
#sys.path.append("../datasets")
#from data_io import read_pfm#, write_depth_img
#from data_io_dmb import *

def read_pfm(filename):
    file = open(filename, 'rb')
    color = None
    width = None
    height = None
    scale = None
    endian = None

    header = file.readline().decode('utf-8').rstrip()
    if header == 'PF':
        color = True
    elif header == 'Pf':
        color = False
    else:
        raise Exception('Not a PFM file.')

    dim_match = re.match(r'^(\d+)\s(\d+)\s$', file.readline().decode('utf-8'))
    if dim_match:
        width, height = map(int, dim_match.groups())
    else:
        raise Exception('Malformed PFM header.')

    scale = float(file.readline().rstrip())
    if scale < 0:  # little-endian
        endian = '<'
        scale = -scale
    else:
        endian = '>'  # big-endian

    data = np.fromfile(file, endian + 'f')
    shape = (height, width, 3) if color else (height, width)

    data = np.reshape(data, shape)
    data = np.flipud(data)
    file.close()
    return data, scale


def write_depth_img(filename, depth_image):
    # Mask the array where equal to a given value
    ma = np.ma.masked_equal(depth_image, 0.0, copy=False)
    d_min = ma.min()
    d_max = ma.max()
    print("d_min: {}, d_max: {}".format(d_min, d_max))
    depth_n = 255.0 * (depth_image - d_min) / (d_max - d_min) # depth map normalize
    depth_n = depth_n.astype(np.uint8)
    out_depth_image = cv2.applyColorMap(depth_n, cv2.COLORMAP_JET) # applyColorMap
    cv2.imwrite(filename, out_depth_image)    


def write_depth_img_V2(filename, depth_image): # hard-coded for DTU
    d_min = 425.0
    d_max = 935.0
    depth_image[(depth_image < d_min) & (depth_image>0)] = d_min
    depth_image[depth_image > d_max] = d_max
    depth_n = 255.0 * (depth_image - d_min) / (d_max - d_min) # depth map normalize
    depth_n = depth_n.astype(np.uint8)
    out_depth_image = cv2.applyColorMap(depth_n, cv2.COLORMAP_JET) # applyColorMap
    out_depth_image[depth_image==0] = (255, 255, 255)
    cv2.imwrite(filename, out_depth_image)    


def read_array(path):
    with open(path, "rb") as fid:
        width, height, channels = np.genfromtxt(fid, delimiter="&", max_rows=1,
                                                usecols=(0, 1, 2), dtype=int)
        fid.seek(0)
        num_delimiter = 0
        byte = fid.read(1)
        while True:
            if byte == b"&":
                num_delimiter += 1
                if num_delimiter >= 3:
                    break
            byte = fid.read(1)
        array = np.fromfile(fid, np.float32)
    array = array.reshape((width, height, channels), order="F")
    return np.transpose(array, (1, 0, 2)).squeeze()


if __name__ == "__main__":
    # parse argument
    parser = argparse.ArgumentParser()
    parser.add_argument("depth_path")
    args = parser.parse_args()
    depth_path = args.depth_path
    print(depth_path)

    if depth_path.endswith('pfm'): # mvsnet format
        depth_map = read_pfm(depth_path)[0]
        print('depth shape: {}'.format(depth_map.shape))
        write_depth_img(depth_path.replace(".pfm", ".jpg"), depth_map)  
    elif depth_path.endswith('bin'): # colmap format
        depth_map = read_array(depth_path)
        print('depth shape: {}'.format(depth_map.shape))
        write_depth_img(depth_path.replace(".bin", ".jpg"), depth_map) 
    # elif depth_path.endswith('dmb'): # ACMH outputs
    #     depth_map = read_dmb(depth_path)
    #     cost_map = read_dmb(depth_path.replace("depths_geom.dmb", "costs.dmb"))
    #     print(cost_map.shape)
    #     #depth_map[cost_map > 0.5] = 0
    #     write_depth_img(depth_path.replace(".dmb", ".jpg"), depth_map) 
