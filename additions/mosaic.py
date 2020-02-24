import rasterio
from rasterio.merge import merge
from rasterio.plot import show



def mosaicTiffs(fileslist, out_fp):

    src_files = []

    for fp in fileslist:
        src = rasterio.open(fp)
        src_files.append(src)

    mosaic, out_trans = merge(src_files)

    out_meta = src.meta.copy()
    out_meta.update({"driver": "GTiff",
                    "height": mosaic.shape[1],
                    "width": mosaic.shape[2],
                    "transform": out_trans
                    })


    with rasterio.open(out_fp, "w", **out_meta) as dest:
        dest.write(mosaic)

if __name__ == '__main__':

    outfilelist = ['/home/s1891967/repos/Assignment/additions/ILVIS1B_AQ2009_1020_R1408_055102.tif','/home/s1891967/repos/Assignment/additions/ILVIS1B_AQ2009_1020_R1408_058456.tif']

    mosaicTiffs(outfilelist, 'merged.tif')
