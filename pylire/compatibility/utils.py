#!/usr/bin/env python
from __future__ import print_function

import sys
import time
import codecs
#from pprint import pprint
from functools import wraps

def test(f):
    sout = codecs.getwriter('iso-8859-1')(sys.stdout)
    fname = getattr(f, "__name__", "<unnamed>")
    
    def tprint(string):
         print(string, file=sout)
    
    @wraps(f)
    def timer(*args, **kwargs):
        tprint("\n")
        #print("==============================================================================")
        tprint("TESTING: %s()" % fname)
        tprint("------------------------------------------------------------------------------")
        tprint("\n")
        t1 = time.time()
        out = f(*args, **kwargs)
        t2 = time.time()
        dt = str((t2-t1)*1.00)
        dtout = dt[:(dt.find(".")+4)]
        tprint("------------------------------------------------------------------------------")
        # tprint('RESULTS:')
        # tprint('%s\n' % out)
        # pprint(out)
        tprint('Test finished in %ss' % dtout)
        tprint("==============================================================================")
        return out
    return timer
