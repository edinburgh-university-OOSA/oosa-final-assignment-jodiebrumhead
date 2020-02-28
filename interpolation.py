import numpy as np
from timeit import default_timer as timer
import resource
import sys
sys.path.append('../src')
from handleTiff import *
from bytesprint import *

"""Function to fill gaps in a 2D NumPy array"""

def gapfill(arr, w, p):
    arr = np.where(arr == -999, np.nan, arr) # change -999 values to nan
    f=lambda a: (abs(a)+a)/2 # from stack exchange - returns negative values as 0
    i = 0
    n = 0

    while np.isnan(np.sum(arr)): # while any values in array are null
        # to stop while loop becoming infinate if no slices have required percentage of not nans
        if n == np.sum(np.isnan(arr)): # if number of nans same as last loop
            p = p+0.10 #decrease percentage needed to change
        i = i+1
        n = np.sum(np.isnan(arr)) # number of nans
        print(f'Loop no: {i}')
        print(f'Left to fill :{n}')
        copyarr = arr.copy()
        for index, x in np.ndenumerate(arr):
            #print(index, x)
            #print(f'{j}')
            if x == x: # intrinsic to np that nan != nan therefore this tests if value is nan
                pass # if not nan pass
            else: # if x is nan
                s = arr[int(f(index[0]-w)):index[0]+w+1,int(f(index[1]-w)):index[1]+w+1] # create slice of window around index
                #print(np.sum(np.isnan(s)), ((w+w+1)**2)*p)
                if np.sum(np.isnan(s)) > ((w+w+1)**2)*p: # check to see if the number of nan in window is more than specified percentage
                    pass
                else:
                    s = s[np.logical_not(np.isnan(s))] # remove nan and flatten
                    copyarr[index] = np.mean(s) # calculate mean and input into array
        arr = copyarr.copy()

    return arr # return array with filled values


"""Function to read tiff, interpolate and then write new tiff"""

def tiftotifgf(filename, outfilename, epsg, p):

        a = tiffHandle(filename)
        a.readTiff(filename,epsg)
        print(a.pixelWidth)

        w = int(1500/a.pixelWidth) # calculate window size based upon 1500m gap between some swaths and resolution

        a.imageArr = gapfill(a.data, w, p) # run inerpolation function

        print(f'RAM usage: {ps((resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)*1000)}') # print RAM usage

        # Reassign variable names from readTiff for writeTiff
        # Some improvements could be made to tiffHandle class to reduce need for this
        a.minX = a.xOrigin
        a.maxY = a.yOrigin # tiff coordinates different way round
        a.res = a.pixelWidth

        a.writeTiff(outfilename,epsg)



if __name__ == '__main__':

    #Test case pretend data
    arr = np.array([-999, 2, 3, 4, 5, 6, 7, -999, 9, -999, 5, 60, 10, 4, 8, 9, -999, 4, 6, 8, 2, 15, -999, 6, 14]).reshape(5,5)
    print(arr.sum())
    arr = gapfill(arr, 1, 0.5)
    print(arr.sum())

    # Test case small subsection of real data

    filename = '/home/s1891967/DO NOT DELETE/clipped.tif'

    percent = [0.1]
    epsg = 3031

    for p in percent:

        start = timer()
        outfilename = f'/home/s1891967/repos/Assignment/additions/percent{p}.tif'
        tiftotifgf(filename, outfilename, epsg, p)
        end = timer()
        print(end-start)
        print(f'{outfilename} test done')
