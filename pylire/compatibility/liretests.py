#!/usr/bin/env jython-pylire

from net.semanticmetadata.lire.imageanalysis import ColorLayout
from net.semanticmetadata.lire.imageanalysis import EdgeHistogram
from net.semanticmetadata.lire.imageanalysis import PHOG
from net.semanticmetadata.lire.imageanalysis import OpponentHistogram
from net.semanticmetadata.lire.imageanalysis import JCD
from org.apache.commons.codec.binary import Base64
from javax.imageio import ImageIO
from java.io import File

im_pth = "/Users/fish/Downloads/5717314638_2340739e06_b.jpg"
im = ImageIO.read(File(im_pth))

def test_color_layout():

    print "Color Layout:"
    colorlay = ColorLayout()
    colorlay.extract(im)
    print colorlay.getStringRepresentation()
    print ""

def test_edge_histogram():
    
    print "Edge Histogram:"
    edgehist = EdgeHistogram()
    edgehist.extract(im)
    print edgehist.getStringRepresentation()
    print ""

def test_PHOG():

    print "PHOG:"
    phog = PHOG()
    phog.extract(im)
    print phog.getStringRepresentation()
    print ""

def test_opponent_histogram():

    print "Opponent Histogram:"
    opphist = OpponentHistogram()
    opphist.extract(im)
    print opphist.getStringRepresentation()
    print ""
    print Base64.encodeBase64String(
        opphist.getByteArrayRepresentation())
    print ""

def test_JCD():

    print "JCD:"
    jcd = JCD()
    jcd.extract(im)
    print jcd.getStringRepresentation()
    print ""

if __name__ == "__main__":
    print ""
    print ""
    
    test_color_layout()
    test_edge_histogram()
    #test_PHOG()
    test_opponent_histogram()
    #test_JCD()
