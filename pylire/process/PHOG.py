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

histogram_out = numpy.zeros(
    PHOG_BINS + 4*PHOG_BINS + 4*4*PHOG_BINS,
    dtype="uint8")
histogram = numpy.zeros(
    PHOG_BINS + 4*PHOG_BINS + 4*4*PHOG_BINS,
    dtype="double")

def PHOG(original):
    (origW, origH) = original.shape[:2]
    gray = ITU_R_601_2(original)
    print(gray)
    




if __name__ == '__main__':
    pth = expanduser('~/Downloads/5717314638_2340739e06_b.jpg')
    ndim = imread(pth)
    (R, G, B) = (channel.T for channel in ndim.T)
    
    print histogram
    
    print ""
    
    print "ophist %d %s" % (
        len(histogram),
        " ".join(histogram.astype('str')))
    
    



