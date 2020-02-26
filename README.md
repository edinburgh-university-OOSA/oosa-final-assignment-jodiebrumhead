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
This script is a RAM optimised version of Task1.py. It therefore allows subsetting of the data and also utilise a sparse array for storing the data in RAM. 

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


### Task3.py - might work?

### Other Scripts
There are a number of other scripts which contain functions used by the main scripts. It is not intended that these scripts are run directly, if run directly most will run test cases on their functionality.
These are;
* filename.py - *used to garner useful information from the path and filename* 
* bytesprint.py - *used to make number of bytes print in human readable format*
* interpolation.py - *contains function to gap fill 2D NumPy array, and further function to read tiff, gap fill and write tiff*
* mosaic.py - *function to utilise rasterio functionality to take a list of tiff files and mosaic before outputting as one new tiff file*



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

