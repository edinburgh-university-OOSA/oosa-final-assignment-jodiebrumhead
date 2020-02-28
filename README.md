# OOSA Assignment

###Respository name:  oosa-final-assignment-jodiebrumhead



## Getting Started

Clone the repository!

### Dependencies and packages

No dependencies other than standard python packages as are available on Geosciences linux cluster.

### File structure

The repository contains 2 sets of files. The python scripts in the *'src'* folder are those provided by Steve Hancock. More details can be founds on these scripts [here](https://github.com/edinburgh-university-OOSA/assignment_2020/blob/master/README.md).

The python scripts in the *'additions'* folder build upon the *'src'* scripts to batch process LVIS data and undertake further analysis. The detail in this README.md refers to these scripts.

### Command Line Interface (CLI)
The scripts in this repository make use of CLI's to allow users to alter the processing as required.

For further information about the optional arguments for each script use the command argument **-h**, i.e.
```bash
python3 Task1.py -h
```
## Script Details

### Task1.py

### Example Command
An example command to run this script is as below. Default values are set so the script will run successfully to produce a tiff output file of a DEM of a single flightline at 10m resolution.
```bash
python3 Task1.py
```
#### Usage

The Task1.py script utilises existing code (provided by Steve Hancock) to process a single LVIS flight line to a DEM of any chosen resolution. A command line parser (CLI) is utilised to allow the user to select LVIS file to input, resolution of output tiff and the option to test the script only processing a selection of the data available in a LVIS file.  

This script remains in the repository as simple standalone example of how to utilise the *'src'* scripts to process LVIS data for a single file into a tiff.

The script contains 2 classes. Firstly the class **indfile** which utilises the **lvisGround** class and the **lvisData** class via inheritance. This processed the h5 files to find the longitude, latitude and ground elevation.

```python
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
```
The second class contains in Task1.py is the class **packArray**. This utilises the longitude, latitude and ground elevation to arrays to create a 2D numpy array. While this script could use object and inheritance from class **indfile** it was decided against as the **packArray** class effectively converts points to raster format and therefore would likely be used for multiple purposes and inheriting would limit this.  

```python
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
```
#### Expected outputs
If the Task1.py script is run directly the expected input is a single .h5 file and the expected output a single .tif file. The script having found the ground elevation for each LVIS wave and then converted these points to a raster.

### Task1sparse.py

### Example Command
An example command to run this script is as below. Default values are set so the script will run successfully to produce a tiff output file of a DEM of a single flightline at 10m resolution.
```bash
python3 Task1sparse.py
```
#### Usage
This script is a RAM optimised version of Task1.py. It therefore allows subsetting of the data and also utilise a sparse array for storing the data in RAM. The following areas are the main differences from Task1.py. Firstly utilising bounds to limit the extend of processing and subsetting the processing to reduce RAM usage.

```python
elif pig == True:

    # find bounds
    b=lvisGround(filename,onlyBounds=True)
    subset = (len(self.lat))/70000 # splits files into approx 10 chunks dependent upon number of records

    pigbounds = [257.834821526081, -75.76906402888673, 282.2133984738954, -65.11822059831096]

    # create empty arrays to append to in loop
    x = np.empty(0)
    y = np.empty(0)
    z = np.empty(0)

    for i in len(subset):
        x0 = (i*((pigbounds[2]-pigbounds[0])))/subset+pigbounds[0]
        y0 = pigbounds[1]
        x1 = ((i+1)*((pigbounds[2]-pigbounds[0])))/subset+pigbounds[0]
        y1 = pigbounds[3]
        # read in bounds
        self.c=lvisGround(filename,minX=x0,minY=y0,maxX=x1,maxY=y1)

        self.c.setElevations()
        # find the ground
        self.c.estimateGround()
        self.c.dumpCoords()
        #self.zG is CofG
        self.c.reproject(inEPSG, outEPSG)

        x = np.append(x, self.c.lon)
        y = np.append(y, self.c.lat)
        z = np.append(z, self.c.zG)

    self.c.lon = x
    self.c.lat = y
    self.c.zG = z
```
When packing the array a sparse array is used. While this may have caused some issues with he data and needs reviewing, it reduced the RAM usage further and could be applied to other situations possibly with more success. The following code realates to this and the packing on the tiff line by line.
```python
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
```

N.B There where some last minute issues with GitHub repository and there fore the code may contain some small bugs and not run.
#### Expected outputs
If this script is run directly the same output as Task1.py is expected but having used significantly less RAM in the process.

### Task2.py

### Example Command
An example command to run this script is as below. Default values are set so the script will run successfully to produce a tiff output file of a gap filled DEM of 2009 at 100m resolution over the Pine Island Glacier area.
```bash
python3 Task2.py
```
#### Usage
This script can be called given a path to a directory containing .h5 files and all .h5 files within the directory will be processed to find ground elevation

 #### Expected outputs
 The output will be a gap-filled DEM in a single tiff file.
 the tiff line by line.

 The script primarily re-uses code form Task1sparse.py, however there are some additions for batch processing and interpolation. The batch process utilises the glob functionality to search the input directory fro relevant files. These are then batch processed through a loop appending to a new array.

 N.B I have just realised this might be why my values are high as I never rezero the arrays I append to in the loop! Moved in script but might be buggy!

 ```python
 fileList = glob(dir+'/*.h5') # search directory for files ending in .h5
 if testing2 is True:
     fileList = fileList[:3] # run on just 3 files to test

 outfilename = year + '.tif'

 # create empty arrays to append to in loop
 x = np.empty(0)
 y = np.empty(0)
 z = np.empty(0)

 # loop through each file in the list
 for infilename in fileList:
     print(infilename)

     # Extract details from path
     f=filenameregex()
     f.findfilename(infilename) # find file name within path
     f.finddeets()

     # Try except loop as some files may not be within bounds
     try:
         a=indfile(infilename, testing1, inEPSG, outEPSG, pig, res)
         print(f'{f.file} processed')

     except:
         print(f'{f.file} was not processed.')
         continue

     # Append relevant values to array
     x = np.append(x, a.c.lon)
     y = np.append(y, a.c.lat)
     z = np.append(z, a.c.zG)
```


### Task3.py

### Example Command
```bash
python3 Task3.py
```
Task 3 utilises Rasterio to clip the input tiffs to each others bounds. While this is not a perfect solution it is most efficient to utilise the packages available. The code is as expected for Rasterio. When run the aray sizes where out by one column. This was bodged to run but a more beautiful solution should be created ideally.


```python
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

```

### Task4.py

### Example Command
Upon running task 4 it will try to undertake two different contours. Firstly on a test 5 x 5 numpy array. This goes most of the way to providing contours by creating x and y coordinates for contours within the numpy array. Further improvement and development are needed to be fully functional. Secondly the elevation change tif produced by Task 3 is used as a test case with in the script. This soon finds that the np.ndenumerate struggles with indexing of proposed arrays. The class to create contours inherits from the Task 3 class which also inherits from handleTiff. This therefore allows many different methods to be called on the data from the same script, with little issue passing variables, due to the use of self.

```bash
python3 Task4.py
```

NB. the code for this script is not added to the read me as it is still in development. 
### Other Scripts
There are a number of other scripts which contain functions used by the main scripts. It is not intended that these scripts are run directly, if run directly most will run test cases on their functionality.
These are;
* filename.py - *used to garner useful information from the path and filename*
* bytesprint.py - *used to make number of bytes print in human readable format*
* interpolation.py - *contains function to gap fill 2D NumPy array, and further function to read tiff, gap fill and write tiff*
* mosaic.py - *function to utilise rasterio functionality to take a list of tiff files and mosaic before outputting as one new tiff file*

Details of the interpolation function are as below. I utilised np.ndenumerate which helped me to loop through all the pixels of the array, this was within a while loop so it ran until no null values remained. Care was taken to ensure the loops would not become infinite. I also took care to copy the array rather than reply on pointers to ensure the results were correct.
```python
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

```

## Contributing

No contributions needed

## Versioning

No versioning expected as of 27/02/2020

## Authors

* **Jodie Brumhead** - *Major contributor for 'additions' scripts*
* **Steve Hancock** - *Lecturer and contributor of 'src' scripts*


## Acknowledgments

* All in OOSA
* Demonstrators
