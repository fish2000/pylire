#!/usr/bin/env python
from __future__ import division

from pylire.process import external

@external
def ITU_R_601_2(sR, sG, sB):
    """ Perceptually proportional RGB-to-grayscale """
    return \
        (sR * 299.0 / 1000.0).astype('uint8') + \
        (sG * 587.0 / 1000.0).astype('uint8') + \
        (sB * 114.0 / 1000.0).astype('uint8')

@external
def YValue(sR, sG, sB):
    """ RGB to Y value (as in YCrCb) """
    return \
        (219.0 * (
            (0.299 * sR + 0.587 * sG + 0.114 * sB) / 256.0
            ).astype('double') + 16.5
        ).astype('int')
