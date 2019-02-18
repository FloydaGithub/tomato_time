import sublime
import sublime_plugin
import os, time

from .utils import log
from .config import TOMATO_TIME, TICK_TIME

tomato_singleton = None


def plugin_loaded():
    tomato = get_tomato()
    tomato.check_cache_time()


class Storage():
    def __init__(self):
        self.cache_path = os.path.join(sublime.cache_path(), 'User',
                                       'tomato_time.cache')

    def save_time(self, time_str=str(time.time())):
        try:
            log.debug('save_time: %s' % time_str)
            fp = open(self.cache_path, 'w+')
            fp.write(time_str)
            fp.close()
        except:
            sublime.error_message("Cann't save current time to local.")

    def load_time(self):
        try:
            fp = open(self.cache_path)
            time_str = fp.read()
            fp.close()
            log.debug('load_time: %s' % time_str)
            return time_str
        except:
            fp = open(self.cache_path, "w+")
            fp.close()
            return None

    def clear_time(self):
        log.debug('=========== clear_time ===========')
        self.save_time('0')


class Tomato(Storage):
    def __init__(self):
        super(Tomato, self).__init__()
        self.counter = 0
        self.actived = False
        self.status_visiable = True

    def is_actived(self):
        return self.actived

    def tick(self):
        if not self.actived:
            return
        self.counter += TICK_TIME
        self.show_progress()
        if self.counter >= TOMATO_TIME:
            self.finish()

    def start(self, last_time=0):
        if last_time == 0:
            self.save_time()
        self.counter = last_time
        self.actived = True
        self.set_status_visiable(True)
        log.info('start')

    def stop(self):
        self.clear_time()
        self.counter = 0
        self.actived = False
        self.set_status_visiable(False)

    def finish(self):
        self.stop()
        sublime.message_dialog('Finish Tomato Time')
        log.info('finish')

    def discard(self):
        self.stop()
        sublime.message_dialog('Discard Tomato Time')
        log.info('discard')

    def set_status_visiable(self, flag):
        self.status_visiable = flag
        self.show_progress()

    def get_status_visiable(self):
        return self.status_visiable

    def show_progress(self):
        if self.status_visiable is False:
            sublime.status_message('')
            return
        progress = int(self.counter / TOMATO_TIME * 100)
        msg = '|' + progress * '-' + 'o' + (100 - progress) * '-' + '|'
        sublime.status_message(msg)

    def check_cache_time(self):
        last_time = self.load_time()
        try:
            last_time = float(last_time)
        except:
            self.clear_time()
            return

        cur_time = time.time()
        delta = cur_time - last_time
        log.debug('delta: %s' % delta)
        if delta >= TOMATO_TIME:
            self.clear_time()
        else:
            self.start(int(delta))


def get_tomato():
    global tomato_singleton
    if not tomato_singleton:
        tomato_singleton = Tomato()
    return tomato_singleton


class CreateTomatoCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        tomato = get_tomato()
        tomato.start()

    def is_visible(self):
        return True


class DiscardTomatoCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        tomato = get_tomato()
        tomato.discard()

    def is_visible(self):
        tomato = get_tomato()
        return tomato.is_actived()


class ShowTomatoProgressCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        tomato = get_tomato()
        tomato.set_status_visiable(True)

    def is_visible(self):
        tomato = get_tomato()
        return tomato.is_actived() and not tomato.get_status_visiable()


class HideTomatoProgressCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        tomato = get_tomato()
        tomato.set_status_visiable(False)

    def is_visible(self):
        tomato = get_tomato()
        return tomato.is_actived() and tomato.get_status_visiable()
