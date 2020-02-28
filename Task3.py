
import argparse
import sys
sys.path.append('../src')

import rasterio
from rasterio.plot import show
from rasterio.plot import show_hist
from rasterio.mask import mask
from shapely.geometry import box
import geopandas as gpd
from fiona.crs import from_epsg

from handleTiff import *
from filename import *


class change(tiffHandle):

    def getFeatures(gdf):
        """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
        import json
        return [json.loads(gdf.to_json())['features'][0]['geometry']]

    def bounds(self, epsg):

        """
        Find bounds tiff as polygon

        """
        bbox = box(self.xOrigin, self.yOrigin, self.xOrigin + (self.nX * self.pixelWidth), self.yOrigin + (self.nY * self.pixelHeight))

        geo = gpd.GeoDataFrame({'geometry': bbox}, index=[0], crs=from_epsg(epsg))

        self.coords = change.getFeatures(geo) # rasterio wants in json format


    def clip(self, fp, out_fp):
        data = rasterio.open(fp) # open tiff
        #show((data, 1), cmap='terrain')

        #Crop to new coords from above
        out_img, out_transform = mask(raster=data, shapes=self.coords, crop=True)

        #Deal with metadata
        out_meta = data.meta.copy()
        out_meta.update({"driver": "GTiff",
                        "height": out_img.shape[1],
                        "width": out_img.shape[2],
                        "transform": out_transform
                        })

        with rasterio.open(out_fp, "w", **out_meta) as dest:
            dest.write(out_img)

    def minus(self, first, second):
        # check shapes match would obviously need perfecting
        if first.data.shape[0] < second.data.shape[0]:
            second.data = np.delete(second.data, 1, 0)
        if first.data.shape[0] > second.data.shape[0]:
            print(2)
        if first.data.shape[1] < second.data.shape[1]:
            print(3)
        if first.data.shape[1] > second.data.shape[1]:
            print(4)

        #Do Array Math
        self.imageArr = second.data - first.data

        self.minX = first.xOrigin
        self.maxY = first.yOrigin # tiff coordinates different way round
        self.res = first.pixelWidth
        self.nX = first.nX
        self.nY = first.nY



def ap():

    # Argument parser to allow user to input values into script

    parser = argparse.ArgumentParser()

    parser.add_argument('-f1', '--file1input',
    default = '/home/s1891967/repos/Assignment/additions/2009_gf.tif',
    help='Input first (chronological) path and file you wish to process')

    parser.add_argument('-f2', '--file2input',
    default = '/home/s1891967/repos/Assignment/additions/2015_gf.tif',
    help='Input second path and file you wish to process')

    return parser.parse_args()

if __name__ == '__main__':

    args = ap()

    filename = [args.file1input, args.file2input]
    epsg = 3031

    t = filename[1].strip('.tif')
    out_fp1 = t + '_crop.tif'

    a = change(filename)

    a.readTiff(filename[0], epsg) # read a and find bounds
    a.bounds(epsg)
    a.clip(filename[1], out_fp1) # use bounds to clip b

    t = filename[0].strip('.tif')
    out_fp0 = t + '_crop.tif'

    a.readTiff(out_fp1, epsg) # repeat above other way round
    a.bounds(epsg)
    a.clip(filename[0], out_fp0)

    #Read cropped tiffs in to calculate change
    a.readTiff(out_fp0, epsg)
    b = change(filename)
    b.readTiff(out_fp1, epsg)

    change_fp = 'task3.tif'
    c = change(filename)

    c.minus(a, b) # calculate
    c.writeTiff(change_fp,epsg) # write out

    #Calculate total volume change over area
    # volume = area X depth
    print((c.imageArr.sum())*c.res**2)
