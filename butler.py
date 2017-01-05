import json
from os import path

import __main__
from ausbutler.interface import Interface


i = Interface(json.load(
    open(path.join(path.dirname(__main__.__file__), 'config', 'butler.json'))))
i.calculate_all()
