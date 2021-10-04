# This script performs the same function as ArcMap zonal statistics function.
# Input clump layer to be used as zone data and cva layer to compute mean of.
# Poley 2/1/2021
import os
import fiona
import glob
import rasterio
import rasterio.mask
import numpy as np


# def clip_raster(rst_fp, shp_path):
#     with fiona.open(shp_path, "r") as shp_src:
#         shp = [features["geometry"] for features in shp_src]
#
#     with rasterio.open(rst_fp) as src:
#         rst, rst_transform = rasterio.mask.mask(src, shp, crop=True)
#         rst = rst[0]
#         # rst = src.read(1)
#     return rst


def open_raster(rst_fp):
    with rasterio.open(rst_fp) as src:
        src_meta = src.meta
        rst = src.read(1)
    return rst, src_meta


def raster_stat(zones, rst, ids):
    poly_means = zones.astype(np.float64)
    for poly in ids:
        mask = zones
        mask = np.where(mask == poly, 1, 0)
        means = (mask*rst).astype(np.float64)
        means[means == 0] = np.nan
        means = np.nanmean(means).astype(np.float64)
        if poly == 1:
            means = 0
        # print(str(poly) + ': ' + str(means))
        poly_means[poly_means == poly] = means

    with rasterio.open(out_file, "w", **cva_meta) as dest:
        dest.write_band(1, poly_means)

    return poly_means


# Input file paths. Need CVA and clump tiles.
cva_fp = 'D:\\Users\\afpoley\\Desktop\\USFWF_TEMP\\stClair\\change\\tile_CVA_mag\\'
# shp_pth = 'Y:\\project\\USFWS\\change_analysis\\stClair\\AOI.shp' # uncomment this and first definition to clip raster
clump_fp = 'D:\\Users\\afpoley\\Desktop\\USFWF_TEMP\\stClair\\change\\tile_clumps\\'
out_fp = 'D:\\Users\\afpoley\\Desktop\\USFWF_TEMP\\stClair\\change\\tile_means_mag\\'


clump_ls = glob.glob(clump_fp + '*.tif')
cva_ls = glob.glob(cva_fp + '*.tif')
clump_ls.sort(reverse=True)
cva_ls.sort(reverse=True)


for n, (img, img2) in enumerate(zip(clump_ls, cva_ls), start=1):
    file_name = os.path.basename(img)
    out_file = out_fp + 'clump_mean_' + file_name.split('_')[-1]
    cva, cva_meta = open_raster(img2)
    clump, clump_meta = open_raster(img)
    IDs = np.unique(clump)
    x = raster_stat(clump, cva, IDs)

    print('File ' + str(n) + ' of ' + str(len(clump_ls)) + ' done')


