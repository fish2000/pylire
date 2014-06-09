#!/usr/bin/env python

from jnius import JavaClass, MetaJavaClass, JavaMethod
from pylire.commands.hashes import setup_jvm
jnius = setup_jvm()

ColorLayout = jnius.autoclass('net.semanticmetadata.lire.imageanalysis.ColorLayout')
EdgeHistogram = jnius.autoclass('net.semanticmetadata.lire.imageanalysis.EdgeHistogram')
PHOG = jnius.autoclass('net.semanticmetadata.lire.imageanalysis.PHOG')
OpponentHistogram = jnius.autoclass('net.semanticmetadata.lire.imageanalysis.OpponentHistogram')
JCD = jnius.autoclass('net.semanticmetadata.lire.imageanalysis.JCD')
Base64 = jnius.autoclass('org.apache.commons.codec.binary.Base64')
#ImageIO = jnius.autoclass('javax.imageio.ImageIO')
File = jnius.autoclass('java.io.File')

class ImageIO(JavaClass):
    __metaclass__ = MetaJavaClass
    __javaclass__ = 'javax/imageio/ImageIO'
    read = JavaMethod('(Ljava/io/File;)Ljava/awt/image/BufferedImage;')


def test_color_layout(im):
    print ""
    print "Color Layout:"
    colorlay = ColorLayout()
    colorlay.extract(im)
    print colorlay.getStringRepresentation()
    print Base64.encodeBase64String(
        colorlay.getByteArrayRepresentation())

def test_edge_histogram(im):
    print ""
    print "Edge Histogram:"
    edgehist = EdgeHistogram()
    edgehist.extract(im)
    print edgehist.getStringRepresentation()
    print Base64.encodeBase64String(
        edgehist.getByteArrayRepresentation())

def test_PHOG(im):
    print ""
    print "PHOG:"
    phog = PHOG()
    phog.extract(im)
    print phog.getStringRepresentation()
    print Base64.encodeBase64String(
        phog.getByteArrayRepresentation())

def test_opponent_histogram(im):
    print ""
    print "Opponent Histogram:"
    opphist = OpponentHistogram()
    opphist.extract(im)
    print opphist.getStringRepresentation()
    print Base64.encodeBase64String(
        opphist.getByteArrayRepresentation())

def test_JCD(im):
    print ""
    print "JCD:"
    jcd = JCD()
    jcd.extract(im)
    print jcd.getStringRepresentation()
    print Base64.encodeBase64String(
        jcd.getByteArrayRepresentation())

def main():
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
        print "IMAGE: %s" % basename(im_pth)
        test_color_layout(im)
        test_edge_histogram(im)
        #test_PHOG(im)
        test_opponent_histogram(im)
        #test_JCD(im)
        print "-" * 120

if __name__ == "__main__":
    main()
