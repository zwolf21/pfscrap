import numpy as np
import pandas as pd

from .scrapers import (
    KofiaFundListScraper,
    KofiaFundInfoScraper,
    KofiaPriceProgressScraper,
    KofiaSettleExSoScraper
)
from .db_column_mappings import RW_FUNDINFO, RW_FUNDINDEX, RW_FUNDSETTLE
from pfscrap.utils.date_str import gen_date_range, get_today_str_date, datetime2str
from pfscrap.lib.orm import DBOrm

FIRST_INITIAL_DATE = '19900101'
DATERANGE_SLICE_INTERVAL_YEAR = 1


def get_kofia_fund_list(start_date, end_date, interval=DATERANGE_SLICE_INTERVAL_YEAR):
    dfs = []
    for start_date, end_date in gen_date_range(start_date, end_date, interval=interval):
        kflist = KofiaFundListScraper()
        r = kflist.scrap(start_date=start_date, end_date=end_date)
        df = pd.DataFrame(r['fund_list'])
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)


def get_kofia_fund_detail(fund_std_code, **kwargs):
    kfinfo = KofiaFundInfoScraper()
    r = kfinfo.scrap(fund_std_code=fund_std_code)
    df_detail = pd.DataFrame(r['fund_detail'])
    df_etc = pd.DataFrame(r['fund_etc'])
    df_detail = pd.merge(df_detail, df_etc)
    return df_detail


def get_kofia_fund_list_detail(start_date, end_date):
    df_fund_list = get_kofia_fund_list(start_date, end_date)
    df_fund_list_detail = apply_fund_list(
        df_fund_list, get_kofia_fund_detail,
        merge_on='표준코드'
    )
    return df_fund_list_detail


def apply_fund_list(df_fund_list, apply, merge_on=None, initial_date=None):
    columns = df_fund_list.columns
    dfs = []
    if '표준코드' not in columns:
        raise ValueError('The Column name of 표준코드 not found')
    elif '회사코드' in columns and '설정일' in columns:
        for fund_std_code, company_code, ini_date in df_fund_list[['표준코드', '회사코드', '설정일']].values:
            df = apply(
                fund_std_code,
                company_code=company_code,
                initial_date=initial_date or ini_date
            )
            dfs.append(df)
    else:
        for fund_std_code in df_fund_list['표준코드'].values:
            df = apply(fund_std_code)
            dfs.append(df)
    df_apply = pd.concat(dfs, ignore_index=True)
    if merge_on:
        return pd.merge(df_fund_list, df_apply, on=merge_on)
    return df_apply


def get_kofia_fund_price_progress(fund_std_code, company_code=None, initial_date=None, **kwargs):
    if company_code is None:
        company_code = ''
    if initial_date is None:
        fund_df = get_kofia_fund_detail(fund_std_code)
        fund = fund_df.iloc[0]
        initial_date = fund['설정일']

    fkprg = KofiaPriceProgressScraper()
    r = fkprg.scrap(
        fund_std_code=fund_std_code,
        company_code=company_code,
        initial_date=initial_date
    )
    df = pd.DataFrame(r['price_progress'])
    return df


def get_kofia_fund_price_progress_by_fund_list(df_fund_list, initial_date=None, **kwargs):
    df_progress = apply_fund_list(
        df_fund_list, get_kofia_fund_price_progress,
        initial_date=initial_date
    )
    return df_progress


def get_kofia_fund_settle_exso(fund_std_code, company_code=None, **kwargs):
    if company_code is None:
        company_code = ''
        # fund_df = get_kofia_fund_detail(fund_std_code)
        # fund = fund_df.iloc[0]
        # company_code = fund['회사코드']
    kfexso = KofiaSettleExSoScraper()
    r = kfexso.scrap(fund_std_code=fund_std_code, company_code=company_code)
    records = r['fund_exso']
    df = pd.DataFrame(records)
    return df


def get_kofia_fund_settle_exso_by_fund_list(df_fund_list, **kwargs):
    df_settle_exso = apply_fund_list(df_fund_list, get_kofia_fund_settle_exso)
    return df_settle_exso


def insert_db_table_kofia_fund_list(df_fund_list, table_name, mapping=RW_FUNDINFO, **db_connect_info):
    db = DBOrm(**db_connect_info)
    df_table = db.get_df(
        table_name,
        columns=[mapping['표준코드'], mapping['설정일'], mapping['회사코드']]
    )
    df_table = df_table[df_table[mapping['설정일']].notnull()]
    if df_table.shape[0] == 0:
        start_date = FIRST_INITIAL_DATE
    else:
        start_date = df_table[mapping['설정일']].max()

    end_date = get_today_str_date()
    print(start_date, end_date)
    exists_std_code = df_table[mapping['표준코드']]
    df = df_fund_list[~df_fund_list['표준코드'].isin(exists_std_code)]
    db.insert_db(df, table_name, column_mapping=mapping)
