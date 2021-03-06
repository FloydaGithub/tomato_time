import sys
import os
from imp import reload
from .libs import log
from .tomato_time import get_tomato
from .config import TICK_TIME

import threading
import time
import inspect
import ctypes

dirname = os.path.split(os.path.dirname(__file__))[1]

all_modules = [
    "config",
    "command",
    "tomato_time",
    "libs.log",
    "libs.resource",
    "libs.storage",
]


def reload_module():
    for module in all_modules:
        name = "%s.%s" % (dirname, module)
        reload(sys.modules[name])
    stop_thread(main_thread)


def plugin_loaded():
    log.debug("---------- plugin_loaded ----------")
    reload_module()
    start_thread()
    tomato = get_tomato()
    tomato.check_cache_time()


def plugin_unloaded():
    log.debug("---------- plugin_unloaded ----------")
    stop_thread(main_thread)


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    pyobj = ctypes.py_object(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, pyobj)
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def start_thread():
    log.debug("start thread")
    main_thread.start()


def stop_thread(thread):
    try:
        _async_raise(thread.ident, SystemExit)
        log.debug("stop thread")
    except Exception:
        log.debug("stop thread failed")


class Tick(threading.Thread):
    def run(self):
        while True:
            time.sleep(TICK_TIME)
            tomato = get_tomato()
            tomato.tick()


main_thread = Tick()
