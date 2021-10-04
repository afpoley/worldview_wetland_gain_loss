# Mosaic image tiles into single image
# Poley 2/1/2021
import glob
import rasterio
from rasterio.merge import merge


def open_raster(rst_fp, files):
    src = rasterio.open(rst_fp)
    src_meta = src.meta
    files.append(src)
    return src_meta


# Input file path to image tiles
# fp = 'D:\\Users\\afpoley\\Desktop\\USFWF_TEMP\\Erie\\wetland_gainloss\\segment_tiles\\'
# out_fp = 'D:\\Users\\afpoley\\Desktop\\USFWF_TEMP\\Erie\\wetland_gainloss\\Erie2019_2020_mag_ang_TCG_segmentation.tif'

fp = 'D:\\Users\\afpoley\\Desktop\\USFWF_TEMP\\stClair\\change\\wetlandGainLoss\\segment_tiles\\'
out_fp = 'D:\\Users\\afpoley\\Desktop\\USFWF_TEMP\\stClair\\change\\wetlandGainLoss\\stClair2014_2019_mag_ang_TCG_segmentation.tif'


ls = glob.glob(fp + '*tif')
mosaic_ls = []

for file in ls:
    meta = open_raster(file, mosaic_ls)

mosaic, out_trans = merge(mosaic_ls, method='first', nodata=0)

# Copy the metadata
out_meta = meta.copy()
print(out_meta)

out_meta.update({'driver': 'GTiff',
                 'width': mosaic.shape[2],
                 'height': mosaic.shape[1],
                 'count': mosaic.shape[0],
                 'transform': out_trans,
                 'nodata': 0})

print(out_meta)

# Write the mosaic raster to disk
with rasterio.open(out_fp, "w", **out_meta) as dest:
    dest.write(mosaic)

print('done')
