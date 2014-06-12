from __future__ import division

import numpy
cimport numpy
cimport cython

#from libc.math cimport floor

# INT = numpy.int
FLOAT64 = numpy.float64

ctypedef numpy.int_t INT_t
ctypedef numpy.float64_t FLOAT64_t

cdef inline FLOAT64_t **cosine = [
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
]

cdef inline FLOAT64_t ZERO = <FLOAT64_t>0.0
cdef inline INT_t EIGHT = <INT_t>8
cdef inline INT_t ROUND_FACTOR(FLOAT64_t x):
    return <INT_t>(<FLOAT64_t>x + <FLOAT64_t>0.499999)

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
def FDCT(numpy.ndarray[INT_t, ndim=1] shape_plane not None):
    cdef int i, j, k
    cdef FLOAT64_t s = ZERO
    cdef numpy.ndarray[FLOAT64_t, ndim=1] dct = numpy.zeros_like(
        shape_plane, dtype=FLOAT64)
    
    for i in range(EIGHT):
        for j in range(EIGHT):
            s = ZERO
            for k in range(EIGHT):
                s += cosine[j][k] * <FLOAT64_t>shape_plane[EIGHT * i + k]
            dct[EIGHT * i + j] = s
    
    for i in range(EIGHT):
        for j in range(EIGHT):
            s = ZERO
            for k in range(EIGHT):
                s += cosine[i][k] * dct[EIGHT * k + j]
            shape_plane[EIGHT * i + j] = ROUND_FACTOR(s)

