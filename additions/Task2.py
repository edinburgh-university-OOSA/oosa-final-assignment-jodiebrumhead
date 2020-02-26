import argparse
import numpy as np
import sys
sys.path.append('../src')
import resource
from glob import glob
import os

import rasterio
from rasterio.plot import show
from rasterio.plot import show_hist
from rasterio.mask import mask
from shapely.geometry import box
import geopandas as gpd
from fiona.crs import from_epsg


from Task1sparse import indfile, packArray
from filename import *
from mosaic import mosaicTiffs
from interpolation import *

def getFeatures(gdf):
    """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
    import json
    return [json.loads(gdf.to_json())['features'][0]['geometry']]


""" Use Rasterio to clip outputs to smaller area for interpolation"""
def clip1(fp, epsg, out_fp):
    bbox = box(-1623462.32, -359576.8, -1550569.47, -149862.07)
    geo = gpd.GeoDataFrame({'geometry': bbox}, index=[0], crs=from_epsg(epsg))
    coords = getFeatures(geo)

    data = rasterio.open(fp)

    out_img, out_transform = mask(raster=data, shapes=coords, crop=True)

    out_meta = data.meta.copy()

    out_meta.update({"driver": "GTiff",
                    "height": out_img.shape[1],
                    "width": out_img.shape[2],
                    "transform": out_transform
                    })

    with rasterio.open(out_fp, "w", **out_meta) as dest:
        dest.write(out_img)

    return


"""
Argparse functionality to select inputs and options.
To process muliple files for Task 2
"""

def ap():

    # Argument parser to allow user to input values into script

    parser = argparse.ArgumentParser()

    parser.add_argument('-p', '--path',
    default='/geos/netdata/avtrain/data/3d/oosa/assignment/lvis/',
    help='Input path for files you wish to process')

    parser.add_argument('-y', '--year',
    default='2009',
    help='Input year you wish to process')

    parser.add_argument('-r', '--resolution', default=100, type=int, help='Enter resolution(m) for output DEM (Default = 10m)')

    parser.add_argument('-i', '--inputEPSG', default=4326, type=int, help='Enter input coordinate system (Default = 4326)')

    parser.add_argument('-o', '--outputEPSG', default=3031, type=int, help='Enter output coordinate system (Default = 3031)')

    parser.add_argument('-t1', '--testing1', default=False, type=bool, help='Enter True to run test portion of all files (Default = False)')

    parser.add_argument('-t2', '--testing2', default=False, type=bool, help='Enter True to run test number of files (Default = False)')

    parser.add_argument('-g', '--glacier', default=True, type=bool, help='Enter False to run area of all files, True to run area over Pine Island Glacier alone (Default = True)')

    return parser.parse_args()


if __name__ == "__main__":
    '''Main block'''

    args = ap()
    # Unpack argparse values

    path = args.path
    year = args.year
    res = args.resolution
    testing1 = args.testing1
    testing2 = args.testing2
    inEPSG = args.inputEPSG
    outEPSG = args.outputEPSG
    pig = args.glacier


dir = path + year

fileList = glob(dir+'/*.h5') # search directory for files ending in .h5
if testing2 is True:
    fileList = fileList[:3] # run on just 3 files to test

outfilelist = []

# create empty arrays to append to in loop
x = np.empty(0)
y = np.empty(0)
z = np.empty(0)

# loop through each file in the list
for infilename in fileList:
    print(infilename)

    # Extract details from path
    f=filenameregex()
    f.findfilename(infilename) # find file name within path
    f.finddeets()

    outfilename = year + ".tif"

    # Try except loop as some files may not be within bounds
    try:
        a=indfile(infilename, testing1, inEPSG, outEPSG, pig, res)
        print(f'{f.file} processed')

    except:
        print(f'{f.file} was not processed.')
        continue

    # Append relevant values to array
    x = np.append(x, a.c.lon)
    y = np.append(y, a.c.lat)
    z = np.append(z, a.c.zG)

# Pass new arrays to be packed into sparse array and output to tiff
aa=packArray(z, x, y, res, outfilename, outEPSG)
print(f'{outfilename} created')

# Clip file to make sure we are not inrpolating more than we need to
clip1(outfilename, outEPSG, out_fp)


# Interpolate clipped tiff
print('Interpolating tif....')
gfname = year+'_gf.tif'

tiftotifgf(out_fp, gfname, outEPSG, 0.40)
print(f'Tiff gap filled and output as {gfname}')
