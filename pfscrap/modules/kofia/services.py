
import numpy as np
import pandas as pd

from .scrapers import (
    KofiaFundListScraper,
    KofiaFundInfoScraper,
    KofiaPriceProgressScraper,
    KofiaSettleExSoScraper,
    KofiaSettleExSoByDateScraper
)
from .db_column_mappings import RW_FUNDINFO, RW_FUNDINDEX, RW_FUNDSETTLE, RW_FUNDSETTLE_BY_DATE
from pfscrap.utils.date_str import gen_date_range, get_today_str_date, datetime2str
from pfscrap.utils.files import guess_input, read_json
from pfscrap.utils.dataframe import df2path
from pfscrap.lib.orm import DBOrm

FIRST_INITIAL_DATE = '19900101'
DATERANGE_SLICE_INTERVAL_YEAR = 1
FUNDINFO_TABLE_NAME = 'RW_FUNDINFO'
FUNDSETTLE_EXSO_TABLE_NAME = 'RW_FUNDSETTLE'


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



def get_kofia_fund_list_detail(start_date, end_date, output=None):
    df_fund_list = get_kofia_fund_list(start_date, end_date)
    df_fund_list_detail = apply_fund_list(
        df_fund_list, get_kofia_fund_detail,
        merge_on='표준코드'
    )
    return df_fund_list_detail


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
    kfexso = KofiaSettleExSoScraper()
    r = kfexso.scrap(fund_std_code=fund_std_code, company_code=company_code)
    records = r['fund_exso']
    df = pd.DataFrame(records)
    return df


def get_kofia_fund_settle_exso_by_fund_list(df_fund_list, **kwargs):
    df_settle_exso = apply_fund_list(df_fund_list, get_kofia_fund_settle_exso)
    return df_settle_exso


def insert_db_table_kofia_fund_list(table_name=FUNDINFO_TABLE_NAME, start_date=None, end_date=None, mapping=RW_FUNDINFO, **db_connection_info):
    설정일 = mapping['설정일']
    표준코드 = mapping['표준코드']
    db = DBOrm(**db_connection_info)
    start_date = start_date or db.get_max(table_name, 설정일)
    end_date = end_date or get_today_str_date()
    df_fund_list = get_kofia_fund_list_detail(start_date, end_date)
    df = db.filter_df_not_exists(table_name, df_fund_list, {표준코드: '표준코드'})
    print('insert_db_table_kofia_fund_list test')
    print(df)
    # db.insert_db(
    #     df, table_name,
    #     column_mapping=mapping,
    #     created=mapping.get('created'),
    #     updated=mapping.get('updated'),
    # )
    return df.shape[0]

def get_kofia_settle_exso_by_date(start_date, end_date, interval=DATERANGE_SLICE_INTERVAL_YEAR):
    dfs = []
    for start_date, end_date in gen_date_range(start_date, end_date, interval=interval):
        exso = KofiaSettleExSoByDateScraper()
        r = exso.scrap(start_date=start_date, end_date=end_date)
        df = pd.DataFrame(r['fund_exso_by_date'])
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)


def insert_db_table_settle_exso_by_date(table_name=FUNDSETTLE_EXSO_TABLE_NAME, start_date=None, end_date=None, mapping=RW_FUNDSETTLE_BY_DATE, **db_connection_info):
    db = DBOrm(**db_connection_info)
    회계기말 = mapping['회계기말']
    start_date = start_date or db.get_max(table_name, 회계기말)
    end_date = end_date or get_today_str_date()
    df = get_kofia_settle_exso_by_date(start_date, end_date)
    print('insert_db_table_settle_exso_by_date test')
    print(df)
    # db.insert_db(
    #     df, table_name,
    #     column_mapping=mapping,
    #     created=mapping.get('created'),
    #     updated=mapping.get('updated')
    # )
    return df.shape[0]
