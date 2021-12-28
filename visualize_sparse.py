import numpy as np
import cv2
import argparse
import re


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


if __name__ == "__main__":
    # parse argument
    parser = argparse.ArgumentParser()
    parser.add_argument("depth_path")
    args = parser.parse_args()
    depth_path = args.depth_path
    
    # read_pfm 
    depth_map, _ = read_pfm(depth_path)
    print('depth shape: {}'.format(depth_map.shape))
    
    # gray2color
    write_sparse_depth_img(depth_path.replace(".pfm", ".jpg"), depth_map)
