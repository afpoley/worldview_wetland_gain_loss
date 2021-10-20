import os, shutil, glob, sys
from datetime import datetime as dt
from osgeo import gdal, ogr
from osgeo.gdalconst import *
from numpy import copy
import numpy as np

get_stats = 1
normalize = 1

# List of raster bands
bands = range(1, 9)

# Name of the file to use as reference
ref_file = 'wv07282018.tif'


#datatype = GDT_Float32
datatype = GDT_Int16

# Location of rasters of interest
rd = 'Y:\\gis_lab\\project\\USFWS\\data\\worldview\\greenbay\\'
# os.chdir(rd)
rasters = glob.glob('{}*wv*.tif'.format(rd))
print(rasters)

# Location of outputs
odir = 'Y:\\gis_lab\\project\\USFWS\\data\\worldview\\greenbay\\'
# odir = rd
if not os.path.exists(odir):
    os.mkdir(odir)

# Location of shapefile w/ the zones (would probably work w/ any OGR-supported vector)
shp = 'Y:\\gis_lab\\project\\USFWS\\data\\worldview\\greenbay\\PIF.shp'

# Location of output CSV
stats_csv = 'Y:\\gis_lab\\project\\USFWS\\data\\worldview\\greenbay\\pifs_stats.csv'

# Field/attribute in the shp to use for zonal summary
# NOT CURRENTLY USED
zone_field = 'pif'

# NoData value of the output layer
nodata_output = 0  # 65536

###############################################################################
### MAIN PROGRAM ###

# Temp directory
# temp_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'temp')
temp_dir = os.path.join(os.path.dirname(rd), 'temp')
if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
os.mkdir(temp_dir)

hdr = ['n', 'mean', 'std', 'min', 'max', 'sum']
hdr_ln = ','.join(['zone', 'band', 'filename'] + hdr)

start = dt.now()
nodata_val = 0
if get_stats:
    od = {}
    for raster in rasters:
        if raster not in (
                # 'wv_hessel_20160616_AOI.tif',
        ) and "wv" in raster:
            print(raster)

            # Get NoData value
            dfile = gdal.Open(raster)
            band1 = dfile.GetRasterBand(1)
            nodata_val = band1.GetNoDataValue()

            # # Get zones
            # ds = ogr.Open(shp)
            # daLayer = ds.GetLayer(0)a
            #
            # zones = []
            # for feature in daLayer:
            #     zones.append(feature.GetField(zone_field))

            rast = os.path.join(rd, raster)

            # Clip raster to zone
            clip_rast = '{}/clip_{}'.format(temp_dir,os.path.basename(raster))
            if not os.path.exists(clip_rast):
                cmd = (
                    'gdalwarp -q '
                    '-srcnodata {nodata_val} '
                    '-dstnodata {nodata_output} '
                    '-cutline {shp} -crop_to_cutline '
                    # '-cutline {shp} -cwhere "pif={zone}" -crop_to_cutline '
                    # '-co "COMPRESS=LZW" '
                    '{rast} {clip_rast}'
                ).format(**locals())

                #print cmd
                os.system(cmd)

            ds = gdal.Open(clip_rast,0)

            ### Get zonal stats ###
            for z, bnd in enumerate(bands):
                # zid = zone
                zid = '{}_{}'.format(bnd, os.path.basename(raster))
                if zid not in od:
                    od[zid] = {}
                od[zid] = {}

                band = ds.GetRasterBand(bnd)

                # GetStatistics returns: (min, max, mean, std)
                stats = band.GetStatistics(0, 1)
                n = band.GetHistogram(0, 9999999999, 1, True, False)[0]
                od[zid] = {
                    'raster': raster,
                    'band': bnd,
                    'min': stats[0],
                    'max': stats[1],
                    'mean': stats[2],
                    'std': stats[3],
                    'n': n,
                    'sum': n * stats[2]
                }

                band = None
        ds = None



    print('\n{}'.format(hdr_ln))

    cs_stuff = hdr_ln + '\n'
    for z in sorted(od):
        b = z.split('_')[0]
        fn = os.path.join(rd, '_'.join(z.split('_')[1:]))
        cs_stuff += ','.join(['"{}"'.format(z), b, '"{}"'.format(fn)] + [str(od[z][x]) for x in hdr]) + '\n'

    print(cs_stuff)

    with open(stats_csv, 'w') as f:
        f.write(cs_stuff)



else:
    od = {}
    print(stats_csv)
    with open(stats_csv, 'r') as f:
        lines = f.readlines()
        hdr_line = lines[0].replace('\n', '').split(',')
        print(hdr_line)
        for line in lines[1:]:
            ln = line.replace('\n', '').replace('\r', '').split(',')
            z = ln[0].replace('"', '')
            x = int(ln[1])
            od[z] = {x: float(ln[hdr_line.index(x)]) for x in hdr}
            od[z]['raster'] = ln[2].replace('"', '')


print(od)


"""
CREATE NORMALIZED RASTERS USING NUMPY
"""

if normalize:
    print('\n\nNORMALIZING')

    # register all of the GDAL drivers
    gdal.AllRegister()

    for fl in set([od[k]['raster'] for k in sorted(od)]):
        print(fl)
        outfl = os.path.join(odir, fl.replace('.tif', '_normalized.tif'))


        if os.path.basename(fl) == ref_file:
            shutil.copyfile(fl, outfl)
        elif not os.path.exists(outfl):
            # open the image
            inDs = gdal.Open(fl)
            if inDs is None:
                print('Could not open image file')
                sys.exit(1)

            # get some metadata to use as template for the outfile
            driver = inDs.GetDriver()
            band1 = inDs.GetRasterBand(1)
            rows = inDs.RasterYSize
            cols = inDs.RasterXSize

            outDs = driver.Create(
                outfl, cols, rows, len(bands), datatype,
                options=['COMPRESS=LZW', 'BIGTIFF=YES']
            )

            if outDs is None:
                print('Could not create output file - bad path?')
                sys.exit(1)

            for band in bands:
                print('\t{}'.format(band))
                k = '{}_{}'.format(band, os.path.basename(fl))
                # ref = od['{}_{}'.format(band,fl)]
                ref = od['{}_{}'.format(band, ref_file)]
                # m = od[k]['std']/ref['std']
                # q = od[k]['mean'] - (m * ref['mean'])

                oldData = inDs.GetRasterBand(band)
                rastData = oldData.ReadAsArray(0, 0, cols, rows)

                outBand = outDs.GetRasterBand(band)
                outData = copy(rastData.astype(np.float64))

                #######################
                # !!! DO MATH HERE !!!#
                #outData = outData*m + q
                outData = (outData - od[k]['min']) * (
                    (ref['max']-ref['min'])/(od[k]['max']-od[k]['min'])
                ) + ref['min']

                # write the data
                outBand.WriteArray(outData, 0, 0)

                # flush data to disk, set the NoData value and calculate stats
                outBand.FlushCache()
                nodata_val = 0
                outBand.SetNoDataValue(nodata_val)

            # georeference the image and set the projection
            outDs.SetMetadata(inDs.GetMetadata())
            outDs.SetGeoTransform(inDs.GetGeoTransform())
            outDs.SetProjection(inDs.GetProjection())

            del outData
            del outDs


print("\nTotal time elapsed: {}\n\n".format(dt.now() - start))
