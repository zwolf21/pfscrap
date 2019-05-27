import functools

from pfscrap.utils.dataframe import df2path
from pfscrap.utils.files import guess_input, read_json
from pfscrap.utils.date_str import get_date_ago_range

from .services.api import (
    get_kofia_fund_list_detail,
    get_kofia_settle_exso_by_date,
    get_kofia_fund_price_progress,
)
from .services.db import (
    insert_db_table_kofia_fund_list,
    insert_db_table_settle_exso_by_date,
    insert_db_table_kofia_price_progress,
)


def _set_date2kwargs(kwargs, start_date, end_date):
    for k, v in [('start_date', start_date), ('end_date', end_date)]:
        if not kwargs.get(k):
            kwargs[k] = v


def pipe(api, output, outputer, *args, **kwargs):
    db_routes = {
        get_kofia_fund_list_detail: insert_db_table_kofia_fund_list,
        get_kofia_settle_exso_by_date: insert_db_table_settle_exso_by_date,
        get_kofia_fund_price_progress: insert_db_table_kofia_price_progress,
    }

    # pipe 2 file
    if output in ['csv', 'excel', 'xlsx']:
        s, e = get_date_ago_range(**kwargs)
        _set_date2kwargs(kwargs, s, e)
        if output in ['excel', 'xlsx']:
            ext = '.xlsx'
        else:
            ext = '.csv'
        output_name = outputer(s, e, ext)
        df = api(*args, **kwargs)
        df2path(df, output_name)
        print(f"Output file: {output_name}")
    # pipe 2 DB
    else:
        guess = guess_input(output)
        if guess == 'db_connection_info':
            db_connection_info = read_json(output)
            app = db_routes.get(api)
            if not app:
                raise ValueError('해당 명령어는 DB와 연결되지 않았습니다.')
            kwargs.update(db_connection_info)
            app(*args, **kwargs)
        # pipe 2 console
        else:
            s, e = get_date_ago_range()
            _set_date2kwargs(kwargs, s, e)
            df = api(*args, **kwargs)
            print(df)
