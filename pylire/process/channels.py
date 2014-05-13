#!/usr/bin/env python
from __future__ import division

def RGB(ndim, astype='float32'):
    """ Split an RGB/RGBA/L-mode image into R, G, and B channel arrays """
    if len(ndim.shape) == 2:
        R = G = B = ndim.astype(astype)
    elif len(ndim.shape) == 3:
        if ndim.shape[2] > 2:
            (R, G, B) = (channel.T.astype(astype) for channel in ndim.T[:3])
        else:
            R = G = B = ndim.T[0].T.astype(astype)
    else:
        raise ValueError(
            "Can't split to RGB channels from image array with shape = %s" % str(
                ndim.shape))
    return (R, G, B)

def YCbCr(ndim):
    """ Split and remap RGB channels to YCbCr values - fast integer-math version. See also:
        https://gist.github.com/fish2000/4e86edd688feddc845e2#file-rgb_ycbcr_ypbpr-py-L112-L122 """
    (R, G, B) = RGB(ndim, astype='uint8')
    Y = ((66*R + 129*G + 25*B + 128) >> 8) + 16
    Cb = ((-38*R - 74*G + 112*B + 128) >> 8) + 128
    Cr = ((112*R - 94*G - 18*B + 128) >> 8) + 128
    return (Y, Cb, Cr)