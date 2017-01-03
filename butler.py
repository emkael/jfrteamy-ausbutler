import json
import __main__

from os import path

from ausbutler.interface import Interface

config = json.load(
    open(path.join(path.dirname(__main__.__file__), 'config', 'butler.json')))

i = Interface(config)
i.init_db()
i.populate_db()
i.opp_scores()
i.normalize_scores()
