#  Copyright (c) 2009-2010, Cloud Matrix Pty. Ltd.
#  All rights reserved; available under the terms of the BSD License.
"""

PySideKick:  helpful utilities for working with PySide
======================================================


This package is a rather ad-hoc collection of helpers, utilities and custom
widgets for building applications with PySide.  So far we have:

  * PySideKick.Call:  helpers for calling functions in a variety of ways,
                      e.g. qCallAfter, qCallInMainThread

  * PySideKick.Console:   a simple interactive console to embed in your
                          application

"""

__ver_major__ = 0
__ver_minor__ = 1
__ver_patch__ = 0
__ver_sub__ = ""
__ver_tuple__ = (__ver_major__,__ver_minor__,__ver_patch__,__ver_sub__)
__version__ = "%d.%d.%d%s" % __ver_tuple__


import thread

from PySide import QtCore, QtGui
from PySide.QtCore import Qt


#  I can't work out how to extract the main thread from a running PySide app.
#  Until then, we assue that whoever imports this module is the main thread.
_MAIN_THREAD_ID = thread.get_ident()

