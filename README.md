# OOSA Assignment

### oosa-final-assignment-jodiebrumhead



## Getting Started

Clone the repository!

### Dependencies and packages

No dependencies other than standard python packages as are available on Geosciences linux cluster.

## Task 1

### Usage

The Task1.py script utilises existing code (provided by Steve Hancock) to process a single LVIS flight line to a DEM of any chosen resolution. A command line parser (CLI) is utilised to allow the user to select LVIS file to input, resolution of output tiff and the option to test the script only processing a selection of the data available in a LVIS file.  


Task    1    (10%)    Use    the    starting    code    to    develop    a    script    capable    of    processing    a    single    LVIS    flight    line    to    a    DEM    of    any    chosen    resolution.    This    will    require    a    command    line    parser    to    provide    the    filename    and    the    resolution,    and    some    additional    methods    adding    to    the    scripts    provided.    Make    use    of    objects    and    inheritance    where    possible    to    make    the    code    easier    to    maintain.    
 Use    this    code    to    process    a    flight    line    of    your    choice    over    PIG    to    a    10    m    resolution    DEM    in    geotiff    format.    Include    that    geotiff    and    a    short    (<=    100    words)    discussion    of    any    interesting    features    in    your    report.    
 Include    a    description    of    the    code    developed    and    an    example    command    to    show    how    to    produce    your    DEM    in    your    repository’s    README.    


```bash
python3 Task1.py -f fileinput -r resolution -t testing
```

For further information about optional arguments for each package use the command argument -h, i.e.
```bash
python3 Task1.py -h
```

### Code Examples

#### Function to determine quartile of given value

```python
def quartfuncself(self, v):
    if min(self.quart['Wage']) < v < max(self.quart['Wage']):  # is the value valid for this dataset?
        for idx, row in self.quart.iterrows():  # for each row in the dataframe
            if v < row['Wage']:
                m1 = idx
                break
            if v > row['Wage']:
                m2 = idx
        return f'The value £{v} is between the {int(m2*100)}th percentile and the {int(m1*100)}th percentile'
    else:  # formatted strings to return
        return f'The value £{v} is outside the permitted range'
```

### Expected outputs

##### Random numbers sorted and threshold added through binary search
![algorithm.py output](20.png)

##### Function fitted to example wage and age data
![funcfit.py output](linePlot.png)

##### Histogram, probability density and quartiles for example wage data
![funcfit.py output](wageplot.png)

## Contributing

No contributions needed

## Versioning

No versioning expected

## Authors

* **Jodie Brumhead** - *Major contributor*
* **Steve Hancock** - *Lecturer*


## Acknowledgments

* All in OOSA
* Demonstrators
* The internet for giving me all the answers
