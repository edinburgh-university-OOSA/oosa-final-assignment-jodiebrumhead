"""

"""

import argparse
import numpy as np
import resource
from timeit import default_timer as timer
import sys
sys.path.append('../src')



from processLVIS import *
from handleTiff import *
from filename import *
from bytesprint import *


"""Class to process and individual h5 lvis file to find ground level of each wave"""

class indfile():

    def __init__(self, filename, testing, inEPSG, outEPSG):
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

        else:
            self.c=lvisGround(filename)

        # set elevation
        self.c.setElevations()
        # find the ground
        self.c.estimateGround()
        #self.zG is CofG
        self.c.reproject(inEPSG, outEPSG) # work out how to do this ... which EPSGs do you need




class packArray():

    def __init__(self,data,x,y,res):

        '''

        Make array from points

        '''
        self.res = res
        # determine bounds
        self.minX=np.min(x)
        maxX=np.max(x)
        minY=np.min(y)
        self.maxY=np.max(y)

        # determine image size
        self.nX=int((maxX-self.minX)/self.res+1)
        self.nY=int((self.maxY-minY)/self.res+1)

        # pack in to array
        self.imageArr=np.full((self.nY,self.nX),-999, dtype=np.int16)
        # make an array of missing data flags
        # dtype=np.int16 reduces data usage - cant use unsigned due to negative vals over sea
        print(f'Image array bytes: {ps(self.imageArr.nbytes)}')

        self.xInds=np.array((x-self.minX)/self.res,dtype=int)  # determine which pixels the data lies in
        #print(self.xInds.nbytes)
        self.yInds=np.array((self.maxY-y)/self.res,dtype=int)  # determine which pixels the data lies in
        #print(self.yInds.nbytes)

        # this is a simple pack which will assign a single footprint to each pixel try to change this to find average?
        self.imageArr[self.yInds,self.xInds]=data
        print(f'Image array bytes: {ps(self.imageArr.nbytes)}')



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

    return parser.parse_args()


if __name__ == "__main__": # only run below if script called directly
    """Main Block"""

    start = timer()

    """Unpack argument parser"""
    args = ap()
    infilename = args.fileinput
    res = args.resolution
    testing = args.testing
    inEPSG = args.inputEPSG
    outEPSG = args.outputEPSG

    """Create output filename"""
    f=filenameregex()  # initialiser
    f.findfilename(infilename)  # call method to extract filename from path and .h5 extension
    outfilename = '/scratch/s1891967/' + f.file + ".tif"  # create out filename string


    a=indfile(infilename, testing, inEPSG, outEPSG)
    print('indfile done')

    aa=packArray(a.c.zG, a.c.lon, a.c.lat, res)
    print('arraypacked')

    aaa=tiffHandle(outfilename)
    tiffHandle.writeTiff(aa,outfilename,outEPSG)


    print(f'RAM usage: {ps((resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)*1000)}')
    end = timer()
    print(f'Time taken = {end-start}')
