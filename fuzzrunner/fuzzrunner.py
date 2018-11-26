import os
import subprocess

import fuzzywuzzy.process

from fuzzrunner.command import Command


class FuzzRunner:
    def __init__(self, script_root, commands):
        self.script_root = script_root
        self.commands = commands
        self.command_to_desc = dict([(cmd, cmd.description) for cmd in commands])

    def recommend(self, search_string):
        found_commands = fuzzywuzzy.process.extract(search_string,
                                                    self.command_to_desc,
                                                    limit=5)
        return [f[2] for f in found_commands]

    def run(self, cmd):
        path_to_script = os.path.join(self.script_root, cmd.script[0])
        subprocess.run([path_to_script, *cmd.script[1:]])

    @classmethod
    def from_settings(cls, settings):
        all_commands = []
        for cmd in settings['commands']:
            all_commands.extend(
                Command(cmd['desc'], cmd['script'], cmd.get('params', None)).expand())
        return cls(settings['script-root'], all_commands)