import yaml
from path import Path

from fuzzrunner.command import Command

FUZZ_YAML_FILE_NAME = "fuzz.yaml"


def get_relative_to_root(fuzz_yaml_path, script):
    if script[0].startswith("./"):
        return [str("./" + (fuzz_yaml_path.parent / script[0]).normpath()), *script[1:]]
    else:
        return script


def extract_cmds(fuzz_path):
    print("Found fuzz.yaml! ", fuzz_path)
    all_cmds = []
    with fuzz_path.open('r') as f:
        fuzz_yaml = yaml.load(f)
        for cmd_yaml in fuzz_yaml['commands']:
            command = Command(description=cmd_yaml['desc'],
                              script=get_relative_to_root(fuzz_path, cmd_yaml['script']),
                              params=cmd_yaml.get('params', None))
            all_cmds.extend(command.expand())

    for cmd in all_cmds:
        print("Saving command: ", cmd.description)

    return all_cmds


def serialize_command(cmd):
    return {
        'desc': cmd.description,
        'script': cmd.script
    }


def index(script_root):
    script_root_path = Path(script_root)
    script_root_path.dirs()
    print("Indexing from script root:", script_root_path)
    all_cmds = []

    with script_root_path:
        for path in Path(".").walk():
            if path.fnmatch(FUZZ_YAML_FILE_NAME):
                all_cmds.extend(extract_cmds(path))

    print("Done indexing. Saving to ~/.fuzzconfig.yaml")

    with Path("~/.fuzzconfig.yaml").expanduser().open("w") as f:
        yaml.dump({
            'script-root': str(script_root_path.abspath()),
            'commands': [serialize_command(c) for c in all_cmds]
        }, f, default_flow_style=False)

    print("Index complete")
