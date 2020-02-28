import sys
sys.path.append('../src')

import numpy as np
import pandas as pd
import geopandas as gpd
from Task3 import *
from handleTiff import *

"""An initial attempt at creating contours"""

class t4(change):

    def npgridcontour(self, arr):
        #Floor division of numpy array
        arr = np.where(arr != -999, arr//subset, arr) # floor division by subset
        arr = np.where(arr == -999, np.nan, arr) # remove -999s

        #print(arr)
        arr1 = arr.copy()
        arr1 = np.where(arr1, np.nan, np.nan)

        #Need to loop through array in both direction
        # along rows
        lastindex = (0, 0)
        for index, x in np.ndenumerate(arr):
            if arr[index] != arr[lastindex]:
                arr1[index] = x
                lastindex = index
            else:
                lastindex = index

        lastindex = (0,0)
        print(arr.shape)
        arrt = arr.T.copy()
        print(arrt.shape)
        arrt1 = arr1.T.copy()
        # down columns
        for index, x in np.ndenumerate(arrt): # issue relating to nd.enumerate on transposed array i think
            print(index, lastindex) # works on square arrays but not rectangle ones
            if arr[index] != arr[lastindex]:
                arrt1[index] = x
                lastindex = index
            else:
                lastindex = index

        contours = arr1.copy()
        print(contours)
        # for unique values in numpy array create list
        contourunique = np.unique(contours)

        contourval = (contourunique[np.logical_not(np.isnan(contourunique))])

        contourval = contourval.tolist()

        # create empty dataframe
        condf = pd.DataFrame(columns=['Height', 'Lon', 'Lat'])

        print(condf)

        print(contourval)
        for val in contourval:
            lon = []
            lat = []
            for index, x in np.ndenumerate(contours):
                if x == val:
                    lon.append(index[0])
                    lat.append(index[1])
            # add val, lon and lat to dataframe
            tempdf = pd.DataFrame([[val, lon, lat]], columns=['Height', 'Lon', 'Lat'])
            condf = condf.append(tempdf, ignore_index=True)


        print(condf)

        # use read tiff xOrigin etc to find the lat and lon rather than x and y of the array

        # could use window to find spatially subset if finding nearest on arrays to order list of points

        # struggling to find what format it needs to be in to become a gpd


if __name__ == '__main__':
    subset = 10

    arr = np.array([21, 25, 38, 40, 45, 666, 78, 79, 91, 99, 95, 60, 10, 46, 88, 99, -999, 4, 6, 8, 2, 1, -999, 6, 14]).reshape(5,5)
    #print(arr)
    filename = 'task3.tif'

    a = t4(filename)
    a.npgridcontour(arr)

    b = t4(filename)
    b.readTiff(filename, 3031)
    arr = b.data
    b.npgridcontour(arr)
