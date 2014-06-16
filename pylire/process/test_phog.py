
from pylire.process.PHOG import hog
from pylire.compatibility.utils import print_array_info

def main(pth):
    from pylire.compatibility.utils import timecheck
    from pylire.process.channels import RGB
    from imread import imread
    
    im = imread(pth)
    (R, G, B) = RGB(im)
    
    @timecheck
    def timetest_cythonized_HOG(ndim):
        hogg = hog(ndim)
        print("Cythonized HOG() function:")
        print_array_info(hogg)
        print("")
    
    timetest_cythonized_HOG(im)
    
    '''
    @timecheck
    def timetest_naive_PHOG(R, G, B):
        phog = PHOG(R, G, B)
        print("naive Lire port (raw PHOG histo):")
        print_array_info(phog)
        print("")
    
    timetest_naive_PHOG(R, G, B)'''

if __name__ == '__main__':
    
    #import sys
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
        #sys.exit(0)


