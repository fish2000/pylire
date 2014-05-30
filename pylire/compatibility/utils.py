#!/usr/bin/env python
from __future__ import print_function

import sys
import time
import codecs
import numpy
from pprint import pformat
from functools import wraps

BREAKER = 60
CODEC = 'iso-8859-1'

def print_array_info(in_array, title=None):
    sout = codecs.getwriter(CODEC)(sys.stdout)
    this_array = numpy.array(in_array)
    
    def tprint(string):
         print(string, file=sout)
    
    def tpprint(obj):
        tprint(pformat(obj, indent=4))
    
    def tbreak(char='-'):
        tprint(char * (BREAKER - 8))
    
    if title is not None:
        tprint(""" %s:      """ % title)
    
    tprint("""
%s
""" % (
        numpy.array2string(
            this_array,
            prefix='',
            max_line_width=BREAKER
        )))
    
    shape = getattr(this_array, 'shape', tuple())
    dtype = getattr(this_array, 'dtype', numpy.dtype(None))
    
    tprint("""
  shape: %s
  dtype: %s [%s] %s
  max: %s min: %s average: %s
        """ % (
            str(shape),
            str(dtype.name),
            str(dtype.char),
            
                ", ".join([
                    "(%s)" % ", ".join(
                        desc for desc in descr if desc
                    ) for descr in dtype.descr if descr
                ]),
            
            numpy.max(this_array),
            numpy.min(this_array),
            numpy.average(this_array),
        ))

def timecheck(f):
    sout = codecs.getwriter(CODEC)(sys.stdout)
    fname = getattr(f, "__name__", "<unnamed>")
    
    def tprint(string):
         print(string, file=sout)
    
    def tpprint(obj):
        tprint(pformat(obj, indent=4))
    
    def tbreak(char='-'):
        tprint(char * BREAKER)
    
    @wraps(f)
    def timer(*args, **kwargs):
        tprint("\n")
        tbreak("=")
        tprint("- %s" % time.strftime("%A %B %d -- %I:%M %p (%Z)"))
        tbreak()
        tprint("+ TESTING: %s()" % fname)
        tprint("\n")
        
        out = None
        t1 = time.time()
        out = f(*args, **kwargs)
        t2 = time.time()
        dt = str((t2 - t1) * 1.00)
        dtout = dt[:(dt.find(".") + 4)]
        
        tbreak()
        if out is not None:
            tprint('')
            tprint('+ RESULTS:')
            tprint('')
            if isinstance(out, numpy.ndarray):
                print_array_info(out)
            else:
                tpprint(out)
            tprint('')
        tprint('- Test finished in %ss' % dtout)
        tbreak("=")
        tprint("\n")
        return out
    return timer
