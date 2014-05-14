#!/usr/bin/env python
from __future__ import division, print_function

import numpy
import numexpr

from pylire.process.channels import YCbCr

zigzag = numpy.array([
    0, 1, 8, 16, 9, 2, 3, 10, 17, 24, 32, 25, 18, 11, 4, 5,
    12, 19, 26, 33, 40, 48, 41, 34, 27, 20, 13, 6, 7, 14, 21, 28,
    35, 42, 49, 56, 57, 50, 43, 36, 29, 22, 15, 23, 30, 37, 44, 51,
    58, 59, 52, 45, 38, 31, 39, 46, 53, 60, 61, 54, 47, 55, 62, 63
], dtype="int")

cosine = numpy.array([
    [
        3.535534e-01, 3.535534e-01, 3.535534e-01, 3.535534e-01,
        3.535534e-01, 3.535534e-01, 3.535534e-01, 3.535534e-01
    ], [
        4.903926e-01, 4.157348e-01, 2.777851e-01, 9.754516e-02,
        -9.754516e-02, -2.777851e-01, -4.157348e-01, -4.903926e-01
    ], [
        4.619398e-01, 1.913417e-01, -1.913417e-01, -4.619398e-01,
        -4.619398e-01, -1.913417e-01, 1.913417e-01, 4.619398e-01
    ], [
        4.157348e-01, -9.754516e-02, -4.903926e-01, -2.777851e-01,
        2.777851e-01, 4.903926e-01, 9.754516e-02, -4.157348e-01
    ], [
        3.535534e-01, -3.535534e-01, -3.535534e-01, 3.535534e-01,
        3.535534e-01, -3.535534e-01, -3.535534e-01, 3.535534e-01
    ], [
        2.777851e-01, -4.903926e-01, 9.754516e-02, 4.157348e-01,
        -4.157348e-01, -9.754516e-02, 4.903926e-01, -2.777851e-01
    ], [
        1.913417e-01, -4.619398e-01, 4.619398e-01, -1.913417e-01,
        -1.913417e-01, 4.619398e-01, -4.619398e-01, 1.913417e-01
    ], [
        9.754516e-02, -2.777851e-01, 4.157348e-01, -4.903926e-01,
        4.903926e-01, -4.157348e-01, 2.777851e-01, -9.754516e-02
    ]
], dtype="double")

def coords_yx(height, width):
    return numpy.swapaxes(
        numpy.dstack(
            numpy.meshgrid(
                numpy.arange(height),
                numpy.arange(width))), 0, 1)

def coords(ndim):
    return coords_yx(*ndim.shape[:2])

def k_coords(height, width):
    (x_axis, y_axis) = coords_yx(height, width).T
    return (y_axis.T << 3) + x_axis.T

def k_map(ndim):
    coordinates = coords(ndim)
    (y, x) = coordinates.shape[:2]
    (x_axis, y_axis) = coordinates.T
    x_axis /= (x * 0.125)
    y_axis /= (y * 0.125)
    return (y_axis.T << 3) + x_axis.T

def quant_ydc(ints):
    return numexpr.evaluate("""
where(ints > 192, 112 + ((i - 192) >> 2),
where(ints > 160, 96 + ((i - 160) >> 1),
where(ints > 96, 32 + (i - 96),
where(ints > 64, 16 + ((i - 64) >> 1), 0))))""")

def quant_cdc(ints):
    return numexpr.evaluate("""
where(ints > 191, 63,
where(ints > 160, 56 + ((i - 160) >> 2),
where(ints > 144, 48 + ((i - 144) >> 1),
where(ints > 112, 16 + (i - 112),
where(ints > 96, 8 + ((i - 96) >> 1),
where(ints > 64, (i - 64) >> 2, 0))))))""")

def quant_ac(ints):
    ints = numpy.clip(ints, -256, 255)
    out = numexpr.evaluate("""
where(abs(ints) > 127, 64 + ((abs(ints)) >> 2),
where(abs(ints) > 63, 32 + ((abs(ints)) >> 2), abs(ints)
))""")
    signed = numexpr.evaluate("where(ints < 0, -1, 1)")
    return (out * signed) + 128

def shape_from_image(ndim):
    """ Return a 'shape' square for a given RGB image.
        
        The shape square is a 64x3 array, filled the per-channel average values
        of the images' spatially quantized YCbCr pixel data.
    """
    Shape = numpy.zeros((64, 3), dtype="int")
    KMap = k_map(ndim)
    kflat = KMap.flatten()
    kmax = numpy.max(kflat)
    
    KCounts = numpy.bincount(kflat)
    KChannelSums = numpy.ndarray((KCounts.shape[0], 3), dtype="int")
    
    print("KCounts:")
    print(KCounts)
    print("KChannelSums:")
    print(KChannelSums)
    
    for kidx in xrange(kmax):
        for channel_idx, channel in enumerate(YCbCr(ndim)):
            KChannelSums[kidx, channel_idx] = numpy.sum(numpy.ma.masked_where(KMap == kidx, channel))
        if KCounts[kidx] == 0:
            continue
        Shape[kidx] = (KChannelSums[kidx] / KCounts[kidx]).astype('int')
    
    return Shape


def main(pth):
    from pylire.compatibility.utils import timecheck
    from imread import imread
    
    ndim = imread(pth)
    
    @timecheck
    def timetest_naive_edge_histogram(ndim):
        shape = shape_from_image(ndim)
        print("image shape:")
        print(ndim.shape)
        print("")
        print("image 'shape':")
        print(shape)
        print("")
    
    timetest_naive_edge_histogram(ndim)


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



    
    
    
