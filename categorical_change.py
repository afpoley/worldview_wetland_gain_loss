# Calculate categorical change between two land cover classifications.
# Notes: fp=year1, fp2=year2. output format: Y100Y2 i.e. 110012 class 11 changes into class 12
# Poley 2/1/2021
import rasterio
import rasterio.mask
import numpy as np


def open_raster(rst_fp):
    with rasterio.open(rst_fp) as src:
        src_meta = src.meta
        rst = src.read(1)
    return rst, src_meta


fp = 'D:\\Users\\afpoley\\Desktop\\USFWF_TEMP\\stClair\\change\\stClair2014_clip.tif'
fp2 = 'D:\\Users\\afpoley\\Desktop\\USFWF_TEMP\\stClair\\change\\stClair2019_clip.tif'
out_file = 'D:\\Users\\afpoley\\Desktop\\USFWF_TEMP\\stClair\\change\\stClair2014_2019_catChange.tif'

y1, meta = open_raster(fp)
y2, meta = open_raster(fp2)
change = (y1*1000) + y2
change = change.astype(np.float64)

# Reclassify non-change zones:
non_change = [1001, 2002, 3003, 4004, 5005, 6006, 7007, 8008, 9009, 10010, 11011, 12012, 13013, 14014, 15015, 16016,
              17017, 18018, 19019, 20020, 21021, 22022, 23023, 24024, 25025, 26026, 27027, 28028, 29029, 30030]

for n in non_change:
    change[change == n] = np.nan

# for n in non_change:
#     change[change >= 6000] = np.nan

change = change.astype(np.uint16)
meta.update({'dtype': 'uint16'})

with rasterio.open(out_file, "w", **meta) as dest:
    dest.write_band(1, change)

print('Finished: ' + str(out_file))
