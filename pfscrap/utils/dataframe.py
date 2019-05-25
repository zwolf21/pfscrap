import functools


import pandas as pd

from .files import guess_input, get_ext


OUTPUT_INVALID_MESSAGE = 'Only Excel or CSV!'


def path2df(path):
    guess = guess_input(path)
    if guess == '.csv':
        return pd.read_csv(path)
    elif guess == '.xlsx':
        return pd.read_excel(path)
    else:
        raise ValueError(OUTPUT_INVALID_MESSAGE)


def df2path(df, path, index=False, **kwargs):
    ext = get_ext(path)
    if ext in ['.xlsx', 'xls']:
        df.to_excel(path, index=index, **kwargs)
    elif ext in ['.csv']:
        df.to_csv(path, index=index, **kwargs)
    else:
        raise ValueError(OUTPUT_INVALID_MESSAGE)
