import sublime
import sublime_plugin
import os, time, json

from .utils import log
from .config import TOMATO_TIME, TICK_TIME, DEBUG

tomato_singleton = None


class Setting():
    def __init__(self):
        self.settings = sublime.load_settings('tomato_time.sublime-settings')


class Storage():
    def __init__(self):
        self.cache_path = os.path.join(sublime.cache_path(), 'User',
                                       'tomato_time.cache')
        self.records_path = os.path.join(sublime.cache_path(), 'User',
                                         'tomato_time_records.cache')
        
        self.desc = ''
        self.tag = None

    def set_desc(self, desc):
        self.desc = desc

    def set_tag(self, tag):
        self.tag = tag

    def save_json(self, path, content='{}'):
        try:
            fp = open(path, 'w+')
            fp.write(content)
            fp.close()
        except:
            sublime.error_message("Cann't save to local.")

    def load_json(self, path):
        try:
            fp = open(path)
            content = fp.read()
            fp.close()
            return json.loads(content)
        except:
            self.save_json(path)
            self.clear_cache()
            return {}

    def save_cache(self):
        cache = {}
        cache['last_time'] = str(time.time())
        cache['desc'] = self.desc
        cache['tag'] = self.tag
        log.debug(cache)
        self.save_json(self.cache_path, json.dumps(cache))

    def load_cache(self):
        return self.load_json(self.cache_path)

    def clear_cache(self):
        self.save_json(self.cache_path)

    def parse_records(self):
        self.records = self.load_json(self.records_path)

    def create_records(self, content):
        localtime = time.localtime()
        date = time.strftime('%Y-%m-%d', localtime)
        _time = time.strftime('%H:%M', localtime)
        self.records[date] = self.records.get(date, [])
        self.records[date].append('%s %s' % (_time, content))
        log.debug(self.records)
        self.save_json(self.records_path, json.dumps(self.records))

    def show_records(self):
        window = sublime.active_window()
        view = window.new_file()
        view.set_name('Tomato Time Records')
        view.set_scratch(True)
        view.settings().set("word_wrap", True)
        view.settings().set("auto_indent", False)
        view.settings().set("tab_width", 4)
        view.set_syntax_file('Packages/Markdown/Markdown.sublime-syntax')

        def write(c):
            view.run_command('insert', {'characters': c})

        write('# Tomato Time Records\n')
        for date in [v for v in sorted(self.records.keys())]:
            write('\n## %s\n' % date)
            for content in self.records.get(date):
                write('  + %s\n' % content)

    def clear_records(self):
        self.save_json(self.records_path)


class Tomato(Storage):
    def __init__(self):
        super(Tomato, self).__init__()
        self.counter = 0
        self.actived = False
        self.status_visiable = True
        self.parse_records()

    def is_actived(self):
        return self.actived

    def tick(self):
        if not self.actived:
            return
        self.counter += TICK_TIME
        self.show_progress()

        if DEBUG and self.counter > 5:
            self.finish()
            return
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
        if self.tag:
            self.create_records('*%s* %s' % (self.tag, self.desc))
        else:
            self.create_records('%s' % (self.desc))
        self.tag = None
        log.info('finish')
        sublime.message_dialog('Finish Tomato Time: %s' % self.desc)

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
        log.debug(cache)
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
            self.set_tag(cache.get('tag'))
            self.start(int(delta))


def get_tomato():
    global tomato_singleton
    if not tomato_singleton:
        tomato_singleton = Tomato()
    return tomato_singleton


class CreateTomatoCommand(sublime_plugin.TextCommand):
    def show_desc_panel(self):
        window = sublime.active_window()
        caption = 'Tomato Time Description:'

        def on_done(desc):
            tomato = get_tomato()
            tomato.set_desc(desc)
            tomato.set_tag(self.tag)
            tomato.start()

        window.show_input_panel(caption, '', on_done, None, None)

    def create_tag(self):
        pass

    def delete_tag(self):
        pass

    def show_tags_panel(self):
        window = sublime.active_window()

        items = [
            'Discard Tag',
            'Create Tag',
            'Delete Tag',
        ]
        tags = [
            'Fightint',
            'WayaGame',
        ]
        for t in tags:
            items.append('>>> %s' % t)

        def on_select(index):
            if index < 0:
                return
            if index == 0:
                self.show_desc_panel()
                return
            if index == 1:
                self.create_tag()
                return
            if index == 2:
                self.delete_tag()
                return
            self.tag = tags[index - 3]
            self.show_desc_panel()

        window.show_quick_panel(items, on_select)

    def run(self, edit):
        self.tag = None
        self.show_tags_panel()


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


class ShowCompleteRecordsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        tomato = get_tomato()
        tomato.show_records()


class ClearCompleteRecordsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        tomato = get_tomato()
        tomato.clear_records()
        tomato.parse_records()
