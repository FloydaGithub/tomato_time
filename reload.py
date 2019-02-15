import sys
import os
from imp import reload

dirname = os.path.split(os.path.dirname(__file__))[1]

all_modules = [
    'tomato_time',
]


def reload_module():
    for module in all_modules:
        name = '%s.%s' % (dirname, module)
        reload(sys.modules[name])
    stop_thread(main_thread)


def plugin_loaded():
    print('---------- plugin_loaded -----------')
    reload_module()
    start_thread()


def plugin_unloaded():
    print('---------- plugin_unloaded -----------')
    stop_thread(main_thread)


import threading
import time
import inspect
import ctypes


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid,
                                                     ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def start_thread():
    print('start thread')
    main_thread.start()


def stop_thread(thread):
    try:
        _async_raise(thread.ident, SystemExit)
        print('stop thread')
    except:
        print('stop thread failed')
        pass


class Tick(threading.Thread):
    def test(self):
        from .tomato_time import TOMATO_TIME
        print('-------------', TOMATO_TIME)

    def run(self):
        while True:
            self.test()
            time.sleep(1)


main_thread = Tick()
