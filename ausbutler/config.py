import json
from os import path

import __main__


def load_config(filename):
    return json.load(
        open(path.join(path.dirname(__main__.__file__),
                       'config', filename + '.json')))
