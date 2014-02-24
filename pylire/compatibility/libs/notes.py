from net.semanticmetadata.lire.imageanalysis import PHOG
from net.semanticmetadata.lire.imageanalysis import OpponentHistogram
from javax.imageio import ImageIO
from java.io import File
from os.path import expanduser
img = ImageIO.read(File(expanduser('~/Downloads/5717314638_2340739e06_b.jpg')))
img
import jarray
ImageUtils.getGrayscaleImage(img)
gray = ImageUtils.getGrayscaleImage(img)
print jarray.zeros(256, 'd')
img.width
img.height
img.getWidth()
img.getHeight()
jarray.zeros(gray.height)
jarray.zeros(gray.height, 'd')
harray = jarray.zeros(gray.height, 'd')
from net.semanticmetadata.lire.utils import ImageUtils
from net.semanticmetadata.lire.indexing.hashing import BitSampling