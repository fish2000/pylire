import jnius
jnius.autoclass('java.lang.System')
# <class 'jnius.reflect.java.lang.System'>
javasys = jnius.autoclass('java.lang.System')
javasys.getProperty('java.class.path')
# '/Users/fish/Praxa/TESSAR:/Users/fish/Praxa/TESSAR/lib/python2.7/site-packages/jnius/src'
javasys.setProperty('java.class.path', "%(cp)s:%(lib)s/commons-codec-1.9.jar:%(lib)s/lire.jar" % dict(cp=javasys.getProperty('java.class.path'), lib="/Users/fish/Praxa/TESSAR/java/lire-solr/lib"))
# '/Users/fish/Praxa/TESSAR:/Users/fish/Praxa/TESSAR/lib/python2.7/site-packages/jnius/src'
javasys.getProperty('java.class.path')
# '/Users/fish/Praxa/TESSAR:/Users/fish/Praxa/TESSAR/lib/python2.7/site-packages/jnius/src:/Users/fish/Praxa/TESSAR/java/lire-solr/lib/commons-codec-1.9.jar:/Users/fish/Praxa/TESSAR/java/lire-solr/lib/lire.jar'
GZIPOutputStream = jnius.autoclass('java.util.zip.GZIPOutputStream')
ObjectOutputStream = jnius.autoclass('java.io.ObjectOutputStream')
File = jnius.autoclass('java.io.File')
FileOutputStream = jnius.autoclass('java.io.FileOutputStream')
from pylire.process.bitsampling import BITS
BITS.shape
# (100, 12, 640)
BITS[0, 0, 0]
# -0.28615448557956791
oortcloud = ObjectOutputStream(GZIPOutputStream(FileOutputStream(File('/tmp/iheardyoulikeboxedvalues.obj'))))
from pylire.process.bitsampling import NUM_BITS, NUM_DIMENSIONS, NUM_FUNCTION_BUNDLES
oortcloud.writeInt(NUM_BITS)
oortcloud.writeInt(NUM_DIMENSIONS)
oortcloud.writeInt(NUM_FUNCTION_BUNDLES)
BITS.flatten()[0]
# -0.28615448557956791

for floater in BITS.flatten():
    oortcloud.writeFloat(floater)


oortcloud.flush()
oortcloud.close()
# quit()
