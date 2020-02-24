import argparse
import numpy as np
import sys
sys.path.append('../src')
import resource
from glob import glob
import os

from Task1sparse import indfile, packArray
from filename import *
from mosaic import mosaicTiffs
from interpolation import *




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
    default='2015',
    help='Input year you wish to process')

    parser.add_argument('-r', '--resolution', default=100, type=int, help='Enter resolution(m) for output DEM (Default = 10m)')

    parser.add_argument('-i', '--inputEPSG', default=4326, type=int, help='Enter input coordinate system (Default = 4326)')

    parser.add_argument('-o', '--outputEPSG', default=3031, type=int, help='Enter output coordinate system (Default = 3031)')

    parser.add_argument('-t1', '--testing1', default=False, type=bool, help='Enter True to run test portion of all files (Default = False)')

    parser.add_argument('-t2', '--testing2', default=False, type=bool, help='Enter True to run test number of files (Default = False)')

    parser.add_argument('-g', '--glacier', default=False, type=bool, help='Enter False to run area of all files, True to run area over Pine Island Glacier alone (Default = True)')

    return parser.parse_args()


if __name__ == "__main__":
    '''Main block'''

    args = ap()

    path = args.path
    year = args.year
    res = args.resolution
    testing1 = args.testing1
    testing2 = args.testing2
    inEPSG = args.inputEPSG
    outEPSG = args.outputEPSG
    pig = args.glacier

dir = path + year

fileList = glob(dir+'/*.h5')
if testing2 is True:
    fileList = fileList[:4]

outfilelist = []

for infilename in fileList:
    print(infilename)

    f=filenameregex()
    f.findfilename(infilename)
    f.finddeets()

    outfilename = f.file + ".tif"  # make this take file name from input filename

    try:
        a=indfile(infilename, testing1, inEPSG, outEPSG, pig)
        print(f'{f.file} processed')

        aa=packArray(a.c.zG, a.c.lon, a.c.lat, res, outfilename, outEPSG)
        print(f'{outfilename} created')
        outfilelist.append(outfilename)

    except:
        print(f'{f.file} was not processed.')
        continue


print('Merging tiffs....')
mergedname = year+'_merged.tif'
mosaicTiffs(outfilelist, mergedname)
print(f'Tiffs merged and output as {mergedname}')

print('Interpolating tif....')
gfname = year+'_gf.tif'
w = 50
p = 0.8
tiftotifgf(mergedname, gfname, outEPSG, w, p)
print(f'Tiff gap filled and output as {gfname}')
