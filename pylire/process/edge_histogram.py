
from __future__ import division
from __future__ import print_function

import numpy
import math
import struct
import base64

from pylire.process.grayscale import YValue
from pylire.process.bitsampling import histogram_hash, histogram_hash_string

THRESHOLD = 11
NUM_BLOCK = 1100
ROOT_2 = math.sqrt(2.0)

NO_EDGE = 0
VERTICAL_EDGE = 1
HORIZONTAL_EDGE = 2
NON_DIRECTIONAL_EDGE = 3
DIAGONAL_45_DEGREE_EDGE = 4
DIAGONAL_135_DEGREE_EDGE = 5

# We have appended the '2.0' values to the end of this table ...
QUANT_TABLE = numpy.array([
    [0.010867, 0.057915, 0.099526, 0.144849, 0.195573, 0.260504, 0.358031, 0.530128, 2.0],
    [0.012266, 0.069934, 0.125879, 0.182307, 0.243396, 0.314563, 0.411728, 0.564319, 2.0],
    [0.004193, 0.025852, 0.046860, 0.068519, 0.093286, 0.123490, 0.161505, 0.228960, 2.0],
    [0.004174, 0.025924, 0.046232, 0.067163, 0.089655, 0.115391, 0.151904, 0.217745, 2.0],
    [0.006778, 0.051667, 0.108650, 0.166257, 0.224226, 0.285691, 0.356375, 0.450972, 2.0],
], dtype="double")

# Here we average the QUANT_TABLE values, between each pair of row elements,
# computed column-wise (thus only iterating across one array dimension) --
quant_averages = numpy.ones((8, 5), dtype="double")
for idx in xrange(QUANT_TABLE.shape[1]-1):
    quant_averages[idx] = numpy.minimum(
        numpy.average(QUANT_TABLE[:, idx:idx+2], axis=1),
        quant_averages[idx])

# -- such that the array of averaged values need only be transposed to yield
# an array whose indices correspond to quantized histogram values. fuck yes!
QUANTIZERS = quant_averages.T

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
    a = int(math.sqrt((W * H) / NUM_BLOCK))
    block_size = int(math.floor(float(a) / 2.0) * 2) or 2
    block_shift = block_size >> 1
    almost_block_size = block_size - 1
    almost_block_shift = block_shift - 1
    bs2 = float(block_size)**2
    four_over = 4.0 / bs2
    
    local_histo = numpy.zeros((16, 5), dtype="double")
    count_local = numpy.zeros(16, dtype="double")
    sub_local_index = 0
    edge_feature = 0
    
    for j in xrange(0, (H - block_size), block_size):
        for i in xrange(0, (W - block_size), block_size):
            sub_local_index = int((i << 2) / float(W)) + \
                             (int((j << 2) / float(H)) << 2)
            count_local[sub_local_index] += 1.0
            
            averages = [
                four_over * numpy.sum(
                    grayscale[
                        i:almost_block_shift+i,
                        j:almost_block_shift+j],
                    dtype="double"),
                four_over * numpy.sum(
                    grayscale[
                        block_shift+i:almost_block_size+i,
                        j:almost_block_shift+j],
                    dtype="double"),
                four_over * numpy.sum(
                    grayscale[
                        i:almost_block_shift+i,
                        block_shift+j:almost_block_size+j],
                    dtype="double"),
                four_over * numpy.sum(
                    grayscale[
                        block_shift+i:almost_block_size+i,
                        block_shift+j:almost_block_size+j],
                    dtype="double")]
            strengths = [0.0, 0.0, 0.0, 0.0, 0.0]
            
            for e in xrange(5):
                strengths[e] = numpy.absolute(
                    numpy.sum(averages * EDGE_FILTER[e]))
            
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
            if edge_feature == VERTICAL_EDGE:
                local_histo[sub_local_index, 0] += 1.0
            elif edge_feature == HORIZONTAL_EDGE:
                local_histo[sub_local_index, 1] += 1.0
            elif edge_feature == DIAGONAL_45_DEGREE_EDGE:
                local_histo[sub_local_index, 2] += 1.0
            elif edge_feature == DIAGONAL_135_DEGREE_EDGE:
                local_histo[sub_local_index, 3] += 1.0
            elif edge_feature == NON_DIRECTIONAL_EDGE:
                local_histo[sub_local_index, 4] += 1.0
    
    for kidx in xrange(16):
        local_histo[kidx] = numpy.divide(local_histo[kidx], count_local[kidx])
    
    histogram = numpy.zeros(80, dtype="int")
    for local_idx, local_values in enumerate(local_histo):
        num_features = local_values.shape[0]
        for feature_idx, local_value in enumerate(local_values):
            bin_idx = (local_idx * num_features) + feature_idx
            histogram[bin_idx] = numpy.min(
                numpy.nonzero(
                    numpy.less_equal(
                        local_value,
                        QUANTIZERS[feature_idx])))
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
    bytecount = int(histogram.shape[0] / 2)
    histogrint = histogram.astype('int')
    idx_left = numpy.arange(bytecount) << 1
    idx_right = idx_left + 1
    return (
        ((histogrint[idx_left] << 4) | histogrint[idx_right]) - 128
    ).astype('byte')

def edge_histo_base64(histobytes):
    return base64.encodestring(
        "".join(
            [struct.pack('b', byte) for byte in histobytes]
        )).replace('\n', '')


def main(pth):
    from pylire.compatibility.utils import timecheck
    from pylire.process.channels import RGB
    from imread import imread
    
    (R, G, B) = RGB(imread(pth))
    
    @timecheck
    def timetest_naive_edge_histogram(R, G, B):
        edge_histo = edge_histogram(R, G, B)
        print("naive Lire port (string rep):")
        print("%s" % edge_histo_str(edge_histo))
        print("")
        print("binary hash:")
        print(edge_histo_bithash_str(edge_histo))
        print("")
        print("base64-encoded byte rep:")
        print(edge_histo_base64(edge_histo_bytes(edge_histo)))
        print("")
    
    timetest_naive_edge_histogram(R, G, B)


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


