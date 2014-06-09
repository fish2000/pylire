
import numpy
cimport numpy
cimport cython

ctypedef numpy.int_t INT_t
#ctypedef numpy.uint8_t UINT8_t

cdef inline INT_t EIGHT = <INT_t>8
cdef inline INT_t SIXTEEN = <INT_t>16
cdef inline INT_t EIGHTEEN = <INT_t>18
cdef inline INT_t TWENTYFIVE = <INT_t>25
cdef inline INT_t SIXTYSIX = <INT_t>66
cdef inline INT_t SEVENTYFOUR = <INT_t>74
cdef inline INT_t NINETYFOUR = <INT_t>94
cdef inline INT_t MINUSTHIRTYEIGHT = <INT_t>-38
cdef inline INT_t ONETWELVE = <INT_t>112
cdef inline INT_t ONETWENTYEIGHT = <INT_t>128
cdef inline INT_t ONETWENTYNINE = <INT_t>129

@cython.boundscheck(False)
@cython.wraparound(False)
def RGBtoYCbCr(numpy.ndarray[INT_t, ndim=2] sR not None,
               numpy.ndarray[INT_t, ndim=2] sG not None,
               numpy.ndarray[INT_t, ndim=2] sB not None):
    return (
        ((SIXTYSIX*sR + ONETWENTYNINE*sG + TWENTYFIVE*sB + ONETWENTYEIGHT) >> EIGHT) + SIXTEEN,
        ((MINUSTHIRTYEIGHT*sR - SEVENTYFOUR*sG + ONETWELVE*sB + ONETWENTYEIGHT) >> EIGHT) + ONETWENTYEIGHT,
        ((ONETWELVE*sR - NINETYFOUR*sG - EIGHTEEN*sB + ONETWENTYEIGHT) >> EIGHT) + ONETWENTYEIGHT)
