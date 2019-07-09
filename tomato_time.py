import sublime
import time

from .libs import log, storage
from .config import TOMATO_TIME, TICK_TIME, DEBUG

tomato_singleton = None


class TimestampCache(object):
    def __init__(self):
        super(TimestampCache, self).__init__()
        self._cache_timestamp = storage.StorageCache("tomato_time_timestamp")
        self._desc = self._cache_timestamp.get("desc", "")
        self._tag = self._cache_timestamp.get("tag", None)

    def set_desc(self, desc):
        self._cache_timestamp.set("desc", desc)
        self._desc = desc

    def get_desc(self):
        return self._desc

    def set_tag(self, tag):
        self._cache_timestamp.set("tag", tag)
        self._tag = tag

    def get_tag(self):
        return self._tag

    def get_last_time(self):
        return self._cache_timestamp.get("last_time")

    def make_timestamp(self):
        self._cache_timestamp.set("last_time", str(time.time()))
        self._cache_timestamp.save()

    def clear_timestamp(self):
        self._cache_timestamp.clear()


class RecordsCache(object):
    def __init__(self):
        super(RecordsCache, self).__init__()
        self._cache_records = storage.StorageCache("tomato_time_records")

    def create_records(self, content):
        localtime = time.localtime()
        date = time.strftime("%Y-%m-%d", localtime)
        _time = time.strftime("%H:%M", localtime)
        cache = self._cache_records.get(date, [])
        cache.append("%s %s" % (_time, content))
        self._cache_records.set(date, cache)
        self._cache_records.save()

    def show_records(self):
        window = sublime.active_window()
        view = window.new_file()
        view.set_name("Tomato Time Records")
        view.set_scratch(True)
        view.settings().set("word_wrap", True)
        view.settings().set("auto_indent", False)
        view.settings().set("tab_width", 4)
        view.set_syntax_file("Packages/Markdown/Markdown.sublime-syntax")

        def write(c):
            view.run_command("insert", {"characters": c})

        write("# Tomato Time Records\n")
        for date in [v for v in sorted(self._cache_records.get_keys())]:
            write("\n## %s\n" % date)
            for content in self._cache_records.get(date):
                write("  + %s\n" % content)

    def clear_records(self):
        self._cache_records.clear()


class TagsSetting(object):
    def __init__(self):
        super(TagsSetting, self).__init__()
        self._setting_tag = storage.StorageSetting("tomato_time")

    def get_tags(self):
        return self._setting_tag.get("tags", [])

    def create_tag(self, name):
        tags = self.get_tags()
        if name not in tags:
            tags.append(name)
        self._setting_tag.set("tags", tags)
        self._setting_tag.save()

    def delete_tag(self, name):
        tags = self.get_tags()
        tags.remove(name)
        self._setting_tag.set("tags", tags)
        self._setting_tag.save()


class Tomato(TimestampCache, RecordsCache, TagsSetting):
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
        if DEBUG and self.counter > 5:
            self.finish()
        if self.counter >= TOMATO_TIME:
            self.finish()

    def start(self, last_time=0):
        if last_time == 0:
            self.make_timestamp()
        self.counter = last_time
        self.actived = True
        self.set_status_visiable(True)
        log.info("start")
        log.info("[tag]: %s" % self._tag)
        log.info("[desc]: %s" % self._desc)

    def stop(self):
        self.clear_timestamp()
        self.counter = 0
        self.actived = False
        self.set_status_visiable(False)

    def finish(self):
        self.stop()
        if self._tag:
            self.create_records("**%s** %s" % (self._tag, self._desc))
            sublime.message_dialog(
                "Finish Tomato Time\nTag: %s\nDesc: %s" % (self._tag, self._desc)
            )
        else:
            self.create_records("%s" % (self._desc))
            sublime.message_dialog("Finish Tomato Time\nDesc: %s" % (self._desc))
        self.show_records()
        log.info("finish")
        log.info("[tag]: %s" % self._tag)
        log.info("[desc]: %s" % self._desc)

    def discard(self):
        self.stop()
        if self._tag:
            sublime.message_dialog(
                "Discard Tomato Time\nTag: %s\nDesc: %s" % (self._tag, self._desc)
            )
        else:
            sublime.message_dialog("Discard Tomato Time\nDesc: %s" % (self._desc))
        log.info("discard")
        log.info("[tag]: %s" % self._tag)
        log.info("[desc]: %s" % self._desc)

    def set_status_visiable(self, flag):
        self.status_visiable = flag
        self.show_progress()

    def get_status_visiable(self):
        return self.status_visiable

    def show_progress(self):
        if self.status_visiable is False:
            sublime.status_message("")
            return
        progress = int(self.counter / TOMATO_TIME * 100)
        msg = "|" + progress * "-" + "o" + (100 - progress) * "-" + "|"
        sublime.status_message(msg)

    def check_cache_time(self):
        last_time = self.get_last_time()
        if last_time is None:
            self.clear_timestamp()
            return
        cur_time = time.time()
        delta = cur_time - float(last_time)
        log.debug("delta: %s" % delta)
        if delta >= TOMATO_TIME:
            self.clear_timestamp()
        else:
            self.start(int(delta))


def get_tomato():
    global tomato_singleton
    if not tomato_singleton:
        tomato_singleton = Tomato()
    return tomato_singleton
