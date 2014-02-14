#!/usr/bin/env python
from __future__ import division

def RGB(ndim):
    """ Split an RGB/RGBA/L-mode image into R, G, and B channel arrays """
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
    return (R, G, B)