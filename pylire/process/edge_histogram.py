
from __future__ import division

import numpy
import math

from pylire.process.grayscale import YValue

THRESHOLD = 11
NUM_BLOCK = 1100
ROOT_2 = math.sqrt(2.0)

NO_EDGE = 0
VERTICAL_EDGE = 1
HORIZONTAL_EDGE = 2
NON_DIRECTIONAL_EDGE = 3
DIAGONAL_45_DEGREE_EDGE = 4
DIAGONAL_135_DEGREE_EDGE = 5

QUANT_TABLE = numpy.array([
    [0.010867, 0.057915, 0.099526, 0.144849, 0.195573, 0.260504, 0.358031, 0.530128],
    [0.012266, 0.069934, 0.125879, 0.182307, 0.243396, 0.314563, 0.411728, 0.564319],
    [0.004193, 0.025852, 0.046860, 0.068519, 0.093286, 0.123490, 0.161505, 0.228960],
    [0.004174, 0.025924, 0.046232, 0.067163, 0.089655, 0.115391, 0.151904, 0.217745],
    [0.006778, 0.051667, 0.108650, 0.166257, 0.224226, 0.285691, 0.356375, 0.450972],
], dtype="double")

EDGE_FILTER = numpy.matrix([
    [1.0, -1.0, 1.0, -1.0],
    [1.0, 1.0, -1.0, -1.0],
    [ROOT_2, 0.0, 0.0, -ROOT_2],
    [0.0, ROOT_2, -ROOT_2, 0.0],
    [2.0, -2.0, -2.0, 2.0],
], dtype="double")

def edge_histogram(ndim):
    if len(ndim.shape) == 2:
        R = G = B = ndim.astype('float32')
    elif len(ndim.shape) == 3:
        if ndim.shape[2] > 2:
            (R, G, B) = (channel.T.astype('float32') for channel in ndim.T[:3])
        else:
            R = G = B = ndim.T[0].T.astype('float32')
    else:
        raise ValueError(
            "Can't create opponent histogram from an image array with shape = %s" % str(
                ndim.shape))
    grayscale = YValue(R, G, B)
    (W, H) = grayscale.shape[:2]
    histo = numpy.zeros(80, dtype="double")
    #block_size = -1
    sub_local_index = 0
    block_edge_type = 0
    count_local = numpy.zeros(16, dtype="int")
    block_size = int(math.floor((int(math.sqrt((W * H) / NUM_BLOCK)) / 2.0) * 2)) or 2
    block_shift = block_size >> 1
    bs2 = float(block_size) * float(block_size)
    four_over = 4.0 / bs2
    
    for j in xrange(0, H - block_size, block_size):
        for i in xrange(0, W - block_size, block_size):
            sub_local_index = int((i << 2) / float(W)) + int((j << 2) / float(H))
            count_local[sub_local_index] += 1
            
            averages = numpy.array([
                four_over * numpy.sum(
                    grayscale[i:(block_shift-1)+i, j:(block_shift-1)+j],
                    dtype="double"),
                four_over * numpy.sum(
                    grayscale[block_shift+i:(block_size-1)+i, j:(block_shift-1)+j],
                    dtype="double"),
                four_over * numpy.sum(
                    grayscale[i:(block_shift-1)+i, block_shift+j:(block_size-1)+j],
                    dtype="double"),
                four_over * numpy.sum(
                    grayscale[block_shift+i:(block_size-1)+i, block_shift+j:(block_size-1)+j],
                    dtype="double")],
                dtype="double")
            threshold = float(THRESHOLD)
            strengths = numpy.zeros(5, dtype="double")
            
            block_edge_type = get_edge_feature(i, j, grayscale, block_size, four_over)
    
    