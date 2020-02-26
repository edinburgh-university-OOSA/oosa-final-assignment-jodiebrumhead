
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

        self.coords = change.getFeatures(geo)


    def clip(self, fp, out_fp):
        data = rasterio.open(fp)
        show((data, 1), cmap='terrain')

        out_img, out_transform = mask(raster=data, shapes=self.coords, crop=True)

        out_meta = data.meta.copy()

        out_meta.update({"driver": "GTiff",
                        "height": out_img.shape[1],
                        "width": out_img.shape[2],
                        "transform": out_transform
                        })

        with rasterio.open(out_tif, "w", **out_meta) as dest:
            dest.write(out_img)




def ap():

    # Argument parser to allow user to input values into script

    parser = argparse.ArgumentParser()

    parser.add_argument('-f1', '--file1input', help='Input first path and file you wish to process')

    parser.add_argument('-f2', '--file2input', help='Input first path and file you wish to process')

    return parser.parse_args()


if __name__ == '__main__':

    args = ap()

    filename = [args.file1input, args.file2input]
    epsg = 3031

    f=filenameregex()
    f.findfilename(filename[1])
    out_fp1 = f.file + '_crop.tif'

    a = change(filename)

    a.readTiff(filename[0], epsg)
    a.bounds(epsg)
    a.clip(filename[1], out_fp1)

    f=filenameregex()
    f.findfilename(filename[0])
    out_fp0 = f.file + '_crop.tif'

    a.readTiff(out_fp1, epsg)
    a.bounds(epsg)
    a.clip(filename[0], out_fp0)
