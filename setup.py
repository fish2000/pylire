#/usr/bin/env python

try:
    from setuptools import setup, Extension
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, Extension

def cython_module(*args):
    ext_package = ".".join(args)
    ext_pth = "/".join(args) + ".pyx"
    return Extension(ext_package, [ext_pth])

def cython_ext(name):
    return cython_module('pylire', 'process', 'ext', name)

from Cython.Distutils import build_ext
from distutils.sysconfig import get_python_inc

try:
    import numpy
except ImportError:
    class FakeNumpy(object):
        def get_include(self):
            return "."
    numpy = FakeNumpy()

setup(
    name='pylire',
    version='0.1.8',
    description='Python/Cython port of Lire image processing algorithms',
    author='Alexander Bohn',
    author_email='fish2000@gmail.com',
    maintainer='Alexander Bohn',
    maintainer_email='fish2000@gmail.com',
    license='GPLv2',
    url='http://github.com/fish2000/pylire/',
    zip_safe=False,
    
    #setup_requires=['cython'],
    install_requires=[
        'numpy',
        'numexpr',
        'imread',
        'scikit-image'],
    
    packages=[
        'pylire',
        'pylire.compatibility',
        'pylire.process',
        'pylire.process.ext',
    ],
    
    package_data={
        'pylire': [
            'process/bits/*.h5',
            'compatibility/libs/*.jar',
        ],
    },
    
    scripts={
        'bin/jython-pylire': 'jython-pylire',
    },
    
    ext_modules=[
        cython_ext("grayscale"),
        cython_ext("opponent_histogram")],
    
    cmdclass=dict(build_ext=build_ext),
    include_dirs=[
        numpy.get_include(),
        get_python_inc(plat_specific=1),
        "."],
    
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities']
)

