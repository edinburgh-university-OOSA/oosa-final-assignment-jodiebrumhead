import argparse
import numpy as np
import sys
sys.path.append('../src')
import resource
from osgeo import gdal             # package for handling geotiff data
from osgeo import osr              # package for handling projection information
from gdal import Warp
import scipy
from timeit import default_timer as timer


from processLVIS import *
from handleTiff import *
from filename import *
from bytesprint import *



"""Class to process and individual h5 lvis file to find ground level of each wave"""

class indfile():

    def __init__(self, filename, testing, inEPSG, outEPSG, pig):
        if testing == True:

            # find bounds
            b=lvisGround(filename,onlyBounds=True)
            # set some bounds
            x0=b.bounds[0]
            y0=b.bounds[1]
            x1=(b.bounds[2]-b.bounds[0])/10+b.bounds[0]
            y1=(b.bounds[3]-b.bounds[1])/10+b.bounds[1]

            # read in bounds
            self.c=lvisGround(filename,minX=x0,minY=y0,maxX=x1,maxY=y1)

        elif pig == True:

            # find bounds
            b=lvisGround(filename,onlyBounds=True)
            #print(b.bounds)

            pigbounds = [257.834821526081, -75.76906402888673, 282.2133984738954, -65.11822059831096]

            x0 = pigbounds[0]
            y0 = pigbounds[1]
            x1 = pigbounds[2]
            y1 = pigbounds[3]
            # read in bounds
            self.c=lvisGround(filename,minX=x0,minY=y0,maxX=x1,maxY=y1)

        else:
            self.c=lvisGround(filename)
        # set elevation
        self.c.setElevations()
        # find the ground
        self.c.estimateGround()
        self.c.dumpCoords()
        #self.zG is CofG
        self.c.reproject(inEPSG, outEPSG) # work out how to do this ... which EPSGs do you need


class packArray():
    #data = lvis.zG
    #lvis.lat
    def __init__(self,z,x,y,res,filename,epsg):

        '''

        Make array from points

        '''
        self.res = res
        #print(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        # determine bounds
        self.minX=np.min(x)
        maxX=np.max(x)
        minY=np.min(y)
        self.maxY=np.max(y)



        # determine image size
        self.nX=int((maxX-self.minX)/self.res+1)
        self.nY=int((self.maxY-minY)/self.res+1)


        self.xInds=np.array((x-self.minX)/self.res,dtype=int)  # determine which pixels the data lies in
        self.yInds=np.array((self.maxY-y)/self.res,dtype=int)  # determine which pixels the data lies in


        data = scipy.sparse.csr_matrix((z,(self.yInds,self.xInds)),dtype=float)
        print(f'Sparse Array RAM:{ps(data.data.nbytes)}')

        # set geolocation information (note geotiffs count down from top edge in Y)
        geotransform = (self.minX, self.res, 0, self.maxY, 0, -1*self.res)

        # load data in to geotiff object
        dst_ds = gdal.GetDriverByName('GTiff').Create(filename, self.nX, self.nY, 1, gdal.GDT_Float32)

        dst_ds.SetGeoTransform(geotransform)    # specify coords
        srs = osr.SpatialReference()            # establish encoding
        srs.ImportFromEPSG(epsg)                # WGS84 lat/long
        dst_ds.SetProjection(srs.ExportToWkt()) # export coords to fill
        offset = 1
        dst_ds.GetRasterBand(1)

        for i in range(data.shape[0]):
            data_row = data[i,:].todense() # output row of sparse array as standard array
            data_row = np.where(data_row == 0, -999, data_row)
            # add line here to change 0s to -999? i.e. np.where ? or reclass like week 5?
            dst_ds.GetRasterBand(1).WriteArray(data_row,0,offset*i)
            dst_ds.GetRasterBand(1).SetNoDataValue(-999)
            dst_ds.FlushCache()
        print(f'Row bytes:{ps(data_row.nbytes)}')

        dst_ds = None





"""
Argparse functionality to select input file.
To process 1 file for Task 1
"""

def ap():

    # Argument parser to allow user to input values into script

    parser = argparse.ArgumentParser()

    parser.add_argument('-f', '--fileinput',
    default='/geos/netdata/avtrain/data/3d/oosa/assignment/lvis/2015/ILVIS1B_AQ2015_1017_R1605_061585.h5',
    help='Input path and file you wish to process')

    parser.add_argument('-r', '--resolution', default=10, type=int, help='Enter resolution(m) for output DEM (Default = 10m)')

    parser.add_argument('-i', '--inputEPSG', default=4326, type=int, help='Enter input coordinate system (Default = 4326)')

    parser.add_argument('-o', '--outputEPSG', default=3031, type=int, help='Enter output coordinate system (Default = 3031)')

    parser.add_argument('-t', '--testing', default=False, type=bool, help='Enter True to run test portion of file (Default = False)')

    parser.add_argument('-g', '--glacier', default=False, type=bool, help='Enter False to run area of all files, True to run area over Pine Island Glacier alone (Default = True)')

    return parser.parse_args()


if __name__ == "__main__":
    '''Main block'''

    start = timer()

    args = ap()

    infilename = args.fileinput
    res = args.resolution
    testing = args.testing
    inEPSG = args.inputEPSG
    outEPSG = args.outputEPSG
    pig = args.glacier

    #inEPSG = 4326 # is it self describing data ?
    #outEPSG = 3031

    f=filenameregex()
    f.findfilename(infilename)
    f.finddeets()

    outfilename = f.file + ".tif"  # make this take file name from input filename
    # add whether testing of not in here

    a=indfile(infilename, testing, inEPSG, outEPSG, pig)
    print(f'{f.file} processed')

    aa=packArray(a.c.zG, a.c.lon, a.c.lat, res, outfilename, outEPSG)
    print(f'{outfilename} created')

    print(f'RAM usage: {ps((resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)*1000)}')

    end = timer()
    print(end-start)
