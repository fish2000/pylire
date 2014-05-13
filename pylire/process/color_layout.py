
import numpy
import numexpr

from pylire.process.channels import YCbCr

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
], dtype="double")

def coords_yx(height, width):
    return numpy.swapaxes(
        numpy.dstack(
            numpy.meshgrid(
                numpy.arange(height),
                numpy.arange(width))), 0, 1)

def coords(ndim):
    return coords_yx(*ndim.shape[:2])

def k_coords(height, width):
    (y_axis, x_axis) = coords_yx(height, width).T
    return (y_axis.T << 3) + x_axis.T

def k_map(ndim):
    (y_axis, x_axis) = coords(ndim).T
    y_axis /= (y_axis.shape[0] * 0.125)
    x_axis /= (x_axis.shape[1] * 0.125)
    return (y_axis.T << 3) + x_axis.T

def quant_ydc(ints):
    return numexpr.evaluate("""
where(ints > 192, 112 + ((i - 192) >> 2),
where(ints > 160, 96 + ((i - 160) >> 1),
where(ints > 96, 32 + (i - 96),
where(ints > 64, 16 + ((i - 64) >> 1), 0))))""")

def quant_cdc(ints):
    return numexpr.evaluate("""
where(ints > 191, 63,
where(ints > 160, 56 + ((i - 160) >> 2),
where(ints > 144, 48 + ((i - 144) >> 1),
where(ints > 112, 16 + (i - 112),
where(ints > 96, 8 + ((i - 96) >> 1),
where(ints > 64, (i - 64) >> 2, 0))))))""")

def quant_ac(ints):
    ints = numpy.clip(ints, -256, 255)
    out = numexpr.evaluate("""
where(abs(ints) > 127, 64 + ((abs(ints)) >> 2),
where(abs(ints) > 63, 32 + ((abs(ints)) >> 2), abs(ints)
))""")
    signed = numexpr.evaluate("where(ints < 0, -1, 1)")
    return (out * signed) + 128

def create_shape_from_RGB_image(ndim):
    Shape = numpy.zeros((64, 3), dtype="int")
    # total = numpy.zeros((3, 64), dtype="long")
    # (Y, Cb, Cr) = 
    
    KMap = k_map(ndim)
    kflat = KMap.flatten()
    kmax = numpy.max(kflat)
    
    KCounts = numpy.bincount(kflat)
    KChannelSums = numpy.ndarray((kmax+1, 3), dtype="int")
    
    # KSums = dict(
    #    sY=numpy.ndarray(Y.shape, dtype="uint"),
    #     sCb=numpy.ndarray(Cb.shape, dtype="uint"),
    #     sCr=numpy.ndarray(Cr.shape, dtype="uint"))
    
    for kidx in xrange(kmax):
        for channel_idx, channel in enumerate(YCbCr(ndim)):
            KChannelSums[kidx, channel_idx] = numpy.sum(numpy.ma.masked_where(KMap == kidx, channel))
        if kidx == 0:
            continue
        Shape[kidx] = (KChannelSums[kidx] / KCounts[kidx]).astype('int')
    
    '''
    for kidx in k_coords(8, 8).flatten():
        KChannelSums[kidx, 1] = numpy.sum(numpy.ma.masked_where(KMap == kidx, Cb))
        KChannelSums[kidx, 2] = numpy.sum(numpy.ma.masked_where(KMap == kidx, Cr))
    '''
    
    
    
    
    
