#!/usr/bin/env jython

from net.semanticmetadata.lire.imageanalysis import ColorLayout
from net.semanticmetadata.lire.imageanalysis import EdgeHistogram
from net.semanticmetadata.lire.imageanalysis import PHOG
from net.semanticmetadata.lire.imageanalysis import OpponentHistogram
from net.semanticmetadata.lire.imageanalysis import JCD
from org.apache.commons.codec.binary import Base64
from javax.imageio import ImageIO
from java.io import File


def test_color_layout(im):
    """ Testing: color layout """
    print ""
    print "Color Layout:"
    colorlay = ColorLayout()
    colorlay.extract(im)
    print colorlay.getStringRepresentation()
    print Base64.encodeBase64String(
        colorlay.getByteArrayRepresentation())

def test_edge_histogram(im):
    """ Testing: edge histogram """
    print ""
    print "Edge Histogram:"
    edgehist = EdgeHistogram()
    edgehist.extract(im)
    print edgehist.getStringRepresentation()
    print Base64.encodeBase64String(
        edgehist.getByteArrayRepresentation())

def test_PHOG(im):
    """ Testing: Pyramidal Histogram of Gradient (PHOG) Descriptor """
    print ""
    print "PHOG:"
    phog = PHOG()
    phog.extract(im)
    print phog.getStringRepresentation()
    print Base64.encodeBase64String(
        phog.getByteArrayRepresentation())

def test_opponent_histogram(im):
    """ Testing: opponent histogram """
    print ""
    print "Opponent Histogram:"
    opphist = OpponentHistogram()
    opphist.extract(im)
    print opphist.getStringRepresentation()
    print Base64.encodeBase64String(
        opphist.getByteArrayRepresentation())

def test_JCD(im):
    """ Testing: Joint Color Descriptor (JCD) """
    print ""
    print "JCD:"
    jcd = JCD()
    jcd.extract(im)
    print jcd.getStringRepresentation()
    print Base64.encodeBase64String(
        jcd.getByteArrayRepresentation())

def main():
    """ Run all tests """
    from os.path import expanduser, basename, join
    from os import listdir
    
    im_directory = expanduser("~/Downloads")
    im_paths = map(
        lambda name: join(im_directory, name),
        filter(
            lambda name: name.lower().endswith('jpg'),
            listdir(im_directory)))
    
    for im_pth in im_paths:
        im = ImageIO.read(File(im_pth))
        print ""
        print "-" * 120
        print ""
        print "IMAGE: %s" % basename(im_pth)
        test_color_layout(im)
        test_edge_histogram(im)
        #test_PHOG(im)
        test_opponent_histogram(im)
        #test_JCD(im)
        print "-" * 120

if __name__ == "__main__":
    main()
