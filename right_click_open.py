import re
import os
import webbrowser

import sublime
import sublime_plugin
from Default.open_context_url import rex


class ListFilesInPanelCommand(sublime_plugin.TextCommand):

    def run(self, edit, dir=None):
        if dir is None:
            dir = self.view.window().extract_variables()['file_path']
        if os.path.exists(dir) == False:
            return

        files = [dir]
        if os.path.abspath(os.path.join(dir, os.pardir)) != dir:
            files.append(os.pardir)
        files += os.listdir(dir)
        self.show_files_in_panel(files)

    def show_files_in_panel(self, files):
        def on_done(index):
            if index < 0: return

            args = {"dir": files[0]}

            if index > 0:
                fname = os.path.abspath(os.path.join(files[0], files[index]))
                if os.path.isdir(fname):
                    args = {"dir": fname}
                else:
                    flags = sublime.ENCODED_POSITION
                    sublime.set_timeout(lambda: window.open_file(fname, flags), 0)

            self.view.run_command("list_files_in_panel", args)

        window = self.view.window()
        flags = sublime.MONOSPACE_FONT|sublime.KEEP_OPEN_ON_FOCUS_LOST
        sublime.set_timeout(lambda: window.show_quick_panel(files, on_done, flags), 10)


class ListHomeDirCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        home_dir = {"dir": os.path.expanduser("~")}
        self.view.run_command("list_files_in_panel", home_dir)


class SearchOnlineCommand(sublime_plugin.TextCommand):

    where_search = {
        "baidu": "https://www.baidu.com/s?ie=UTF-8&wd=",
        "google": "http://google.com/#q="
    }

    def run(self, edit, event, where):
        if where in self.where_search:
            webbrowser.open_new_tab(self.where_search[where] + self.content)

    def get_content(self, event):
        pt = self.view.window_to_text((event["x"], event["y"]))
        selected = self.view.sel()
        if len(selected) and selected[0].size() and selected[0].contains(pt):
            return self.view.substr(selected[0])
        else: return None

    def is_visible(self, event, where):
        if RightClickOpenCommand(self.view).find_all(event):
            return False
        self.content = self.get_content(event)
        return self.content is not None

    def description(self, event, where):
        content = self.get_content(event)
        if len(content) > 64:
            content = content[0:64] + "..."

        # caption = " ".join(["Search:", "*"+content+"*", "on", where])
        caption = "Search on " + where
        return caption

    def want_event(self):
        return True


class RightClickOpenCommand(sublime_plugin.TextCommand):

    where_open = {
    "url": "browser",
    "file": "sublime",
    "fold": "quick panel"
    }

    def run(self, edit, event, where):
        if self.url is None: return

        if self.url_type == "url":
            webbrowser.open_new_tab(self.url)
        if self.url_type == "file":
            flags = sublime.ENCODED_POSITION
            window = self.view.window()
            sublime.set_timeout(lambda: window.open_file(self.url, flags), 0)
        if self.url_type == "fold":
            self.view.run_command("list_files_in_panel", {"dir": self.url})

    def get_selected(self, event):
        pt = self.view.window_to_text((event["x"], event["y"]))
        selected = self.view.sel()
        if len(selected) and selected[0].size() and selected[0].contains(pt):
            self.line = selected[0]
            self.pt = pt
            return self.view.substr(selected[0])
        else: return None

    def get_line(self, event):
        pt = self.view.window_to_text((event["x"], event["y"]))
        line = self.view.line(pt)

        line.a = max(line.a, pt - 1024)
        line.b = min(line.b, pt + 1024)

        self.line = line
        self.pt = pt
        return self.view.substr(line)

    def find_url(self, text, line, pt):
        it = rex.finditer(text)
        for match in it:
            if match.start() <= (pt - line.a) and match.end() >= (pt - line.a):
                url = text[match.start():match.end()]
                self.url_type = "url"
                return url
        return None

    def find_path(self, text, line, pt):
        workdir = os.path.dirname(self.view.file_name())
        path = os.path.abspath(os.path.join(workdir, text))
        if os.path.isdir(path):
            self.url_type = "fold"
            return path
        if os.path.isfile(path):
            self.url_type = "file"
            return path

        os.chdir(workdir)
        names = "/".join(text.split("\\"))
        names = [x for x in names.split("/") if x]
        for i in range(len(names), 0, -1):
            path = os.path.abspath(os.path.sep.join(names[:i]))
            if os.path.isdir(path):
                self.url_type = "fold"
                return path
            if os.path.isfile(path):
                self.url_type = "file"
                return path
        return None

    def find_all(self, event):
        text = self.get_selected(event)
        if text is None:
            text = self.get_line(event)

        # if len(text) == 0:
        #     return None

        url = self.find_url(text, self.line, self.pt)
        if url is None:
            url = self.find_path(text, self.line, self.pt)
        return url

    def match_type(self, where):
        return self.where_open[self.url_type] == where

    def is_visible(self, event, where):
        self.url = self.find_all(event)
        if self.url is not None:
            return self.match_type(where)
        return False

    def description(self, event, where):
        url = self.find_all(event)
        if len(url) > 64:
            url = url[0:64] + "..."

        caption = " ".join(["Open:", "*"+url+"*", "in", where])
        return caption

    def want_event(self):
        return True
