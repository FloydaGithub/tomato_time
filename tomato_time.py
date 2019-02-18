import sublime
import sublime_plugin

from .config import TOMATO_TIME, TICK_TIME
tomato_singleton = None


class Tomato():
    def __init__(self):
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

    def start(self):
        self.counter = 0
        self.actived = True
        self.show_progress()

    def stop(self):
        self.counter = 0
        self.actived = False

    def finish(self):
        self.stop()
        sublime.message_dialog("Finish Tomato Time")

    def discard(self):
        self.stop()
        sublime.message_dialog("Discard Tomato Time")

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
        return tomato.is_actived()


class HideTomatoProgressCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        tomato = get_tomato()
        tomato.set_status_visiable(False)

    def is_visible(self):
        tomato = get_tomato()
        return tomato.is_actived()
