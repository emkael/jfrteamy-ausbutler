import json
from os import path

import __main__
from ausbutler.interface import Interface

config = json.load(
    open(path.join(path.dirname(__main__.__file__), 'config', 'butler.json')))

i = Interface(config)
i.init_db()
i.populate_db()
i.opp_scores()
i.normalize_scores()
