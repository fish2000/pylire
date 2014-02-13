from __future__ import division

import numpy
cimport numpy
cimport cython

cdef extern from "math.h":
    double sqrt(double x)

INT = numpy.int
UINT8 = numpy.uint8
FLOAT32 = numpy.float32

ctypedef numpy.int_t INT_t
ctypedef numpy.uint8_t UINT8_t
ctypedef numpy.float32_t FLOAT32_t

cdef inline float csqrt(float x): return <FLOAT32_t>sqrt(<double>x)

cdef inline FLOAT32_t ROOT_2 = csqrt(2.0)
cdef inline FLOAT32_t ROOT_3 = csqrt(3.0)
cdef inline FLOAT32_t ROOT_6 = csqrt(6.0)

cdef inline FLOAT32_t TWOFIFTYFIVE_OVER_ROOT2 = <FLOAT32_t>255.0 / ROOT_2
cdef inline FLOAT32_t FIVETEN_OVER_ROOT2 = <FLOAT32_t>510.0 / ROOT_2
cdef inline FLOAT32_t FIVETEN_OVER_ROOT6 = <FLOAT32_t>510.0 / ROOT_6
cdef inline FLOAT32_t TENTWENTY_OVER_ROOT6 = <FLOAT32_t>1020.0 / ROOT_6
cdef inline FLOAT32_t THREE_TIMES_TWOFIFTYFIVE_OVER_ROOT3 = <FLOAT32_t>3.0 * <FLOAT32_t>255.0 / ROOT_3
cdef inline INT_t FOURBYFOUR = <INT_t>4 * <INT_t>4

@cython.boundscheck(False)
@cython.wraparound(False)
def opponent_histogram_key_vector(numpy.ndarray[FLOAT32_t, ndim=2] sR not None,
                                  numpy.ndarray[FLOAT32_t, ndim=2] sG not None,
                                  numpy.ndarray[FLOAT32_t, ndim=2] sB not None):
    return \
        (numpy.minimum(numpy.floor(
            ((((sR - sG) / ROOT_2) + \
                TWOFIFTYFIVE_OVER_ROOT2).astype('float32') / \
                FIVETEN_OVER_ROOT2) * 4.0), 3.0)).astype('int') + \
        (numpy.minimum(numpy.floor(
            ((((sR + sG - 2 * sB) / ROOT_6).astype('float32') + FIVETEN_OVER_ROOT6) / \
                TENTWENTY_OVER_ROOT6) * 4.0), 3.0)).astype('int') * 4 + \
        (numpy.minimum(3.0, numpy.floor(
            (((sR + sG + sB) / ROOT_3).astype('float32') / \
                THREE_TIMES_TWOFIFTYFIVE_OVER_ROOT3) * 4.0))).astype('int') * FOURBYFOUR