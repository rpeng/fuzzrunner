#!/usr/bin/env python3

import curses
import curses.ascii
import itertools
import logging
import os
import subprocess

import fuzzywuzzy.process
import yaml


class Command:
    def __init__(self, description: str, script: [str], params=None):
        self.description = description
        self.script = script
        self.params = params or {}

    """
    Replaces the description and script token parameters with all the params.
    
    E.g.:
    
    Description: "Connect to {datacenter} cluster"
    Script: ["cluster/login.sh", "{datacenter}"]
    Parameters:
      "datacenter": ["us-west", "us-east"],
    
    resulting commands:
        Connect to us-west cluster: cluster/login.sh us-west
        Connect to us-east cluster: cluster/login.sh us-east
    """

    def expand(self):
        if self.params == {}:
            return [self]

        expanded_commands = []

        name_values = []
        for name, values in self.params.items():
            name_values.append(itertools.product([name], values))
        expanded_params = itertools.product(*name_values)

        for params in expanded_params:
            expanded_desc = self.description.format(**dict(params))
            expanded_script = [s.format(**dict(params)) for s in self.script]
            expanded_commands.append(Command(expanded_desc, expanded_script))

        return expanded_commands

    def __repr__(self):
        return "Command(Desc: {}, Script: {}, Params: {})".format(self.description, self.script, self.params)


class FuzzRunner:
    def __init__(self, script_root, commands):
        self.script_root = script_root
        self.commands = commands
        self.command_to_desc = dict([(cmd, cmd.description) for cmd in commands])

    @classmethod
    def from_yaml(cls, file_name):
        with open(file_name, "r") as yaml_file:
            settings = yaml.load(yaml_file.read())
        all_commands = []
        for command in settings['commands']:
            all_commands.extend(
                Command(command['desc'], command['script'], command.get('params', None)).expand())
        return cls(settings['script-root'], all_commands)

    def recommend(self, search_string):
        found_commands = fuzzywuzzy.process.extract(search_string,
                                                    self.command_to_desc,
                                                    limit=5)
        return [f[2] for f in found_commands]

    def run(self, cmd):
        path_to_script = os.path.join(self.script_root, cmd.script[0])
        subprocess.run([path_to_script, *cmd.script[1:]])


class FuzzShell:
    def __init__(self):
        self.fuzzrunner = FuzzRunner.from_yaml("index.yaml")
        self.cmd = ""
        self.results = []

    def draw_loop(self, stdscr):
        stdscr.clear()
        _, screen_width = stdscr.getmaxyx()
        max_desc_len = max([len(c.description) for c in self.results])
        desc_width = max_desc_len + 10

        stdscr.addstr(0, 0, "Fuzz Command Query: {}".format(self.cmd))
        stdscr.addstr(2, 0, "Results:")
        for i, cmd in enumerate(self.results):
            output_line = "[{idx}] {desc:<{width}} {script}".format(
                idx=i,
                desc=cmd.description,
                width=desc_width,
                script=' '.join(cmd.script))

            if len(output_line) > screen_width:
                output_line = output_line[:screen_width-2]+".."
            stdscr.addstr(3 + i, 0, output_line)
        stdscr.refresh()

    def get_cmd(self, stdscr):
        curses.start_color()
        curses.use_default_colors()
        curses.curs_set(0)
        while True:
            self.results = self.fuzzrunner.recommend(self.cmd)
            self.draw_loop(stdscr)

            try:
                ch = stdscr.getch()
            except KeyboardInterrupt:
                return None

            if ch in (curses.KEY_BACKSPACE, curses.ascii.DEL, curses.ascii.BS):
                self.cmd = self.cmd[:-1]
            elif ch in (curses.KEY_ENTER, curses.ascii.LF, curses.ascii.NL):
                if len(self.results) > 0:
                    return self.results[0]
            elif curses.ascii.isdigit(ch):
                idx = ch - ord('0')
                if idx < len(self.results):
                    return self.results[idx]
            elif curses.ascii.isascii(ch):
                self.cmd += chr(ch)

    def run(self):
        cmd = curses.wrapper(self.get_cmd)
        if cmd is not None:
            self.fuzzrunner.run(cmd)


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    FuzzShell().run()
