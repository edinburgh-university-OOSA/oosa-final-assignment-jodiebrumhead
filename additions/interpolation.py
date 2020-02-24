import numpy as np
import sys
sys.path.append('../src')
from handleTiff import *


def gapfill(arr, w, p):
    arr = np.where(arr < -998, np.nan, arr)
    f=lambda a: (abs(a)+a)/2

    while np.isnan(np.sum(arr)):

        for index, x in np.ndenumerate(arr):
            #print(index[0], index[1], x)
            if x == x:
                pass
            else:
                s = arr[int(f(index[0]-w)):index[0]+w+1,int(f(index[1]-w)):index[1]+w+1]
                if np.isnan(s).sum() > ((w+w+1)**2)//p: # check to see if the number of nan in window is more than specified percentage
                    pass
                else:
                    s = s[np.logical_not(np.isnan(s))] # remove nan and flatten
                    arr[index] = np.mean(s) # calculate mean and input into array
    return arr

def tiftotifgf(filename, outfilename, epsg, w, p):

        a = tiffHandle(filename)
        a.readTiff(filename,epsg)

        w = 10 # number of grid squares either side to create focal window from
        p = 0.75 # percentage of acceptable when calculating mean

        a.imageArr = gapfill(a.data, w, p)

        # Reassign variable names from readTiff for writeTiff
        # Some improvements could be made to tiffHandle class to reduce need for this
        a.minX = a.xOrigin
        a.maxY = a.yOrigin
        a.res = a.pixelWidth

        a.writeTiff(outfilename,epsg)



if __name__ == '__main__':

    #arr = np.array([-999, 2, 3, 4, 5, 6, 7, -999, 9, -999, 5, 60, 10, 4, 8, 9, -999, 4, 6, 8, 2, 15, -999, 6, 14]).reshape(5,5)
    #gapfill(arr, 1)


    filename = '/home/s1891967/repos/Assignment/additions/ILVIS1B_AQ2009_1020_R1408_061398.tif'

    outfilename = '/home/s1891967/repos/Assignment/additions/gapfill_test.tif'

    a = tiffHandle(filename)
    a.readTiff(filename,epsg=3031)

    w = 10 # number of grid squares either side to create focal window from
    p = 0.75 # percentage of acceptable when calculating mean

    a.imageArr = gapfill(a.data, w, p)

    # Reassign variable names from readTiff for writeTiff
    # Some improvements could be made to tiffHandle class to reduce need for this
    a.minX = a.xOrigin
    a.maxY = a.yOrigin
    a.res = a.pixelWidth


    a.writeTiff(outfilename,3031)
