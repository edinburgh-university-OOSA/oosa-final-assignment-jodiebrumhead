import re

"""
Class to hold funtions to extract information from path and filename
"""

class filenameregex():

    def __init__(sel):
        '''
        Class initialiser
        Does nothing as this is only an example
        '''

    """Finds filename"""
    def findfilename(self, fileandpath):

        self.file = re.search(r"ILVIS1B_[A-Z]{2}\d{4}_\d{4}_R\d{4}_\d{6}", fileandpath) # finds where this pattern exists
        self.file = self.file.group()

    """Splits file name into parts"""
    def finddeets(self):

        self.place = self.file[8:10]
        self.yyyy = self.file[10:14]
        self.mm = self.file[15:17]
        self.dd = self.file[17:19]
        self.seconds = self.file[26:]


if __name__ == '__main__':

    """Calls to test functions work as expected"""

    fileandpath = '/geos/netdata/avtrain/data/3d/oosa/assignment/lvis/2015/ILVIS1B_AQ2015_1017_R1605_043439.h5'

    a=filenameregex()

    a.findfilename(fileandpath)

    a.finddeets()

    print(a.place, a.yyyy, a.mm, a.dd, a.seconds)
