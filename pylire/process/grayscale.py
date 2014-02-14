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
        (219.0 * (((sR * 299.0).astype('double') + \
        (sG * 587.0).astype('double') + \
        (sB * 114.0).astype('double')) / 256.0) + 16.5).astype('int')
