#!/usr/bin/env jython

from net.semanticmetadata.lire.imageanalysis import ColorLayout
from net.semanticmetadata.lire.imageanalysis import EdgeHistogram
from net.semanticmetadata.lire.imageanalysis import PHOG
from net.semanticmetadata.lire.imageanalysis import OpponentHistogram
from net.semanticmetadata.lire.imageanalysis import JCD

from net.semanticmetadata.lire.indexing.hashing import BitSampling
from net.semanticmetadata.lire.solr import ParallelSolrIndexer

from org.apache.commons.codec.binary import Base64
from javax.imageio import ImageIO
from java.io import File


def test_color_layout(im, silence=False):
    """ Testing: color layout """
    if not silence:
        print ""
        print "Color Layout:"
    colorlay = ColorLayout()
    colorlay.extract(im)
    return (
        colorlay.getStringRepresentation(),
        Base64.encodeBase64String(
            colorlay.getByteArrayRepresentation()),
        ParallelSolrIndexer.arrayToString(
            BitSampling.generateHashes(
                colorlay.getDoubleHistogram())))

def test_edge_histogram(im, silence=False):
    """ Testing: edge histogram """
    if not silence:
        print ""
        print "Edge Histogram:"
    edgehist = EdgeHistogram()
    edgehist.extract(im)
    return (
        edgehist.getStringRepresentation(),
        Base64.encodeBase64String(
            edgehist.getByteArrayRepresentation()),
        ParallelSolrIndexer.arrayToString(
            BitSampling.generateHashes(
                edgehist.getDoubleHistogram())))

def test_PHOG(im, silence=False):
    """ Testing: Pyramidal Histogram of Gradient (PHOG) Descriptor """
    if not silence:
        print ""
        print "PHOG:"
    phog = PHOG()
    phog.extract(im)
    return (
        phog.getStringRepresentation(),
        Base64.encodeBase64String(
            phog.getByteArrayRepresentation()),
        ParallelSolrIndexer.arrayToString(
            BitSampling.generateHashes(
                phog.getDoubleHistogram())))

def test_opponent_histogram(im, silence=False):
    """ Testing: opponent histogram """
    # sb.append(arrayToString(BitSampling.generateHashes(feature.getDoubleHistogram())));
    if not silence:
        print ""
        print "Opponent Histogram:"
    opphist = OpponentHistogram()
    opphist.extract(im)
    return (
        opphist.getStringRepresentation(),
        Base64.encodeBase64String(
            opphist.getByteArrayRepresentation()),
        ParallelSolrIndexer.arrayToString(
            BitSampling.generateHashes(
                opphist.getDoubleHistogram())))

def test_JCD(im, silence=False):
    """ Testing: Joint Color Descriptor (JCD) """
    if not silence:
        print ""
        print "JCD:"
    jcd = JCD()
    jcd.extract(im)
    return (
        jcd.getStringRepresentation(),
        Base64.encodeBase64String(
            jcd.getByteArrayRepresentation()),
        ParallelSolrIndexer.arrayToString(
            BitSampling.generateHashes(
                jcd.getDoubleHistogram())))

def main():
    """ Run all tests """
    from os.path import expanduser, join
    from os import listdir
    
    # Load test images
    im_directory = expanduser("~/Downloads")
    im_paths = map(
        lambda name: join(im_directory, name),
        filter(
            lambda name: name.lower().endswith('jpg'),
            listdir(im_directory)))
    
    # Load bit-hashing functions
    BitSampling.readHashFunctions()
    #readable_values(im_paths)
    json_encoded_values(im_paths)

def readable_values(im_paths):
    from os.path import basename
    
    for im_pth in im_paths:
        im = ImageIO.read(File(im_pth))
        print ""
        print "-" * 120
        print ""
        print "IMAGE: %s" % basename(im_pth)
        
        for histoval in test_color_layout(im):
            print histoval
        
        for histoval in test_edge_histogram(im):
            print histoval
        
        #for histoval in test_PHOG(im):
        #   print histoval
        
        for histoval in test_opponent_histogram(im):
            print histoval
        
        #for histoval in test_JCD(im):
        #   print histoval
        
        print ""
        #print "-" * 120


def json_encoded_values(im_paths):
    import simplejson as json
    
    list_of_dicts = []
    list_of_names = ('string', 'base64', 'hash')
    
    for im_pth in im_paths:
        im = ImageIO.read(File(im_pth))
        
        list_of_dicts.append(dict(
            color_layout=dict(
                zip(list_of_names,
                    test_color_layout(im, silence=True))),
            
            edge_histogram=dict(
                zip(list_of_names,
                    test_edge_histogram(im, silence=True))),
            
            #phog=dict(
            #    zip(list_of_names,
            #       test_PHOG(im, silence=True))),
            
            opponent_histogram=dict(
                zip(list_of_names,
                    test_opponent_histogram(im, silence=True))),
            
            #jcd=dict(
            #    zip(list_of_names,
            #       test_JCD(im, silence=True))),
        ))
    
    print json.dumps(list_of_dicts, indent=4)


if __name__ == "__main__":
    main()
