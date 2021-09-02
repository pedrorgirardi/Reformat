import subprocess
import os
import json

import sublime_plugin
import sublime


def program_path(program):
    return os.path.join(sublime.packages_path(), "Reformat", "bin", program)


def zprint_path():
    return program_path("zprint")


class PgReformatCommand(sublime_plugin.TextCommand):
    """
    Command to formnat Clojure and JSON.

    Clojure is formatted by zprint.
    JSON is formatted using the built-in Python JSON API.
    """

    def run(self, edit):
        syntax = self.view.syntax()

        for region in self.view.sel():
            region = sublime.Region(0, self.view.size()) if region.empty() else region

            if syntax.scope in {
                "source.edn",
                "source.clojure",
                "source.clojure.clojurescript",
            }:
                self.format_clojure(edit, region)
            elif syntax.scope == "source.json":
                self.format_json(edit, region)
            elif syntax.scope == "source.python":
                self.format_python(edit, region)

    def format_json(self, edit, region):
        try:
            decoded = json.loads(self.view.substr(region))

            formatted = json.dumps(decoded, indent=4)

            self.view.replace(edit, region, formatted)
        except Exception as e:
            print(f"(Reformat) Failed to format JSON: {e}")

    def format_clojure(self, edit, region):
        zprint_config = f"{{:style :respect-bl}}"

        process = subprocess.Popen(
            [zprint_path(), zprint_config],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        try:
            stdout, stderr = process.communicate(self.view.substr(region).encode())

            formatted = stdout.decode("utf-8")

            if formatted:
                self.view.replace(edit, region, formatted)

        except subprocess.TimeoutExpired as e:
            print(f"(Reformat) Failed to format Clojure: {e}")

            process.kill()

    def format_python(self, edit, region):
        """
        Please make sure `black` is installed: pip3 install black
        """
        process = subprocess.Popen(
            ["black", "--code", self.view.substr(region).encode()],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        try:
            stdout, stderr = process.communicate()

            formatted = stdout.decode("utf-8")

            if formatted:
                self.view.replace(edit, region, formatted)

        except subprocess.TimeoutExpired as e:
            print(f"(Reformat) Failed to format Python: {e}")

            process.kill()
