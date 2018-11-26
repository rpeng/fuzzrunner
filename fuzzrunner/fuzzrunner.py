import os

import fuzzywuzzy.fuzz
import fuzzywuzzy.process
import ngram
from path import Path

from fuzzrunner.command import Command


class FuzzRunner:
    def __init__(self, script_root, commands):
        self.script_root = script_root
        self.commands = commands
        self.command_to_desc = dict([(cmd, cmd.description) for cmd in commands])

    def ngram_score(self, s1, s2):
        return ngram.NGram.compare(s1, s2, N=3)

    def recommend(self, search_string):
        found_commands = fuzzywuzzy.process.extract(search_string,
                                                    self.command_to_desc,
                                                    limit=5,
                                                    scorer=self.ngram_score)
        return [f[2] for f in found_commands]

    def run(self, cmd):
        if cmd.script[0].startswith("./"):
            path_to_script = Path(self.script_root) / cmd.script[0]
        else:
            path_to_script = Path(cmd.script[0])

        print("Running:", ' '.join(cmd.script))
        os.execvp(path_to_script, [path_to_script.name, *cmd.script[1:]])

    @classmethod
    def from_settings(cls, settings):
        all_commands = []
        for cmd in settings['commands']:
            if 'params' in cmd:
                raise RuntimeError("Unexpected parameters in expanded index! Please re-generate index.")
            all_commands.append(
                Command(cmd['desc'], cmd['script'], cmd.get('params', None)))
        return cls(settings['script-root'], all_commands)
