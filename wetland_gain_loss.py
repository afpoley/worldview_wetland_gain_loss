# Wetland gain, loss, and type change automation
# Inputs: segmented CVA, initial classification (reclassified see README for class info), output directory,
# output base filename (typically "locationYear1_year2"), magnitude threshold, and TCG lower and upper thresholds
# Poley 10/20/2021
import rasterio
from rasterio import mask
import geopandas as gpd
import numpy as np
import subprocess
import gdal


def open_raster(rst_fp, band):
    with rasterio.open(rst_fp) as src:
        src_meta = src.meta
        crs = src.crs
        rst = src.read(band)
    return rst, src_meta


def aoi_extent(img):
    fp_shp = fp_out + '\\' + img.split('\\')[-1][:-4] + '.shp'
    cmd = f"gdaltindex -f geoJSON {fp_shp} {img}"
    subprocess.run(cmd)
    return fp_shp


def clip_raster(rst_fp, shp, ref_meta):
    with rasterio.open(rst_fp) as src:
        # convert AOI coordinates to image coordinates if different
        if src.crs != ref_meta['crs']:
            shp = shp.to_crs(src.crs)

        # clip image to AOI extent
        rst, rst_transform = rasterio.mask.mask(src, shp.geometry, crop=True)
        meta = src.meta

    # update metadata to new clip extent
    meta.update({"driver": "GTiff",
                 "height": rst.shape[1],
                 "width": rst.shape[2],
                 "transform": rst_transform,
                 "count": rst.shape[0]
                 })
    return rst, meta


# Input files
fp_cva = r'D:\Users\afpoley\Desktop\USFWF_TEMP\stClair\change\wetlandGainLoss\stClair2014_2019_mag_ang_TCG_segmentation.tif'
fp_class = r'D:\Users\afpoley\Desktop\USFWF_TEMP\stClair\change\wetlandGainLoss\stClair2014_reclassification.tif'
fp_out = r'D:\Users\afpoley\Desktop\USFWF_TEMP\stClair\change\wetlandGainLoss'
out_base = 'stClair2014_2019'
change_mag = 120
TCG_upper = 300
TCG_lower = -100


# Open images (Expects images are the exact same # of rows/cols and same projection
classification, class_meta = open_raster(fp_class, 1)
cva_mag, cva_meta = open_raster(fp_cva, 1)
TCG, _ = open_raster(fp_cva, 3)


# threshold CVA to change=1 and no-change=0
# angle_threshold = np.where(cva_angle >= change_angle, 1, 0)
angle_threshold = np.where(cva_mag >= change_mag, 1, 0)
angle_threshold = angle_threshold.astype(np.int8)


# Wetland gain or loss. Reclassify TCG to gain(>0) or loss(<0)
TCG_threshold = TCG.astype(np.int32)
TCG_threshold[np.where((TCG_threshold > TCG_lower) & (TCG_threshold < TCG_upper))] = 0
TCG_threshold[np.where(TCG_threshold <= TCG_lower)] = -1
TCG_threshold[np.where(TCG_threshold >= TCG_upper)] = 1


# reclassify classification to mask out non-wetland classes
wetlands = classification
wetlands = np.where(classification == 1, 0, classification)  # Urban
wetlands = np.where(wetlands == 2, 0, wetlands)  # Suburban
wetlands = np.where(wetlands == 3, 0, wetlands)  # Barren land
wetlands = np.where(wetlands == 4, 0, wetlands)  # Agriculture
wetlands = np.where(wetlands == 5, 0, wetlands)  # Grasslands
wetlands = np.where(wetlands == 6, 0, wetlands)  # Deciduous
wetlands = np.where(wetlands == 7, 0, wetlands)  # Evergreen
wetlands = np.where(wetlands == 8, 0, wetlands)  # Shrubs


# Apply threshold for wetland change
wetland_change = angle_threshold * wetlands
wetland_gainLoss = TCG_threshold * wetland_change


# Reclassify to wetland gain & loss
wetland_gainLoss[np.where(wetland_gainLoss == 12)] = 100
wetland_gainLoss[np.where((wetland_gainLoss > 0) & (wetland_gainLoss < 100))] = 1
wetland_gainLoss[np.where(wetland_gainLoss == -12)] = 0
wetland_gainLoss[np.where(wetland_gainLoss < 0)] = -1


# # Export wetland change/no-change image
# class_meta.update({"driver": "GTiff",
#                    "height": wetland_change.shape[0],
#                    "width": wetland_change.shape[1],
#                    "dtype": wetland_change.dtype}
#                   )
#
# outData = fp_out + '\\' + out_base + '_' + 'wetlandChange.tif'
# with rasterio.open(outData, "w", **class_meta) as dest:
#     dest.write_band(1, wetland_change)


#%%
# Export wetland gain & loss image
wetland_gainLoss = wetland_gainLoss.astype(np.int16)
class_meta.update({"driver": "GTiff",
                   "height": wetland_gainLoss.shape[0],
                   "width": wetland_gainLoss.shape[1],
                   "dtype": wetland_gainLoss.dtype}
                  )

outData2 = fp_out + '\\' + out_base + '_' + 'gainLoss.tif'
with rasterio.open(outData2, "w", **class_meta) as dest:
    dest.write_band(1, wetland_gainLoss)

