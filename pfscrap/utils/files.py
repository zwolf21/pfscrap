import os
import json


def read_json(path):
    with open(path, encoding='utf-8') as fp:
        return json.loads(fp.read())


def is_file(path):
    return os.path.exists(path)


def get_ext(path):
    fn, ext = os.path.splitext(path)
    return ext


def guess_input(keyword):
    if is_file(keyword):
        fn, ext = os.path.splitext(keyword)
        if ext in ['.xls', '.xlsx']:
            return '.xlsx'
        elif ext in ['.csv']:
            return '.csv'
        elif ext in ['.json']:
            r = read_json(keyword)
            if {'host', 'port', 'db', 'user', 'passwd'} <= r.keys():
                return 'db_connection_info'
            return '.json'
        else:
            return ext
    else:
        return keyword
