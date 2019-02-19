import sublime
import sublime_plugin
import os, time, json

from .utils import log
from .config import TOMATO_TIME, TICK_TIME

tomato_singleton = None


class Storage():
    def __init__(self):
        self.cache_path = os.path.join(sublime.cache_path(), 'User',
                                       'tomato_time.cache')

    def save_cache(self, time_str=str(time.time())):
        cache = {}
        cache['last_time'] = time_str
        cache['desc'] = self.desc
        try:
            fp = open(self.cache_path, 'w+')
            fp.write(json.dumps(cache))
            fp.close()
        except:
            sublime.error_message("Cann't save current time to local.")

    def load_cache(self):
        try:
            fp = open(self.cache_path)
            cache = fp.read()
            fp.close()
            log.debug(cache)
            return json.loads(cache)
        except:
            self.clear_cache()
            return None

    def clear_cache(self):
        try:
            fp = open(self.cache_path, 'w+')
            fp.write('{}')
            fp.close()
        except:
            sublime.error_message("Cann't save current time to local.")


class Tomato(Storage):
    def __init__(self):
        super(Tomato, self).__init__()
        self.desc = ''
        self.counter = 0
        self.actived = False
        self.status_visiable = True

    def set_desc(self, desc):
        self.desc = desc

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
            self.save_cache()
        self.counter = last_time
        self.actived = True
        self.set_status_visiable(True)
        log.info('start')

    def stop(self):
        self.clear_cache()
        self.counter = 0
        self.actived = False
        self.set_status_visiable(False)

    def finish(self):
        self.stop()
        sublime.message_dialog('Finish Tomato Time: %s' % self.desc)
        log.info('finish')

    def discard(self):
        self.stop()
        sublime.message_dialog('Discard Tomato Time: %s' % self.desc)
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
        cache = self.load_cache()
        try:
            last_time = float(cache.get('last_time'))
        except:
            self.clear_cache()
            return

        cur_time = time.time()
        delta = cur_time - last_time
        log.debug('delta: %s' % delta)
        if delta >= TOMATO_TIME:
            self.clear_cache()
        else:
            self.set_desc(cache.get('desc'))
            self.start(int(delta))


def get_tomato():
    global tomato_singleton
    if not tomato_singleton:
        tomato_singleton = Tomato()
    return tomato_singleton


class CreateTomatoCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        def on_done(desc):
            tomato = get_tomato()
            tomato.set_desc(desc)
            tomato.start()

        window = sublime.active_window()
        caption = 'Tomato Time Description:'
        window.show_input_panel(caption, '', on_done, None, None)

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
