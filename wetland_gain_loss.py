# Wetland gain, loss, and type change automation
# Inputs: segmented CVA, initial classification (reclassified see README for class info), output directory,
# output base filename (typically "locationYear1_year2"), magnitude threshold, and GVI lower and upper thresholds
# Poley 10/20/2021
import rasterio
from rasterio import mask
import geopandas as gpd
import numpy as np
import subprocess


def open_raster(rst_fp, band):
    with rasterio.open(rst_fp) as src:
        src_meta = src.meta
        crs = src.crs
        rst = src.read(band)
    return rst, src_meta


# Input files
fp_cva = r'D:\Users\afpoley\Desktop\USFWF_TEMP\stClair\change\wetlandGainLoss\stClair2014_2019_mag_ang_GVI_segmentation.tif'
fp_class = r'D:\Users\afpoley\Desktop\USFWF_TEMP\stClair\change\wetlandGainLoss\stClair2014_reclassification.tif'
fp_out = r'D:\Users\afpoley\Desktop\USFWF_TEMP\stClair\change\wetlandGainLoss'
out_base = 'stClair2014_2019'
change_mag = 120
GVI_upper = 300
GVI_lower = -100


# Open images (Expects images are the exact same # of rows/cols and same projection
classification, class_meta = open_raster(fp_class, 1)
cva_mag, cva_meta = open_raster(fp_cva, 1)
GVI, _ = open_raster(fp_cva, 3)


# threshold CVA to change=1 and no-change=0
# angle_threshold = np.where(cva_angle >= change_angle, 1, 0)
mag_threshold = np.where(cva_mag >= change_mag, 1, 0)
mag_threshold = mag_threshold.astype(np.int8)


# Wetland gain or loss. Reclassify GVI to gain(>0) or loss(<0)
GVI_threshold = GVI.astype(np.int32)
GVI_threshold[np.where((GVI_threshold > GVI_lower) & (GVI_threshold < GVI_upper))] = 0
GVI_threshold[np.where(GVI_threshold <= GVI_lower)] = -1
GVI_threshold[np.where(GVI_threshold >= GVI_upper)] = 1


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
wetland_change = mag_threshold * wetlands
wetland_gainLoss = GVI_threshold * wetland_change


# Reclassify to wetland gain & loss (for more info, refer to overview Gain/Loss powerpoint in project folder)
wetland_gainLoss[np.where(wetland_gainLoss == 12)] = 100                            # wetland change type
wetland_gainLoss[np.where((wetland_gainLoss > 0) & (wetland_gainLoss < 100))] = 1   # wetland gain
wetland_gainLoss[np.where(wetland_gainLoss == -12)] = 0                             # no change
wetland_gainLoss[np.where(wetland_gainLoss < 0)] = -1                               # wetland loss


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

