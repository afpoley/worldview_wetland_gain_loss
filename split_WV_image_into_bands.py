# Splits multi-band image into images for every band
# Poley 9-16-2021

import os
import rasterio


fp = ''
out_dir = ''


with rasterio.open(fp) as src:
    rst = src.read()
    meta = src.meta

    meta.update({'count': 1})

    for b in range(0, src.count):
        out_file = out_dir + '/' + os.path.splitext(os.path.basename(fp))[0] + '_b' + str(b+1) + ".tif"
        with rasterio.open(out_file, "w", **meta) as dest:
            dest.write_band(1, rst[b, :, :])

print("Finished")
