# Calculate change vector analysis (CVA) for Worldview images.
# Exports change magnitude, angle, and tasseled cap greeness (TCG) as single 3-band image
# Inputs: year 1 & 2 worldview images, output directory, output filename
# Poley 9/16/2021
import rasterio
import rasterio.mask
import numpy as np


def open_raster(rst_fp):
    with rasterio.open(rst_fp) as src:
        src_meta = src.meta
        crs = src.crs
        rst = src.read()
    return rst, src_meta, crs


def dotproduct(v1, v2):
    return sum((a*b) for a, b in zip(v1, v2))


def length(v):
    return np.linalg.norm(v, axis=0)


def angle(v1, v2):
    return np.arccos(dotproduct(v1, v2) / (length(v1) * length(v2)))


# File paths. fp1=year 1, fp2=year 2
fp1 = r"Y:\gis_lab\project\USFWS\change_analysis\erie\clipped_wv\wv20190824_normalized.tif"
fp2 = r"Y:\gis_lab\project\USFWS\change_analysis\erie\clipped_wv\wv20200703_normalized.tif"
out_fp = r"Y:\gis_lab\project\USFWS\change_analysis\erie\CVA"
outName = 'erie2019_2020'


# Open data
wv, out_meta, out_crs = open_raster(fp1)
wv2, _, _ = open_raster(fp2)
wv1 = wv[0:8, :, :]
wv2 = wv2[0:8, :, :]


# Calculate magnitude and angle
wv1 = wv1.astype(np.float64)
wv2 = wv2.astype(np.float64)
CVA_angle = angle(wv1, wv2)
CVA_mag = np.sqrt(sum((wv1-wv2)**2)).astype(np.float64)


# Spectral indices
# WV bands: 0=coastal, 1=blue, 2=green, 3=yellow, 4=red, 5=red edge, 6=NIR1, 7=NIR2
# Tasseled cap green vegetation index (TC_GVI)
# Reference https://www.l3harrisgeospatial.com/docs/broadbandgreenness.html#Green5
GVI1 = -0.283 * wv1[1, :, :] - 0.660 * wv1[3, :, :] + 0.577 * wv1[4, :, :] + 0.388 + wv1[6, :, :]
GVI2 = -0.283 * wv2[1, :, :] - 0.660 * wv2[3, :, :] + 0.577 * wv2[4, :, :] + 0.388 + wv2[6, :, :]
dGVI = GVI2 - GVI1


# Copy and update output metadata
CVA_mag_meta = out_meta
CVA_ang_meta = out_meta
CVA_tc_gvi_meta = out_meta
CVA_mag_meta.update({'height': CVA_mag.shape[0], 'width': CVA_mag.shape[1], 'count': 1, 'dtype': np.float32})
CVA_ang_meta.update({'height': CVA_angle.shape[0], 'width': CVA_angle.shape[1], 'count': 1, 'dtype': np.float32})
CVA_tc_gvi_meta.update({'height': dGVI.shape[0], 'width': dGVI.shape[1], 'count': 1, 'dtype': np.float32})


# Export images (uncomment if you want to export each index as separate image)
# with rasterio.open(out_fp + '\\' + outName + '_mag.tif', "w", **CVA_mag_meta) as dest:
#     dest.write(CVA_mag, 1)
#
# with rasterio.open(out_fp + '\\' + outName + '_ang.tif', "w", **CVA_ang_meta) as dest:
#     dest.write(CVA_angle, 1)
#
# with rasterio.open(out_fp + '\\' + outName + '_GVI.tif', "w", **CVA_tc_gvi_meta) as dest:
#     dest.write(dTC_GVI, 1)

#%%
# Export image
stack = np.stack([CVA_mag, CVA_angle, dGVI])        # Add any additional indices here
stack = np.nan_to_num(stack, nan=-999)
stack = stack.astype(np.float32)

CVA_meta_all = CVA_mag_meta
CVA_meta_all.update({'height': stack.shape[1],
                     'width': stack.shape[2],
                     'count': stack.shape[0],
                     'nodata': -999,
                     'dtype': stack.dtype}
                    )

# Modify output extension to account for any new indices added to output
with rasterio.open(out_fp + '\\' + outName + '_mag_ang_GVI.tif', "w", **CVA_meta_all) as dest:
    dest.write(stack)

print('done')
