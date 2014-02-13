#!/usr/bin/env python
from __future__ import print_function

import h5py
import numpy

from pylire.compatibility.utils import test
from os.path import join, dirname

# Best values for PHOG: 3000 results include > 80% true positives
# after re-ranking in the 1str 20 results
# Optimal for ColorLayout, 1000 hashed results should be fine
# and will include > 90% true positives after re-ranking 
# in the 1st 20 results.
# Dimensions should cover the maximum dimensions
# of descriptors used with bit sampling

NUM_FUNCTION_BUNDLES = 100
NUM_BITS = 12
NUM_DIMENSIONS = 640

BIT_HASHER_SHAPE = (
    NUM_FUNCTION_BUNDLES,
    NUM_BITS,
    NUM_DIMENSIONS)

BIT_HASHER_ID = u"0x%x%x%x" % BIT_HASHER_SHAPE

BIT_HASH_LUT = numpy.exp2(
    numpy.arange(32, dtype='double'))

BIT_BUCKET = join(
    dirname(__file__), 'bits')

BIT_STORE = h5py.File(
    join(BIT_BUCKET,
        'hash-functions.h5'),
    libver='latest')

BITSET = BIT_STORE.require_dataset(
    BIT_HASHER_ID,
    shape=BIT_HASHER_SHAPE,
    dtype='double', exact=True)

BITS = numpy.zeros(
    shape=BITSET.shape,
    dtype=BITSET.dtype)

BITSET.read_direct(BITS)

def _generate_shuffled_hasher():
    """ Populates a numpy array with random bit-sampling hash
        function seeds and writes it to a package-local HDF5 store. """
    BITSET.write_direct(
        numpy.random.random(size=BIT_HASHER_SHAPE) * 4.0 - 2.0)
    BITSET.read_direct(BITS)
    BIT_STORE.flush()

def int_to_hex(int_vector):
    """ Converts vector of integers to hex string. Adapted from:
    https://github.com/RedDevil7/groupimg/blob/master/v1/compute_hashes.py """
    return " ".join([hex(xx)[2:].zfill(2) for xx in int_vector])
    
def histogram_hash(histo):
    """ Get a 100-member 1-dimensional integer array with results from
        performing a bit-sampled hashing on a histogram of doubles.
        This is a totally un-optimized port of the logic from here:
    https://github.com/fish2000/lire/blob/master/src/main/java/net/semanticmetadata/lire/indexing/hashing/BitSampling.java """
    hashout = numpy.zeros(BITS.shape[0], dtype="int")
    for bundle_idx in xrange(BITS.shape[0]):
        for bit_idx in xrange(BITS.shape[1]):
            val = 0.0
            for dimension_idx in xrange(histo.shape[0]):
                val += BITS[bundle_idx, bit_idx, dimension_idx] * histo[dimension_idx]
            hashout[bundle_idx] += BIT_HASH_LUT[bit_idx] * int(val < 0)
    return hashout

def histogram_hash_string(histo):
    return int_to_hex(histogram_hash(histo).astype('int32'))

@test
def main():
    """ Display the hash function array (generating it if needed)
        
        WARNING: don't uncomment this unles you need to --
        the disk file has to stay consistent for your
        searches to make any sense.
    """
    #_generate_shuffled_hasher()
    
    print("""
*************************************************************************
    
    Uncomment the function call to _generate_shuffled_hasher() --
    above this message in the code -- 
    to regenerate the serialized bit-sampling hash function array
    that is cached on disk in process/bits/hash-functions.h5
    
    
    BIT SAMPLING TESTS:
    
    NUM_BITS = %s
    NUM_DIMENSIONS = %s
    NUM_FUNCTION_BUNDLES = %s
    
    len(BITS) = %s
    
    
    BITS[0, 0] = 
        
        %s
    
    
    
*************************************************************************
    """ % (
        NUM_BITS,
        NUM_DIMENSIONS,
        NUM_FUNCTION_BUNDLES,
        len(BITS),
        numpy.array2string(
            BITS[0, 0],
            max_line_width=40,
            precision=2,
            suppress_small=True).replace('\n', "\n\t")))


if __name__ == '__main__':
    main()