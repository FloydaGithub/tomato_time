import sublime
import sublime_plugin
from .tomato_time import get_tomato


class CreateTomatoCommand(sublime_plugin.TextCommand):
    def show_desc_panel(self):
        window = sublime.active_window()
        caption = 'Tomato Time Description:'

        def on_done(desc):
            self.tomato.set_desc(desc)
            self.tomato.set_tag(self.tag)
            self.tomato.start()

        window.show_input_panel(caption, self.tomato.get_desc(), on_done, None,
                                None)

    def create_tag(self):
        window = sublime.active_window()
        caption = 'New Tag\'s Name:'

        def on_done(name):
            self.tomato.create_tag(name)
            self.show_tags_panel()

        window.show_input_panel(caption, '', on_done, None, None)

    def delete_tag(self):
        window = sublime.active_window()
        items = []
        tags = self.tomato.get_tags()
        if len(tags) == 0:
            self.show_tags_panel()
            return
        for t in tags:
            items.append(': %s' % t)

        def on_select(index):
            if index < 0:
                return
            self.tomato.delete_tag(tags[index])
            self.show_tags_panel()

        window.show_quick_panel(items, on_select)

    def show_tags_panel(self):
        window = sublime.active_window()
        items = []
        tag = self.tomato.get_tag()
        desc = self.tomato.get_desc()

        if tag:
            items.append('Go on with last tomato: [%s] %s' % (tag, desc))
        else:
            items.append('Go on with last tomato: %s' % (desc))
        items.append('Discard Tag')
        items.append('Create Tag')
        items.append('Delete Tag')

        tags = self.tomato.get_tags()
        for t in tags:
            items.append(': %s' % t)

        def on_select(index):
            if index < 0:
                return
            if index == 0:
                self.tag = self.tomato.get_tag()
                self.show_desc_panel()
                return
            if index == 1:
                self.tag = None
                self.show_desc_panel()
                return
            if index == 2:
                self.create_tag()
                return
            if index == 3:
                self.delete_tag()
                return
            self.tag = tags[index - 4]
            self.show_desc_panel()

        window.show_quick_panel(items, on_select)

    def run(self, edit):
        self.tomato = get_tomato()
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
