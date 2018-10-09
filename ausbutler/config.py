import json
from os import path

import __main__


def load_config(filename):
    possible_directories = ['.', path.dirname(__main__.__file__)]
    for directory in possible_directories:
        if path.exists(path.join(directory, 'config')):
            return json.load(
                open(path.join(directory, 'config',
                               filename + '.json')))
