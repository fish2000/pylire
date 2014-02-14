
from __future__ import division, print_function

import numpy
import math
import struct
import base64

from pylire.process.grayscale import YValue
from pylire.process.bitsampling import histogram_hash, histogram_hash_string

THRESHOLD = 11.0
NUM_BLOCK = 1100.0
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

EDGE_FILTER = numpy.array([
    [1.0,    -1.0,     1.0,   -1.0],
    [1.0,     1.0,    -1.0,   -1.0],
    [ROOT_2,  0.0,     0.0,   -ROOT_2],
    [0.0,     ROOT_2, -ROOT_2, 0.0],
    [2.0,    -2.0,    -2.0,    2.0]],
dtype="double")

def edge_histogram(R, G, B):
    grayscale = YValue(R, G, B)
    (W, H) = grayscale.shape[:2]
    local_histo = numpy.zeros(80, dtype="double")
    sub_local_index = 0
    count_local = numpy.zeros(16, dtype="int")
    block_size = int(math.floor((math.sqrt((W * H) / NUM_BLOCK) / 2.0)) * 2) or 2
    block_shift = block_size >> 1
    bs2 = float(block_size)**2
    four_over = 4.0 / bs2
    
    for j in xrange(0, H - block_size, block_size):
        for i in xrange(0, W - block_size, block_size):
            sub_local_index = int((i << 2) / W) + (int((j << 2) / H) << 2)
            count_local[sub_local_index] += 1
            
            averages = [
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
                    dtype="double")]
            strengths = [0.0, 0.0, 0.0, 0.0, 0.0]
            
            for e in xrange(5):
                for k in xrange(4):
                    strengths[e] += averages[k] * EDGE_FILTER[e, k]
                strengths[e] = abs(strengths[e])
            
            # incrementally test through strengths,
            # determining which type of feature we have
            eMAX = strengths[0]
            edge_feature = VERTICAL_EDGE
            if strengths[1] > eMAX:
                eMAX = strengths[1]
                edge_feature = HORIZONTAL_EDGE
            if strengths[2] > eMAX:
                eMAX = strengths[2]
                edge_feature = DIAGONAL_45_DEGREE_EDGE
            if strengths[3] > eMAX:
                eMAX = strengths[3]
                edge_feature = DIAGONAL_135_DEGREE_EDGE
            if strengths[4] > eMAX:
                eMAX = strengths[4]
                edge_feature = NON_DIRECTIONAL_EDGE
            if eMAX < THRESHOLD:
                edge_feature = NO_EDGE
            
            # now that we have the feature,
            # use it to properly increment the histogram
            if edge_feature == NO_EDGE:
                pass
            elif edge_feature == VERTICAL_EDGE:
                local_histo[sub_local_index * 5] += 1
            elif edge_feature == HORIZONTAL_EDGE:
                local_histo[sub_local_index * 5 + 1] += 1
            elif edge_feature == DIAGONAL_45_DEGREE_EDGE:
                local_histo[sub_local_index * 5 + 2] += 1
            elif edge_feature == DIAGONAL_135_DEGREE_EDGE:
                local_histo[sub_local_index * 5 + 3] += 1
            elif edge_feature == NON_DIRECTIONAL_EDGE:
                local_histo[sub_local_index * 5 + 4] += 1
    
    for k in xrange(len(local_histo)):
        local_histo[k] /= count_local[int(k / 5)]
    
    histogram = numpy.zeros(80, dtype="int")
    for i in xrange(len(local_histo)):
        for j in xrange(8):
            histogram[i] = j
            quantval = (j < 7) \
                and (QUANT_TABLE[i % 5][j] + QUANT_TABLE[i % 5][j + 1]) / 2.0 \
                or 1.0
            if local_histo[i] <= quantval:
                break
    return histogram

def edge_histo_str(histogram):
    return "edgehistogram;%s" % " ".join(histogram.astype('str'))

def edge_histo_bithash(histogram):
    return histogram_hash(
        histogram.astype('double'))

def edge_histo_bithash_str(histogram):
    return histogram_hash_string(
        histogram.astype('double'))

def edge_histo_bytes(histogram):
    histobytes = numpy.zeros(
        int(histogram.shape[0] / 2),
        dtype='byte')
    for i in xrange(int(len(histogram) / 2)):
        histobytes[i] = ((
            histogram[i << 1].astype('int') << 4 | \
            histogram[(i << 1) + 1].astype('int')) - 128)
    return histobytes

def edge_histo_base64(histobytes):
    return base64.encodestring(
        "".join(
            [struct.pack('b', byte) for byte in histobytes]
        )).replace('\n', '')


def main():
    from pylire.compatibility.utils import test
    from pylire.process.channels import RGB
    from os.path import expanduser
    from imread import imread
    
    pth = expanduser('~/Downloads/5717314638_2340739e06_b.jpg')
    #pth = expanduser('~/Downloads/8411181216_b16bf74632_o.jpg')
    (R, G, B) = RGB(imread(pth))
    
    @test
    def timetest_naive_edge_histogram(R, G, B):
        return edge_histogram(R, G, B)
    
    edge_histo = timetest_naive_edge_histogram(R, G, B)
    
    print("naive Lire port (string rep):")
    print("%s" % edge_histo_str(edge_histo))
    print("")
    print("binary hash:")
    print(edge_histo_bithash_str(edge_histo))
    print("")
    print("base64-encoded byte rep:")
    print(edge_histo_base64(edge_histo_bytes(edge_histo)))
    print("")
    
if __name__ == '__main__':
    main()


