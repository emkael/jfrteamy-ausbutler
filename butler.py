import sys

from ausbutler.config import load_config
from ausbutler.goniec import Goniec
from ausbutler.interface import Interface


def main():
    args = sys.argv[1:]
    if len(args) == 0:
        args = ['calculate', 'generate', 'send']

    i = Interface(load_config('butler'))

    if 'calculate' in args:
        i.calculate_all()

    if 'generate' in args:
        files = i.generate_all()
        if 'send' in args:
            client = Goniec(load_config('goniec'))
            client.send(files)

if __name__ == '__main__':
    main()
