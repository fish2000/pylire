#!/usr/bin/env python
from __future__ import division

from scipy.ndimage import sobel as scipy_sobel
from skimage.filter import canny as skimage_canny
import numpy
import math

from pylire.compatibility.utils import print_array_info
from pylire.process.grayscale import ITU_R_601_2

CANNY_THRESHOLD_LOW = 60.0
CANNY_THRESHOLD_HIGH = 100.0
PHOG_BINS = 30

PI_OVER_TWO = numpy.pi / 2.0
PI_OVER_EIGHT = numpy.pi / 8.0
THREE_PI_OVER_EIGHT = 3.0 * numpy.pi / 8.0
PI_PLUS_POINT_FIVE = numpy.pi + 0.5

BINS_TIMES_TWO = PHOG_BINS * 2
BINS_TIMES_THREE = PHOG_BINS * 3
BINS_TIMES_FOUR = PHOG_BINS * 4

# Notes (from the Lire source):
# // used to quantize bins to [0, quantizationFactor]
# // Note that a quantization factor of 127d has better precision,
# but is not supported by the current serialization method.
QUANTIZATION_FACTOR = 15.0


def set_canny_pixel(x, y, grayscale, value):
    if value > CANNY_THRESHOLD_LOW:
        grayscale[x, y] = 0
    elif value > CANNY_THRESHOLD_HIGH:
        grayscale[x, y] = 128
    else:
        grayscale[x, y] = 255


def track_weak_ones(x, y, grayscale):
    """ Tail-recursive neighborhood-stalking function to hunt
        and normalize weak pixels (with extreme predjudice) """
    for xx in xrange(x - 1, x + 1):
        for yy in xrange(y - 1, y + 1):
            # 'if isWeak()' (unrolled)
            if 0 < grayscale[xx, yy] < 255:
                grayscale[xx, yy] = 0
                track_weak_ones(xx, yy, grayscale)

def naive_subphog(X, Y, W, H, grayscale, grayD):
    subhistogram = numpy.zeros(PHOG_BINS, dtype="double")
    for x in xrange(X, X + W):
        for y in xrange(Y, Y + H):
            # N.B. replace this shit with a numpy.where() call
            if grayscale[x, y] < 50:
                # "it's an edge pixel, so it counts in."
                actual = (grayD[x, y] / numpy.pi + 0.5) * PHOG_BINS
                bindex = math.floor(actual) != PHOG_BINS and int(math.floor(actual)) or 0
                if actual == math.floor(actual):
                    # "if it's a discrete thing ..."
                    subhistogram[bindex] += 1
                else:
                    subhistogram[bindex] += actual - math.floor(actual)
                    binhigh = math.ceil(actual) != PHOG_BINS and int(math.ceil(actual)) or 0
                    subhistogram[binhigh] += math.ceil(actual) - actual
    
    # "normalize histogram to max norm."
    # NB. this piece is actually vectorized
    histomax = numpy.max(subhistogram)
    if histomax > 0.0:
        subhistogram = numpy.minimum(
            QUANTIZATION_FACTOR,
            numpy.floor(
                QUANTIZATION_FACTOR * subhistogram / histomax))
    
    return subhistogram


def vector_subphog(X, Y, W, H, grayscale, grayD):
    #from numpy.ma import MaskedArray
    import scipy.stats
    
    subhistogram = numpy.zeros(PHOG_BINS, dtype="double")
    subphog = grayscale[X:(X+W), Y:(Y+H)] < 50
    #bindex = numpy.floor((MaskedArray(grayD, mask=subphog) / numpy.pi + 0.5) * PHOG_BINS).astype('int')
    # bins = numpy.bincount(numpy.where(bindex == PHOG_BINS, 0, bindex))
    
    print_array_info(grayD, title="grayD")
    print_array_info(subphog, title="subphog")
    #print_array_info(bindex, title="bindex")
    
    subdirectionals = (grayD[subphog] / numpy.pi + 0.5) * PHOG_BINS
    histo = numpy.bincount(
        numpy.where(
            subdirectionals.astype('int') == PHOG_BINS,
            0, subdirectionals.astype('int')))
    
    print_array_info(histo, title="HISTOGRAM (grayD[subphog])")
    # print_array_info(bins, title="BINS")
    
    
    
    # print("BINDEXES:")
    # print(numpy.array_repr(bindexes, max_line_width=200))
    # print("max: %s min: %s" % (numpy.max(bindexes), numpy.min(bindexes)))
    
    return
    
    # yo = numpy.where(numpy.floor(bindexfp) == PHOG_BINS, 0, numpy.floor(bindexfp))
    # bindexes = numpy.where(bindexfp == numpy.floor(bindexfp),
    #     (numpy.floor(bindexfp).astype('int'), 1),
    #     (numpy.floor(bindexfp).astype('int'), bindexfp - numpy.floor(bindexfp)))
    # bindexes = numpy.zeros_like(subphog)
    # bindexes += numpy.where(values == numpy.floor(values).astype('int'),
    #     1, (values - numpy.floor(values)))
    # bindexes += numpy.where(values == numpy.ceil(values).astype('int'),
    #     0, (numpy.ceil(values) - values))
    # print("BINDEXES:")
    # print(bindexes)
    # return
    
    # "normalize histogram to max norm."
    # NB. this piece is actually vectorized
    histomax = numpy.max(subhistogram)
    if histomax > 0.0:
        subhistogram = numpy.minimum(
            QUANTIZATION_FACTOR,
            numpy.floor(
                QUANTIZATION_FACTOR * subhistogram / histomax))
    
    return subhistogram


def naive_sobel(grayscale):
    """ Totally naive port of pixel-loop logic, taken straight
        from Lire's PHOG implementation:
    https://github.com/fish2000/lire/blob/master/src/main/java/net/semanticmetadata/lire/imageanalysis/PHOG.java#L288
        ... There are a bajillion better ways to Sobel things
        (including fast Python implementations in scipy,
        scikit-image, and mahotas) which will replace this
        torturously braindead semantic-wholesale-copy Java-style
        for-loop hodown... in THE FUTURE. """
    (W, H) = grayscale.shape[:2]
    sobelX = numpy.zeros((W, H), dtype="double")
    sobelY = numpy.zeros((W, H), dtype="double")
    # N.B. these loops start at 1, not zero
    for x in xrange(1, W - 1):
        for y in xrange(1, H - 1):
            sX = sY = 0
            sX += grayscale[x - 1, y - 1]
            sY += grayscale[x - 1, y - 1]
            sX += 2 * grayscale[x - 1, y]
            sX += grayscale[x - 1, y + 1]
            sY -= grayscale[x - 1, y + 1]
            
            sX -= grayscale[x + 1, y + 1]
            sY += grayscale[x + 1, y - 1]
            sX -= 2 * grayscale[x + 1, y]
            sX -= grayscale[x + 1, y + 1]
            sY -= grayscale[x + 1, y + 1]
            sobelX[x, y] = sX
            
            sY += 2 * grayscale[x, y - 1]
            sY -= 2 * grayscale[x, y + 1]
            sobelY[x, y] = sY
    return (sobelX, sobelY)

def PHOG(R, G, B):
    grayscale = ITU_R_601_2(R, G, B)
    (W, H) = grayscale.shape[:2]
    
    #(sobelX, sobelY) = naive_sobel(grayscale)
    sobelX = numpy.zeros((W, H), dtype="double")
    sobelY = numpy.zeros((W, H), dtype="double")
    scipy_sobel(grayscale, axis=0, output=sobelX)
    scipy_sobel(grayscale, axis=1, output=sobelY)
    
    grayD = numpy.zeros((W, H), dtype="double")
    # grayM = numpy.zeros((W, H), dtype="double")
    
    # "setting gradient magnitude and gradinet direction"
    for x in xrange(W):
        for y in xrange(H):
            if sobelX[x, y] != 0.0:
                grayD[x, y] = math.atan(sobelY[x, y] / sobelX[x, y])
            else:
                grayD[x, y] = PI_OVER_TWO
    
    # grayM = numpy.sqrt(numpy.square(sobelY) + numpy.square(sobelX))
    
    # "non-maximum suppression"
    # grayscale[:, 0] = 255
    # grayscale[:, H - 1] = 255
    # grayscale[0, :] = 255
    # grayscale[W - 1, :] = 255
    
    grayscale = skimage_canny(grayscale,
        low_threshold=CANNY_THRESHOLD_LOW,
        high_threshold=CANNY_THRESHOLD_HIGH).astype('int') * 255
    
    # As they say in lire:
    # "Canny Edge Detection over ... lets go for the PHOG ..."
    histogram = numpy.zeros(
        PHOG_BINS + 4*PHOG_BINS + 4*4*PHOG_BINS,
        dtype="double")
    
    # "level0"
    vector_subphog(0, 0, W, H, grayscale, grayD)
    histogram[:PHOG_BINS] = naive_subphog(
        0, 0, W, H, grayscale, grayD)
    
    # "level1"
    vector_subphog(0, 0, int(W / 2), int(H / 2), grayscale, grayD)
    histogram[PHOG_BINS:PHOG_BINS+PHOG_BINS] = naive_subphog(
        0, 0, int(W / 2), int(H / 2), grayscale, grayD)
    
    vector_subphog(int(W / 2), 0, int(W / 2), int(H / 2), grayscale, grayD)
    histogram[BINS_TIMES_TWO:PHOG_BINS+BINS_TIMES_TWO] = naive_subphog(
        int(W / 2), 0, int(W / 2), int(H / 2), grayscale, grayD)
    
    vector_subphog(0, int(H / 2), int(W / 2), int(H / 2), grayscale, grayD)
    histogram[BINS_TIMES_THREE:PHOG_BINS+BINS_TIMES_THREE] = naive_subphog(
        0, int(H / 2), int(W / 2), int(H / 2), grayscale, grayD)
    
    vector_subphog(int(W / 2), int(H / 2), int(W / 2), int(H / 2), grayscale, grayD)
    histogram[BINS_TIMES_FOUR:PHOG_BINS+BINS_TIMES_FOUR] = naive_subphog(
        int(W / 2), int(H / 2), int(W / 2), int(H / 2), grayscale, grayD)
    
    # "level 2"
    wstep = int(W / 4)
    hstep = int(H / 4)
    binpos = 5 # "the next free section in the histogram"
    for xidx in xrange(4):
        for yidx in xrange(4):
            offset = binpos * PHOG_BINS
            histogram[offset:PHOG_BINS+offset] = naive_subphog(
                xidx * wstep, yidx * hstep, wstep, hstep, grayscale, grayD)
            binpos += 1
    
    return histogram.astype("byte")


def PHOG_bytes(histogram):
    """ N.B. THIS FUNCTION IS EXACTLY THE SAME AS edge_histo_bytes()
        IN THE edge_histogram MODULE SO EVENTUALLY SOMEONE SHOULD DO
        SOMETHING ABOUT THAT OK YEAH """
    bytecount = int(histogram.shape[0] / 2)
    histogrint = histogram.astype('int')
    idx_left = numpy.arange(bytecount) << 1
    idx_right = idx_left + 1
    return (
        ((histogrint[idx_left] << 4) | histogrint[idx_right]) - 128
    ).astype('byte')




def main(pth):
    from pylire.compatibility.utils import timecheck
    from pylire.process.channels import RGB
    from imread import imread
    
    (R, G, B) = RGB(imread(pth))
    
    @timecheck
    def timetest_naive_PHOG(R, G, B):
        phog = PHOG(R, G, B)
        print("naive Lire port (raw PHOG histo):")
        print_array_info(phog)
        print("")
    
    timetest_naive_PHOG(R, G, B)

if __name__ == '__main__':
    
    import sys
    from os import listdir
    from os.path import expanduser, basename, join
    
    im_directory = expanduser("~/Downloads")
    im_paths = map(
        lambda name: join(im_directory, name),
        filter(
            lambda name: name.lower().endswith('jpg'),
            listdir(im_directory)))
    
    for im_pth in im_paths:
        
        print("")
        print("")
        print("IMAGE: %s" % basename(im_pth))
        main(im_pth)
        sys.exit(0)


