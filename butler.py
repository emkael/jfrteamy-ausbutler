from ausbutler.config import load_config
from ausbutler.interface import Interface


i = Interface(load_config('butler'))
i.calculate_all()
