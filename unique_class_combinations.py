# Get unique class combinations from categorical change. Used for CVA threshold csv
# Poley 2/1/21

import rasterio
import numpy as np


def open_raster(rst_fp):
    src = rasterio.open(rst_fp)
    img = src.read()
    return img


# Input file path to categorical change
fp = 'D:\\Users\\afpoley\\Desktop\\USFWF_TEMP\\stClair\\change\\stClair2014_2019_catChange.tif'
out = 'D:\\Users\\afpoley\\Desktop\\USFWF_TEMP\\stClair\\change\\change_thresholds.csv'

rst = open_raster(fp)
classes = np.unique(rst)
classes = classes.astype(int)
np.savetxt(out, classes, delimiter=',')

