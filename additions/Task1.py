import argparse
import numpy as np
import sys
sys.path.append('../src')
import resource


from processLVIS import *
from handleTiff import *
from filename import *

"""Class to process and individual h5 lvis file to find ground level of each wave"""

class indfile():

    def __init__(self, filename, testing, inEPSG, outEPSG):
        if testing == True:

            # find bounds
            b=lvisGround(filename,onlyBounds=True)
            # set some bounds
            x0=b.bounds[0]
            y0=b.bounds[1]
            x1=(b.bounds[2]-b.bounds[0])/15+b.bounds[0]
            y1=(b.bounds[3]-b.bounds[1])/15+b.bounds[1]
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
    #data = lvis.zG
    #lvis.lat
    def __init__(self,data,x,y,res):

        '''

        Make array from points

        '''
        self.res = res
        print(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        # determine bounds
        self.minX=np.min(x)
        maxX=np.max(x)
        minY=np.min(y)
        self.maxY=np.max(y)

        print(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)

        # determine image size
        self.nX=int((maxX-self.minX)/self.res+1)
        self.nY=int((self.maxY-minY)/self.res+1)
        print(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        # pack in to array
        self.imageArr=np.full((self.nY,self.nX),-999)        # make an array of missing data flags
        xInds=np.array((x-self.minX)/self.res,dtype=int)  # determine which pixels the data lies in
        yInds=np.array((self.maxY-y)/self.res,dtype=int)  # determine which pixels the data lies in

        print(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        # this is a simple pack which will assign a single footprint to each pixel try to change this to find average?

        self.imageArr[yInds,xInds]=data
        print(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)

class interpolate():
    pass




"""
Argparse functionality to select input file.
To process 1 file for Task 1
"""

def ap():

    # Argument parser to allow user to input values into script

    parser = argparse.ArgumentParser()

    parser.add_argument('-f', '--fileinput',
    default='/geos/netdata/avtrain/data/3d/oosa/assignment/lvis/2015/ILVIS1B_AQ2015_1017_R1605_043439.h5',
    help='Input path and file you wish to process')

    parser.add_argument('-r', '--resolution', default=10, type=int, help='Enter resolution(m) for output DEM (Default = 10m)')

    parser.add_argument('-i', '--inputEPSG', default=4326, type=int, help='Enter input coordinate system (Default = 4326)')

    parser.add_argument('-o', '--outputEPSG', default=3031, type=int, help='Enter output coordinate system (Default = 3031)')

    parser.add_argument('-t', '--testing', default=False, type=bool, help='Enter True to run test portion of file (Default = False)')

    return parser.parse_args()


if __name__ == "__main__":
    '''Main block'''

    args = ap()

    infilename = args.fileinput
    res = args.resolution
    testing = args.testing
    inEPSG = args.inputEPSG
    outEPSG = args.outputEPSG

    #inEPSG = 4326 # is it self describing data ?
    #outEPSG = 3031

    f=filenameregex()
    f.findfilename(infilename)
    f.finddeets()

    outfilename = f.file + ".tif"  # make this take file name from input filename


    a=indfile(infilename, testing, inEPSG, outEPSG)
    print('indfile done')
    aa=packArray(a.c.zG, a.c.lat, a.c.lon, res)
    print('arraypacked')
    aaa=tiffHandle(outfilename)

    tiffHandle.writeTiff(aa,outfilename,outEPSG)
