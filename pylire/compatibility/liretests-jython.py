#!/usr/bin/env jython-pylire

from net.semanticmetadata.lire.imageanalysis import ColorLayout
from net.semanticmetadata.lire.imageanalysis import EdgeHistogram
from net.semanticmetadata.lire.imageanalysis import PHOG
from net.semanticmetadata.lire.imageanalysis import OpponentHistogram
from net.semanticmetadata.lire.imageanalysis import JCD
from org.apache.commons.codec.binary import Base64
from javax.imageio import ImageIO
from java.io import File


def test_color_layout(im):

    print "Color Layout:"
    colorlay = ColorLayout()
    colorlay.extract(im)
    print colorlay.getStringRepresentation()

def test_edge_histogram(im):
    
    print "Edge Histogram:"
    edgehist = EdgeHistogram()
    edgehist.extract(im)
    print edgehist.getStringRepresentation()

def test_PHOG(im):

    print "PHOG:"
    phog = PHOG()
    phog.extract(im)
    print phog.getStringRepresentation()

def test_opponent_histogram(im):

    print "Opponent Histogram:"
    opphist = OpponentHistogram()
    opphist.extract(im)
    print opphist.getStringRepresentation()
    print Base64.encodeBase64String(
        opphist.getByteArrayRepresentation())

def test_JCD(im):

    print "JCD:"
    jcd = JCD()
    jcd.extract(im)
    print jcd.getStringRepresentation()

def main():
    # im_pth = "/Users/fish/Downloads/5717314638_2340739e06_b.jpg"
    
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
        print "IMAGE: %s" % basename(im_pth)
        test_color_layout(im)
        test_edge_histogram(im)
        #test_PHOG(im)
        test_opponent_histogram(im)
        #test_JCD(im)

if __name__ == "__main__":
    main()
