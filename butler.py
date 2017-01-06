from ausbutler.config import load_config
from ausbutler.interface import Interface
from ausbutler.goniec import Goniec

i = Interface(load_config('butler'))
i.calculate_all()
files = i.generate_all()
g = Goniec(load_config('goniec'))
g.send(files)
