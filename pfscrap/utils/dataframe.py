import pandas as pd

from .files import guess_input


def path2df(path):
    guess = guess_input(path)
    if guess == '.csv':
        return pd.read_csv(path)
    elif guess == '.xlsx':
        return pd.read_excel(path)
    else:
        raise ValueError('Only Excel or CSV!')
