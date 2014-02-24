#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import zipfile
import tempfile
import pylire
import shutil
import sys

from clint.textui import progress, colored
from clint.textui import puts, indent
from argh import ArghParser, arg
from os.path import join, dirname, basename, isfile

_copy = shutil.copy2

def jarpath(jar):
    pth = join(
        dirname(pylire.__file__),
        "compatibility", "libs", jar)
    return isfile(pth) and pth or ''


def oort(oortpath, jnius):
    GZIPOutputStream = jnius.autoclass('java.util.zip.GZIPOutputStream')
    ObjectOutputStream = jnius.autoclass('java.io.ObjectOutputStream')
    File = jnius.autoclass('java.io.File')
    FileOutputStream = jnius.autoclass('java.io.FileOutputStream')
    
    from pylire.process.bitsampling import BITS
    from pylire.process.bitsampling import NUM_BITS, NUM_DIMENSIONS, NUM_FUNCTION_BUNDLES
    
    puts(colored.cyan("Writing HDF5 data to ObjectOutputStream..."))
    
    oortcloud = ObjectOutputStream(
        GZIPOutputStream(
            FileOutputStream(
                File(oortpath))))
    
    oortcloud.writeInt(NUM_BITS)
    oortcloud.writeInt(NUM_DIMENSIONS)
    oortcloud.writeInt(NUM_FUNCTION_BUNDLES)
    
    with indent(4, quote='+ '):
        puts(colored.red("(int) NUM_BITS: %d" % NUM_BITS))
        puts(colored.red("(int) NUM_DIMENSIONS: %d" % NUM_DIMENSIONS))
        puts(colored.red("(int) NUM_FUNCTION_BUNDLES: %d" % NUM_FUNCTION_BUNDLES))
    
        for floatval in progress.bar(BITS.flatten(),
            label=colored.red("(float) BITS")):
            oortcloud.writeFloat(floatval)
    
    oortcloud.flush()
    oortcloud.close()


def rejar(jarpth, fresh_content_map={}, compression=zipfile.ZIP_DEFLATED):
    if not isfile(jarpth):
        raise IOError("No jar: %s" % jarpth)
    
    puts(colored.cyan("Re-jarring '%s' with %d possible replacements:" % (
        basename(jarpth),
        len(fresh_content_map))))
    
    with indent(3, quote=' *'):
        for fresh_key in fresh_content_map.keys():
            puts(colored.cyan(fresh_key))
    
    print()
    
    oldjar = zipfile.ZipFile(jarpth, mode='r')
    newjar = zipfile.ZipFile(
        tempfile.mktemp(suffix='.zip'),
        mode='w', compression=compression)
    
    for item in progress.bar(oldjar.infolist(),
        label=colored.cyan(
            "Re-jar: %s" % basename(jarpth))):
        replace = basename(item.filename) in fresh_content_map
        content = replace \
            and fresh_content_map[basename(item.filename)] \
            or oldjar.read(item.filename)
        replace and puts(colored.yellow("Replaced %s" % item.filename))
        newjar.writestr(item, content)
    
    print ()
    oldjarpth = oldjar.filename
    newjarpth = newjar.filename
    oldjar.testzip()
    oldjar.close()
    shutil.move(oldjar.filename, oldjar.filename+".backup")
    
    newjar.testzip()
    newjar.close()
    _copy(newjarpth, oldjarpth)
    
    puts(colored.yellow("Finished restructuring jar: %s" % oldjarpth))
    print()


def setup_jvm():
    puts(colored.yellow("Starting JVM..."))
    print()
    
    import jnius
    
    javasys = jnius.autoclass('java.lang.System')
    classpath = javasys.getProperty('java.class.path')
    
    puts(colored.cyan("Classpath:"))
    puts(colored.cyan(classpath))
    print()
    
    amended_cp = ":".join([
        classpath,
        jarpath('commons-codec-1.9.jar'),
        jarpath('lire.jar'),
    ])
    
    javasys.setProperty('java.class.path', amended_cp)
    
    puts(colored.cyan("Classpath (amended):"))
    puts(colored.cyan(amended_cp))
    print()
    
    return jnius


@arg('FILE',
    default="LshBitSampling.obj", nargs='?',
    help="Path to which the Java ObjectOutputStream will be serialized")
def write(args):
    if isfile(args.FILE):
        raise IOError("File already exists: %s" % args.FILE)
    
    jnius = setup_jvm()
    oort(args.FILE, jnius)
    return

@arg('JAR',
    default=None,
    help="Zipped file to which the Java ObjectOutputStream will be serialized")
@arg('FILE',
    default="/tmp/LshBitSampling.obj", nargs='?',
    help="Zipped file to which the Java ObjectOutputStream will be serialized")
def inject(args):
    if args.JAR is None:
        raise IOError("You must specify a *.jar archive for hash injection")
    if args.FILE is None:
        args.FILE = "/tmp/LshBitSampling.obj"
    if isfile(args.FILE):
        raise IOError("File already exists: %s" % args.FILE)
    
    jnius = setup_jvm()
    oort(args.FILE, jnius)
    
    if not isfile(args.FILE):
        raise IOError("Failed to serialize Java data to file: %s" % args.FILE)
    
    with open(args.FILE, 'rb') as javadata:
        rejar(args.JAR, fresh_content_map={
            basename(args.FILE): javadata.read()
        })
    return


def main(*argv):
    arguments = list(argv and argv or sys.argv[1:])
    parser = ArghParser()
    parser.add_commands([write, inject])
    #parser.set_default_command(write)
    parser.dispatch(argv=list(arguments))
    return 0

if __name__ == '__main__':
    main('write')
    #main('write', "/Users/fish/Desktop/yodogg-I-like-hash-functions.obj")
    #main('inject', '/tmp/lire.jar')