#  Copyright (c) 2009-2010, Cloud Matrix Pty. Ltd.
#  All rights reserved; available under the terms of the BSD License.
"""

PySideKick:  helpful utilities for working with PySide
======================================================


This package is a rather ad-hoc collection of helpers, utilities and custom
widgets for building applications with PySide.  So far we have:

  * Helpers for calling functions in a variety of ways:

        qCallAfter, qCallLater, qCallInMainThread, qCallInWorkerThread

  * A method/function decorator that can ensure a function is always called
    using one of the above helpers:

        qCallUsing

  * A simple interactive console to embed in your application:

        Console.QPythonConsole

"""

__ver_major__ = 0
__ver_minor__ = 1
__ver_patch__ = 0
__ver_sub__ = ""
__ver_tuple__ = (__ver_major__,__ver_minor__,__ver_patch__,__ver_sub__)
__version__ = "%d.%d.%d%s" % __ver_tuple__


import sys
import thread
import threading
from functools import wraps
import Queue

from PySide import QtCore, QtGui
from PySide.QtCore import Qt


#  I can't work out how to extract the main thread from a running PySide app.
#  Until then, we assue that whoever imports this module is the main thread.
_MAIN_THREAD_ID = thread.get_ident()


class qCallAfter(QtCore.QObject):
    """Call the given function on a subsequent iteration of the event loop.

    This helper arranges for the given function to be called on a subsequent
    iteration of the main event loop.  It's most useful inside event handlers,
    where you may want to defer some work unti after the event has finished
    being processed.

    The implementation is as a singleton QObject subclass.  It maintains a
    queue of functions to the called, and posts an event to itself whenever
    a new function is queued.
    """
 
    def __init__(self):
        super(qCallAfter,self).__init__(None)
        self.app = None
        self.event_id = QtCore.QEvent.registerEventType()
        self.event_type = QtCore.QEvent.Type(self.event_id)
        self.pending_func_queue = Queue.Queue()
        self.func_queue = Queue.Queue()
 
    def customEvent(self,event):
        if event.type() == self.event_type:
            self._popCall()

    def __call__(self,func,*args,**kwds):
        if self.app is None:
            app = QtCore.QCoreApplication.instance()
            if app is None:
                self.pending_func_queue.put((func,args,kwds))
            else:
                self.app = app
                try:
                    while True:
                        self.func_queue.put(self.pending_func_queue.get(False))
                        self._postEvent()
                except Queue.Empty:
                    pass
                self.func_queue.put((func,args,kwds))
                self._postEvent()
        else:
            self.func_queue.put((func,args,kwds))
            self._postEvent()

    def _popCall(self):
        (func,args,kwds) = self.func_queue.get(False)
        func(*args,**kwds)

    def _postEvent(self):
        event = QtCore.QEvent(self.event_type)
        try:
            self.app.postEvent(self,event)
        except RuntimeError:
            #  This can happen if the app has been destroyed.
            #  Empty the queue.
            try:
                while True:
                    self._popCall()
            except Queue.Empty:
                pass

#  Things could get a little tricky here.  The object must belong to the
#  same thread as the QApplication.  For now we assume that this module
#  has been imported from the main thread.
qCallAfter = qCallAfter()



class Future(object):
    """Primative "future" class, for executing functions in another thread."""

    _READY_INSTANCES = []

    def __init__(self):
        self.ready = threading.Event()
        self.result = None
        self.exception = None

    @classmethod
    def get_or_create(cls):
        try:
            return cls._READY_INSTANCES.pop(0)
        except IndexError:
            return cls()

    def recycle(self):
        self.result = None
        self.exception = None
        self.ready.clear()
        self._READY_INSTANCES.append(self)

    def call_function(self,func,*args,**kwds):
        try:
            self.result = func(*args,**kwds)
        except Exception:
            self.exception = sys.exc_info()
        finally:
            self.ready.set()

    def get_result(self):
        self.ready.wait()
        try:
            if self.exception is None:
                return self.result
            else:
                raise self.exception[0], \
                      self.exception[1], \
                      self.exception[2]
        finally:
            self.recycle()


def qCallInMainThread(func,*args,**kwds):
    """Synchronosly call the given function in the main thread.

    This helper arranges for the given function to be called in the main
    event loop, then blocks and waits for the result.  It's a simple way to
    call functions that manipulate the GUI from a non-GUI thread.
    """
    try:
     if thread.get_ident() == _MAIN_THREAD_ID:
        func(*args,**kwds)
     else:
        future = Future.get_or_create()
        qCallAfter(future.call_function,func,*args,**kwds)
        return future.get_result()
    finally:


def qCallInWorkerThread(func,*args,**kwds):
    """Asynchronously call the given function in a background worker thread.

    This helper arranges for the given function to be executed by a background
    worker thread.  Eventually it'll get a thread pool; for now each task
    spawns a new background thread.

    If you need to know the result of the function call, this helper returns
    a Future object; use f.ready.isSet() to test whether it's ready and call
    f.get_result() to get the return value or raise the exception.
    """
    future = Future.get_or_create()
    def runit():
        future.call_function(func,*args,**kwds)
    threading.Thread(target=runit).start()
    return future


def qCallLater(interval,func,*args,**kwds):
    """Asynchronously call the given function after a timeout.

    This helper is similar to qCallAfter, but it waits at least 'interval'
    seconds before executing the function.  To cancel the call before the
    sleep interval has expired, call 'cancel' on the returned object.

    Currently this is a thin wrapper around threading.Timer; eventually it
    will be integrated with Qt's own timer mechanisms.
    """
    def runit():
        qCallAfter(func,*args,**kwds)
    t = threading.Timer(interval,runit)
    t.start()
    return t


def qCallUsing(helper):
    """Function/method decorator to always apply a function call helper.

    This decorator can be used to ensure that a function is always called
    using one of the qCall helpers.  For example, the following function can
    be safely called from any thread, as it will transparently apply the
    qCallInMainThread helper whenever it is called:

        @qCallUsing(qCallInMainThread)
        def prompt_for_input(msg):
            # ... pop up a dialog, return input

    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args,**kwds):
            return helper(func,*args,**kwds)
        return wrapper
    return decorator


