import itertools


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
