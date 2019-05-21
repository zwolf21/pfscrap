import os


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
