# Produce hybrid categorical and radiometric land cover change.
# Inputs: Categorical change tiles, CVA tiles, csv of change thresholds (column1=change classes, column2=threshold)
# Poley 2/1/2021
import os
import glob
import rasterio
import numpy as np
from numpy import genfromtxt


def open_raster(rst_fp):
    with rasterio.open(rst_fp) as src:
        src_meta = src.meta
        rst = src.read(1)
    return rst, src_meta


# Inuput file paths
change_fp = 'D:\\Users\\afpoley\\Desktop\\USFWF_TEMP\\stClair\\change\\tile_change\\'
cva_fp = 'D:\\Users\\afpoley\\Desktop\\USFWF_TEMP\\stClair\\change\\tile_means\\'
threshold_fp = 'D:\\Users\\afpoley\\Desktop\\USFWF_TEMP\\stClair\\change\\change_thresholds.csv'
out_fp = 'D:\\Users\\afpoley\\Desktop\\USFWF_TEMP\\stClair\\change\\tile_hybrid\\'
out_file = 'hybrid_2014_2019_'


# Get list of image tiles
change_ls = glob.glob(change_fp + '*tif')
cva_ls = glob.glob(cva_fp + '*tif')
change_ls.sort(reverse=True)
cva_ls.sort(reverse=True)
csv = genfromtxt(threshold_fp, delimiter=',', skip_header=1)
csv = csv.astype(np.uint16)

changeID = csv[:, 0]
threshold = csv[:, 1]


# Calculate hybrid change
for img, (rst1, rst2) in enumerate(zip(change_ls, cva_ls), start=1):
    cva, meta = open_raster(rst2)
    change, meta = open_raster(rst1)
    shape = change.shape
    hybrid = np.zeros(shape)

    file_name = os.path.basename(rst1)
    out = out_fp + out_file + file_name.split('_')[-1]

    for (i, j) in zip(changeID, threshold):
        changeid = np.where(change == i, 1, 0)
        change_cva = cva * changeid
        change_cva = np.where(change_cva >= j, 1, 0)
        hybrid_temp = change_cva * change
        hybrid = hybrid + hybrid_temp

    hybrid = hybrid.astype(np.uint16)

    with rasterio.open(out, "w", **meta) as dest:
        dest.write_band(1, hybrid)

    print('File ' + str(img) + ' of ' + str(len(change_ls)) + ' done')

