from __future__ import division

import numpy
cimport numpy
cimport cython

ctypedef numpy.float32_t FLOAT32_t

cdef inline FLOAT32_t sR_NUMERATOR = <FLOAT32_t>299.0
cdef inline FLOAT32_t sG_NUMERATOR = <FLOAT32_t>587.0
cdef inline FLOAT32_t sB_NUMERATOR = <FLOAT32_t>114.0
cdef inline FLOAT32_t ONETHOUSAND = <FLOAT32_t>1000.0

@cython.boundscheck(False)
@cython.wraparound(False)
def ITU_R_601_2(numpy.ndarray[FLOAT32_t, ndim=2] sR not None,
                numpy.ndarray[FLOAT32_t, ndim=2] sG not None,
                numpy.ndarray[FLOAT32_t, ndim=2] sB not None):
    return \
        (sR * sR_NUMERATOR / ONETHOUSAND).astype('uint8') + \
        (sG * sG_NUMERATOR / ONETHOUSAND).astype('uint8') + \
        (sB * sB_NUMERATOR / ONETHOUSAND).astype('uint8')
