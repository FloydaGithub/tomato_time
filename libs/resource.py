import sublime
import os


def get_file_path_cache(name):
    user_dir = os.path.join(sublime.cache_path(), "User")
    if not os.path.exists(user_dir):
        os.mkdir(user_dir)
    return os.path.join(user_dir, "%s.cache" % name)


def get_setting_path_user(name):
    user_dir = os.path.join(sublime.packages_path(), "User")
    if not os.path.exists(user_dir):
        os.mkdir(user_dir)
    return os.path.join(user_dir, "%s.sublime-settings" % name)
