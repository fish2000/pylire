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
