import os
from functools import partial

import pandas as pd

from pfscrap.utils.dataframe import path2df
from pfscrap.utils.files import is_file, read_json

from pfscrap.modules.kofia import (
    get_kofia_fund_list,
    get_kofia_fund_list_detail,
    get_kofia_settle_exso_by_date,
    get_kofia_fund_price_progress
)
from pfscrap.modules.kofia.pipelines import pipe

FUND_LIST_PREFIX = 'FundList'
FUND_LIST_DETAIL_PREFIX = 'FundListDetail'
PRICE_PROGRESS_POSTFIX = 'FundPriceProgress'
SETTLE_EXSO_PREFIX = 'FundSettleExSo'


def get_output_filename_generator(action, **kwargs):
    if action == 'ls':
        prefix = FUND_LIST_PREFIX
    elif action == 'ls-al':
        prefix = FUND_LIST_DETAIL_PREFIX
    elif action == 'ex':
        prefix = SETTLE_EXSO_PREFIX
    elif action == 'pg':
        prefix = PRICE_PROGRESS_POSTFIX

    def outputer(start_date, end_date, ext, **kwargs):
        output = f"{prefix}_{start_date}~{end_date}{ext}"
        return output
    return outputer


def parse_kofia_args(action,  **kwargs):
    if action == 'ls':
        app = get_kofia_fund_list
    elif action == 'ls-al':
        app = get_kofia_fund_list_detail
    elif action == 'pg':
        app = get_kofia_fund_price_progress
    elif action == 'ex':
        app = get_kofia_settle_exso_by_date
    else:
        error_message = ">>python pfscrap kofia [ls, ls-al, pg, ex]!"
        print(error_message)

    piper = partial(
        pipe,
        **kwargs
    )
    outputer = get_output_filename_generator(action, **kwargs)
    piper(app, outputer=outputer, **kwargs)
