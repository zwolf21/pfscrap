import os
import json


def is_file(path):
    return os.path.exists(path)


def guess_input(keyword):
    if is_file(keyword):
        fn, ext = os.path.splitext(keyword)
        if ext in ['.xls', '.xlsx']:
            return '.xlsx'
        elif ext in ['.csv']:
            return '.csv'
        else:
            return ext
    else:
        return keyword


def read_json(path):
    with open(path, encoding='utf-8') as fp:
        return json.loads(fp.read())
