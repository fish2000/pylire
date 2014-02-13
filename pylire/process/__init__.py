
from __future__ import print_function

from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

from importlib import import_module
from functools import wraps
import inspect
import sys

MAKE_NOISE = False

def external(f):
    """ Decorator that looks for an external version of
        the decorated function -- if one is found and
        imported, it replaces the decorated function
        in-place (and thus transparently, to would-be
        users of the code). """
    f.__external__ = 0 # Mark func as non-native
    
    function_name = hasattr(f, 'func_name') and f.func_name or f.__name__
    module_name = inspect.getmodule(f).__name__
    
    # Always return the straight decoratee func,
    # whenever something goes awry. 
    if not function_name or not module_name:
        MAKE_NOISE and print("Bad function or module name (respectively, %s and %s)" % (
            function_name, module_name), file=sys.stderr)
        return f
    
    module_file_name = module_name.split('.')[-1]
    module_name = "pylire.process.ext.%s" % module_file_name
    
    # Import the 'ext' version of process
    try:
        module = import_module(module_name)
    except ImportError:
        MAKE_NOISE and print("Error importing module (%s)" % (
            module_name,), file=sys.stderr)
        return f
    MAKE_NOISE and print("Using ext module: %s" % (
        module_name,), file=sys.stderr)
    
    # Get the external function with a name that
    # matches that of the decoratee.
    try:
        ext_function = getattr(module, function_name)
    except AttributeError:
        # no matching function in the ext module
        MAKE_NOISE and print("Ext function not found with name (%s)" % (
            function_name,), file=sys.stderr)
        return f
    except TypeError:
        # function_name was probably shit
        MAKE_NOISE and print("Bad name given for ext_function lookup (%s)" % (
            function_name,), file=sys.stderr)
        return f
    
    # Try to set telltale/convenience attributes
    # on the new external function -- this doesn't
    # always work, for more heavily encythoned
    # and cdef'd function examples.
    try:
        setattr(ext_function, '__external__', 1)
        setattr(ext_function, 'orig', f)
    except AttributeError:
        MAKE_NOISE and print("Bailing, failed setting ext_function attributes (%s)" % (
            function_name,), file=sys.stderr)
        return ext_function
    return wraps(f)(ext_function)
