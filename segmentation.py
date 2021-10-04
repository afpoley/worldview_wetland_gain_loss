# Segment image using scikit-learn segmentation (slic)
# Input: Directory to CVA tiles
# Output: Directory where segment tiles will be saved
# Poley 9/20/2021

import numpy as np
from skimage.segmentation import slic, quickshift
import rasterio
import glob
import gc


def open_raster(rst_fp):
    with rasterio.open(rst_fp) as src:
        src_meta = src.meta
        rst = src.read()
    return rst, src_meta


# File paths
# fp = r'D:\Users\afpoley\Desktop\erie2019_2020_mag_ang_GVI.tif'
# fp = 'D:\\Users\\afpoley\\Desktop\\USFWF_TEMP\\Erie\\wetland_gainloss\\cva_tiles\\'
fp = 'D:\\Users\\afpoley\\Desktop\\USFWF_TEMP\\stClair\\change\\wetlandGainLoss\\cva_tiles\\'
# out_fp = r'D:\Users\afpoley\Desktop\erie2019_2020_mag_ang_GVI_segment3.tif'
# out_fp = 'D:\\Users\\afpoley\\Desktop\\USFWF_TEMP\\Erie\\wetland_gainloss\\segment_tiles\\'
out_fp = 'D:\\Users\\afpoley\\Desktop\\USFWF_TEMP\\stClair\\change\\wetlandGainLoss\\segment_tiles\\'


#%%
images = glob.glob(fp + '*.tif')
images.sort()
for i in images:
    # Open image
    img, meta = open_raster(i)

    # prep file as array into correct format
    Gimg = np.moveaxis(img, [0, 1, 2], [2, 1, 0])

    #%%
    segments = slic(Gimg.astype(np.double), compactness=1, sigma=0, multichannel=True, convert2lab=False,
                    enforce_connectivity=False, min_size_factor=0, max_size_factor=3, slic_zero=False)

    # segments = quickshift(Gimg.astype(np.double), ratio=0, kernel_size=1, max_dist=10, return_tree=False, sigma=0, convert2lab=False)

    #%%
    intensityMask = np.ndarray(Gimg.shape)
    region_means = np.ndarray(Gimg.shape)
    numRegions = (np.unique(segments)).size

    for b in range(Gimg.shape[2]):
        band = Gimg[:, :, b]
        for regionIndex in range(numRegions):
            cur_region_mask = (segments == regionIndex)  # Pick out current region
            cur_region_mean = np.nanmean(band[cur_region_mask])  # Find median over that region
            intensityMask[:, :, b][cur_region_mask] = cur_region_mean  # Assigns to each pixel in that region, the corresponding mean value

    #%%
    intensityMask = np.dstack([intensityMask, segments])
    intensityMask = intensityMask.astype(np.float32)
    intensityMask = np.moveaxis(intensityMask, [0, 1, 2], [2, 1, 0])

    meta.update({
        'dtype': intensityMask.dtype,
        'count': intensityMask.shape[0]
    })

    out_file = out_fp + 'segment_tile_' + i.split('_')[-1]
    with rasterio.open(out_file, 'w', **meta) as dest:
        dest.write(intensityMask)

    print(out_file)
    gc.collect()

print('Finished')

