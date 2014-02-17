#!/usr/bin/env python
from __future__ import division

import numpy
from imread import imread
from os.path import expanduser

from pylire.process.grayscale import ITU_R_601_2

CANNY_THRESHOLD_LOW = 60.0
CANNY_THRESHOLD_HIGH = 100.0
PHOG_BINS = 30

# Notes (from the Lire source):
# // used to quantize bins to [0, quantizationFactor]
# // Note that a quantization factor of 127d has better precision,
# but is not supported by the current serialization method.
QUANTIZATION_FACTOR = 15.0

# histogram_out = numpy.zeros(
#     PHOG_BINS + 4*PHOG_BINS + 4*4*PHOG_BINS,
#     dtype="uint8")
# histogram = numpy.zeros(
#     PHOG_BINS + 4*PHOG_BINS + 4*4*PHOG_BINS,
#     dtype="double")

def PHOG(R, G, B):
    gray = ITU_R_601_2(R, G, B)
    print(gray)
    print("")
    print("MAXIMUM GRAY: %s" % numpy.max(gray))
    print("")
    print("")



def main(pth):
    from pylire.compatibility.utils import test
    from pylire.process.channels import RGB
    from imread import imread
    
    (R, G, B) = RGB(imread(pth))
    
    @test
    def timetest_naive_PHOG(R, G, B):
        phog_histo = PHOG(R, G, B)
    
    timetest_naive_PHOG(R, G, B)

if __name__ == '__main__':
    
    from os.path import expanduser, basename, join
    from os import listdir
    
    im_directory = expanduser("~/Downloads")
    im_paths = map(
        lambda name: join(im_directory, name),
        filter(
            lambda name: name.lower().endswith('jpg'),
            listdir(im_directory)))
    
    for im_pth in im_paths:
        
        print("")
        print("")
        print("IMAGE: %s" % basename(im_pth))
        main(im_pth)


