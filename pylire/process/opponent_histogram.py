#!/usr/bin/env python
from __future__ import division

import math
import numpy
import struct
import base64

from pylire.process import external
from pylire.process.bitsampling import histogram_hash, histogram_hash_string

ROOT_2 = math.sqrt(2.0)
ROOT_3 = math.sqrt(3.0)
ROOT_6 = math.sqrt(6.0)

@numpy.vectorize
def opponent_histogram_scalar_keys(sR, sG, sB):
    """ Old method with scalar ops mixed in (exec time ~3.000s) """
    return \
        int(min(math.floor(((float((sR - sG) / ROOT_2) + 255.0 / ROOT_2) / (510.0 / ROOT_2)) * 4.0), 3.0)) + \
        int(min(math.floor(((float((sR + sG - 2 * sB) / ROOT_6) + 510.0 / ROOT_6) / (1020.0 / ROOT_6)) * 4.0), 3.0)) * 4 + \
        int(min(3.0, math.floor((float((sR + sG + sB) / ROOT_3) / (3.0 * 255.0 / ROOT_3)) * 4.0))) * 4 * 4

def opponent_histogram_key_vector_ORIG(sR, sG, sB):
    """ New method -- everything results in vector ops (exec time <0.076s) """
    # TAKE NOTE: `numpy.minimum(a)` behaves like `numpy.vectorize(__builtins__['min'])(a)`
    # ... which is DIFFERENT from `numpy.min(a)`, which acts like `min(list(a.flatten()))`
    # ... (the latter returns a scalar whereas the former returns an array shaped like `a`)
    return \
        (numpy.minimum(numpy.floor(
            ((((sR - sG) / ROOT_2) + 255.0 / ROOT_2).astype('float32') / (510.0 / ROOT_2)) * 4.0), 3.0)).astype('int') + \
        (numpy.minimum(numpy.floor(
            ((((sR + sG - 2 * sB) / ROOT_6).astype('float32') + 510.0 / ROOT_6) / (1020.0 / ROOT_6)) * 4.0), 3.0)).astype('int') * 4 + \
        (numpy.minimum(3.0, numpy.floor(
            (((sR + sG + sB) / ROOT_3).astype('float32') / (3.0 * 255.0 / ROOT_3)) * 4.0))).astype('int') * 4 * 4

TWOFIFTYFIVE_OVER_ROOT2 = 255.0 / ROOT_2
FIVETEN_OVER_ROOT2 = 510.0 / ROOT_2
FIVETEN_OVER_ROOT6 = 510.0 / ROOT_6
TENTWENTY_OVER_ROOT6 = 1020.0 / ROOT_6
THREE_TIMES_TWOFIFTYFIVE_OVER_ROOT3 = 3.0 * 255.0 / ROOT_3
FOURBYFOUR = 4 * 4

@external
def opponent_histogram_key_vector(sR, sG, sB):
    """ New method plus -- vector ops with inlined scalar values (exec time <0.072s) """
    return \
        (numpy.minimum(numpy.floor(
            ((((sR - sG) / ROOT_2) + TWOFIFTYFIVE_OVER_ROOT2).astype('float32') / FIVETEN_OVER_ROOT2) * 4.0), 3.0)).astype('int') + \
        (numpy.minimum(numpy.floor(
            ((((sR + sG - 2 * sB) / ROOT_6).astype('float32') + FIVETEN_OVER_ROOT6) / TENTWENTY_OVER_ROOT6) * 4.0), 3.0)).astype('int') * 4 + \
        (numpy.minimum(3.0, numpy.floor(
            (((sR + sG + sB) / ROOT_3).astype('float32') / THREE_TIMES_TWOFIFTYFIVE_OVER_ROOT3) * 4.0))).astype('int') * FOURBYFOUR

def histogram_count(keys, minlength=64):
    return numpy.bincount(
        keys.flatten(),
        minlength=minlength)

def histogram_normalize(histogram, scale=127.0):
    return numpy.floor(
        (histogram.astype('float32') / (numpy.max(histogram)).astype('float32')) * float(scale)
    ).astype('uint8')

def opponent_histogram(R, G, B):
    histogram_keys = opponent_histogram_key_vector(R, G, B)
    return histogram_normalize(
        histogram_count(
            histogram_keys))

def oh_str(histogram):
    return "ophist %d %s" % (
        len(histogram),
        " ".join(histogram.astype('str')))

def oh_bithash(histogram):
    return histogram_hash(
        histogram.astype('double'))

def oh_bithash_str(histogram):
    return histogram_hash_string(
        histogram.astype('double'))

def oh_base64(histogram):
    return base64.encodestring(
        "".join(
            [struct.pack('B', char) for char in histogram]
        )).replace('\n', '')

def main(pth):
    from pylire.compatibility.utils import test
    from pylire.process.channels import RGB
    from imread import imread
    
    (R, G, B) = RGB(imread(pth))
    
    '''@test
    def timetest_scalar(R, G, B):
        histogram_keys = opponent_histogram_scalar_keys(R, G, B)
        hh = histogram_normalize(
            histogram_count(
                histogram_keys))
        print "vectorized scalar func:"
        print "%s" % oh_str(h)
        print "binary hash:"
        print oh_bithash_str(h)
        print ""
    
    timetest_scalar(R, G, B)
    '''
    
    @test
    def timetest_vector(R, G, B):
        histogram_key_vec = opponent_histogram_key_vector_ORIG(R, G, B)
        hh = histogram_normalize(
            histogram_count(
                histogram_key_vec))
        
        print "pure-python vector func:"
        print "%s" % oh_str(hh)
        print "binary hash:"
        print oh_bithash_str(hh)
        print ""
        
        return hh
    
    timetest_vector(R, G, B)
    
    @test
    def timetest_vector(R, G, B):
        histogram_key_vec_inline = opponent_histogram_key_vector(R, G, B)
        hh = histogram_normalize(
            histogram_count(
                histogram_key_vec_inline))
        
        print "native (inlined and cythonized) vector func:"
        print "%s" % oh_str(hh)
        print "binary hash:"
        print oh_bithash_str(hh)
        print ""
        
    timetest_vector(R, G, B)
    
    
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
        
        print ""
        print ""
        print "IMAGE: %s" % basename(im_pth)
        main(im_pth)
