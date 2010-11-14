#  Copyright (c) 2009-2010, Cloud Matrix Pty. Ltd.
#  All rights reserved; available under the terms of the BSD License.

import os
import sys
setup_kwds = {}
if sys.version_info > (3,):
    from setuptools import setup
    setup_kwds["test_suite"] = "PySideKick.tests"
    setup_kwds["use_2to3"] = True
else:
    from distutils.core import setup

#  This awfulness is all in aid of grabbing the version number out
#  of the source code, rather than having to repeat it here.  Basically,
#  we parse out all lines starting with "__version__" and execute them.
try:
    next = next
except NameError:
    def next(i):
        return i.next()
info = {}
try:
    src = open("PySideKick/__init__.py")
    lines = []
    ln = next(src)
    while "__version__" not in ln:
        lines.append(ln)
        ln = next(src)
    while "__version__" in ln:
        lines.append(ln)
        ln = next(src)
    exec("".join(lines),info)
except Exception:
    pass


#  Screw the MANIFEST file, it just caches out of date data and messes
#  up my builds.
mfst = os.path.join(os.path.dirname(__file__),"MANIFEST")
if os.path.exists(mfst):
    os.unlink(mfst)


NAME = "PySideKick"
VERSION = info["__version__"]
DESCRIPTION = "helpful utils for working with PySide"
AUTHOR = "Ryan Kelly"
AUTHOR_EMAIL = "rfk@cloudmatrix.com.au"
URL = "http://github.com/cloudmatrix/pysidekick/"
LICENSE = "BSD"
KEYWORDS = "GUI Qt PySide"
LONG_DESC = info["__doc__"]

PACKAGES = ["PySideKick","PySideKick.tests"]
EXT_MODULES = []
PKG_DATA = {}

setup(name=NAME,
      version=VERSION,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      url=URL,
      description=DESCRIPTION,
      long_description=LONG_DESC,
      keywords=KEYWORDS,
      packages=PACKAGES,
      ext_modules=EXT_MODULES,
      package_data=PKG_DATA,
      license=LICENSE,
      **setup_kwds
     )

