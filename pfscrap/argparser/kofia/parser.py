import os

import pandas as pd

from pfscrap.utils.dataframe import path2df
from pfscrap.utils.files import is_file
from pfscrap.utils.date_str import get_date_ago_range

from pfscrap.modules.kofia import (
    get_kofia_fund_list,
    get_kofia_fund_detail,
    get_kofia_fund_price_progress,
    get_kofia_fund_settle_exso, apply_fund_list,

    validate_fund_list,
)

from pfscrap.lib.orm import DBOrm
from pfscrap.settings.db import DB_CON_KWARGS

APP_NAME = 'kofia'
COMMANDS = ['ls', 'ls-al', 'pg', 'ex']
FUND_LIST_PREFIX = 'FundList'
FUND_LIST_DETAIL_PREFIX = 'FundListDetail'
PRICE_PROGRESS_POSTFIX = 'FundPriceProgress'
SETTLE_EXSO_POSTFIX = 'FundSettleExSo'


def parse_kofia_args(args):
    keywords = args.keywords
    if isinstance(keywords, str):
        keywords = [keywords]
        if len(keywords) < 2:
            error_message = "It require at least 2 keywords (>> pfscrap scrap_appname action)"

    app_name, root, *rest = keywords

    if app_name != APP_NAME:
        pass

    if root not in COMMANDS:
        error_message = 'Action must in {}(>> pfscrap scrap_appname action [keywords])'
        raise ValueError(error_message.format(COMMANDS))

    start_date, end_date = get_date_ago_range(
        start_date=args.start_date,
        end_date=args.end_date,
        days_ago=args.day_ago,
        months_ago=args.month_ago,
        years_ago=args.year_ago
    )

    if root in ['ls', 'ls-al']:
        df = get_kofia_fund_list(start_date, end_date)
        output_name = '{}_{}~{}'.format(FUND_LIST_PREFIX, start_date, end_date)
        if root == 'ls-al':
            df = apply_fund_list(df, get_kofia_fund_detail, merge_on='표준코드')
            output_name = '{}_{}~{}'.format(
                FUND_LIST_DETAIL_PREFIX, start_date, end_date
            )

    if root in ['pg', 'ex']:
        if root == 'pg':
            apply = get_kofia_fund_price_progress
            output_name_postfix = PRICE_PROGRESS_POSTFIX
        else:
            apply = get_kofia_fund_settle_exso
            output_name_postfix = SETTLE_EXSO_POSTFIX
        if rest:
            keyword = rest[0]
            if is_file(keyword):
                fn, ext = os.path.splitext(keyword)
                df_fund_list = path2df(keyword)
                if not validate_fund_list(df_fund_list):
                    raise ValueError(
                        'Validation Error: Source File columns is different from FundList or FundDetail signature'
                    )
                df = apply_fund_list(df_fund_list, apply)
                output_name = '{}-{}'.format(fn, output_name_postfix)
            else:
                df = apply(keyword)
                output_name = '{}-{}'.format(keyword, output_name_postfix)
        else:
            raise ValueError(
                'pg, ex action get intput fund_list files or 표준코드'
            )

    if args.output in ['xlsx', 'xls', 'excel', 'xl', 'csv']:
        output_to = args.output
        if output_to in ['xlsx', 'xls', 'excel', 'xl']:
            output_filename = '{}.xlsx'.format(output_name)
            df.to_excel(output_filename, index=False)
        else:
            output_filename = '{}.csv'.format(output_name)
            df.to_csv(output_filename, index=False)
    elif args.output == 'print':
        print(df.head())
    else:
        if not is_file(args.output):
            raise ValueError("-o 'xlsx', 'csv', or DB_CONNECTION_FILE_PATH")
        db_connection_kwargs = dict(path2df(args.output).loc[0].to_dict())
        db = DBOrm(**db_connection_kwargs)
        exist_pk = db.get_df()['ID']
        df = df_fund_list[df_fund_list['ID'].notin(exist_pk)]
        

