#!/usr/bin/env python
from __future__ import division, print_function
#from math import floor

import numpy
import numexpr

from pylire.process import external
from pylire.process.channels import YCbCr
from pylire.process.bitsampling import histogram_hash, histogram_hash_string

SHAPE_WIDTH = 8
SHAPE_HEIGHT = 8
SHAPE_SIZE = SHAPE_WIDTH * SHAPE_HEIGHT

NUM_Y = 21
NUM_C = 6
ROUND_FACTOR = 0.499999

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
], dtype="float64")

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
    (y, x) = ndim.shape[:2]
    (x_axis, y_axis) = coordinates.T
    x_axis /= (x * 0.125)
    y_axis /= (y * 0.125)
    return (y_axis.T << 3) + x_axis.T

def quant_ydc(ints):
    return numexpr.evaluate("""
where(ints > 192, 112 + ((ints - 192) >> 2),
where(ints > 160, 96 + ((ints - 160) >> 1),
where(ints > 96, 32 + (ints - 96),
where(ints > 64, 16 + ((ints - 64) >> 1), 0))))""")

def quant_cdc(ints):
    return numexpr.evaluate("""
where(ints > 191, 63,
where(ints > 160, 56 + ((ints - 160) >> 2),
where(ints > 144, 48 + ((ints - 144) >> 1),
where(ints > 112, 16 + (ints - 112),
where(ints > 96, 8 + ((ints - 96) >> 1),
where(ints > 64, (ints - 64) >> 2, 0))))))""")

def quant_ac(ints):
    ints = numpy.clip(ints, -256, 255)
    nints = numpy.absolute(ints)
    out = numexpr.evaluate("""
where(nints > 127, 64 + ((nints) >> 2),
where(nints > 63, 32 + ((nints) >> 2), nints
))""")
    signed = numexpr.evaluate("where(ints < 0, -1, 1)")
    if not nints.shape:
        return None
    return (out * signed) + 128

#@external
def FDCT(shape_plane):
    """ FDCT -- 'Fast' Discrete Cosine Transform,
        performed in-place on a 1D shape plane of length 64.
        ... This is the naively-ported logic straight from Lire:
            http://git.io/naive-fdct """
    dct = numpy.zeros_like(shape_plane, dtype='float64')
    
    for i in xrange(8):
        for j in xrange(8):
            s = 0.0
            for k in xrange(8):
                s += cosine[j, k] * shape_plane[8 * i + k]
            dct[8 * i + j] = s
    
    for i in xrange(8):
        for j in xrange(8):
            s = 0.0
            for k in xrange(8):
                s += cosine[i, k] * dct[8 * k + j]
            shape_plane[8 * i + j] = int(s + ROUND_FACTOR)

C_FDCT = external(FDCT)

def shape_from_image(ndim):
    """ Return a 'shape' square for a given RGB image.

        The shape square is a 64x3 array, filled the per-channel average values
        of the images' spatially quantized YCbCr pixel data.
    """
    ycbcr = YCbCr(ndim)

    Shape = numpy.zeros((SHAPE_SIZE, 3), dtype="int")
    KMap = k_map(ndim)
    kflat = KMap.flatten()
    kmax = numpy.max(kflat)

    KCounts = numpy.bincount(kflat, minlength=SHAPE_SIZE)
    KChannelSums = numpy.ndarray((KCounts.shape[0], 3), dtype="int")

    # print("KCounts (len = %s):" % len(KCounts))
    # print(KCounts)
    # print("KChannelSums:")
    # print(KChannelSums)

    for kidx in xrange(kmax):
        for channel_idx, channel in enumerate(ycbcr):
            KChannelSums[kidx, channel_idx] = numpy.sum(
                numpy.ma.masked_where(KMap == kidx, channel))

    for kidx in k_coords(SHAPE_WIDTH, SHAPE_HEIGHT).T.flatten():
        if KCounts[kidx] == 0:
            continue
        Shape[kidx] = (KChannelSums[kidx] // KCounts[kidx]).astype('int')

    return Shape.T

def color_layout(ndim):
    shape = shape_from_image(ndim)
    YCoeff = numpy.zeros((64,), dtype="int")
    CbCoeff = numpy.zeros((64,), dtype="int")
    CrCoeff = numpy.zeros((64,), dtype="int")
    
    FDCT(shape[0])
    FDCT(shape[1])
    FDCT(shape[2])
    
    # print("ZIGZAG:")
    # print(shape[0][zigzag] >> 1)
    # print("NORMAL:")
    # print(shape[0] >> 1)
    
    YCoeff = quant_ac(shape[0][zigzag] >> 1) >> 3
    CbCoeff = quant_ac(shape[1][zigzag] >> 3)
    CrCoeff = quant_ac(shape[2][zigzag] >> 3)
    
    YCoeff[0] = quant_ydc(shape[0][0] >> 3) >> 1
    CbCoeff[0] = quant_cdc(shape[1][0] >> 3)
    CrCoeff[0] = quant_cdc(shape[2][0] >> 3)
    
    return (YCoeff, CbCoeff, CrCoeff)

def cl_str(cY, cCb, cCr):
    return "%sz%sz" % (
        " ".join(cY[:NUM_Y].astype('str')),
        " ".join(cCb[:NUM_C].astype('str')),
        " ".join(cCr[:NUM_C].astype('str')))

def cl_bithash(cY, cCb, cCr):
    return histogram_hash(
        numpy.concatenate(
            cY, cCb, cCr).astype('double'))

def cl_bithash_str(cY, cCb, cCr):
    return histogram_hash_string(
        numpy.concatenate(
            cY, cCb, cCr).astype('double'))

def cl_base64(cY, cCb, cCr):
    pass

def main(pth):
    from pylire.compatibility.utils import timecheck
    from imread import imread

    ndim = imread(pth)
    #ndim_shape = shape_from_image(ndim)

    @timecheck
    def timetest_FDCT_python(ndim_shape):
        FDCT(ndim_shape[0])
        FDCT(ndim_shape[1])
        FDCT(ndim_shape[2])
        #print(ndim_shape)
        return ndim_shape

    @timecheck
    def timetest_FDCT_cython(ndim_shape):
        C_FDCT(ndim_shape[0])
        C_FDCT(ndim_shape[1])
        C_FDCT(ndim_shape[2])
        #print(ndim_shape)
        return ndim_shape

    ns1 = shape_from_image(ndim)
    out_py = timetest_FDCT_python(ns1)
    ns2 = shape_from_image(ndim)
    out_cy = timetest_FDCT_cython(ns2)
    print("")
    print("RESULTS EQUAL:")
    print(numpy.equal(out_py, out_cy))
    print("")

    @timecheck
    def timetest_color_layout_shape(ndim):
        shape = shape_from_image(ndim)
        print("image shape:")
        print(ndim.shape)
        print("")
        # print("image 'shape':")
        # print(shape)
        # print("")
        print("image 'shape' shape:")
        print(shape.shape)
        print("")

    #timetest_color_layout_shape(ndim)

    @timecheck
    def timetest_color_layout(ndim):
        (cY, cCb, cCr) = color_layout(ndim)
        # print("")
        # print(cY)
        # print(cCb)
        # print(cCr)

    #timetest_color_layout(ndim)

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
