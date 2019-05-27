import pandas as pd

from ..scrapers import (
    KofiaFundListScraper,
    KofiaFundInfoScraper,
    KofiaPriceProgressScraper,
    KofiaSettleExSoScraper,
    KofiaSettleExSoByDateScraper
)

from ..constants import (
    FIRST_INITIAL_DATE
)
from pfscrap.utils.date_str import slice_date_range


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


def get_kofia_fund_list(start_date, end_date, **kwargs):
    dfs = []
    for start_date, end_date in slice_date_range(start_date, end_date, by='year'):
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


def get_kofia_fund_list_detail(start_date, end_date, **kwargs):
    df_fund_list = get_kofia_fund_list(start_date, end_date)
    df_fund_list_detail = apply_fund_list(
        df_fund_list, get_kofia_fund_detail,
        merge_on='표준코드'
    )
    return df_fund_list_detail


def get_kofia_fund_price_progress(fund_std_code, company_code=None, initial_date=FIRST_INITIAL_DATE, **kwargs):
    if company_code is None:
        company_code = ''
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


def get_kofia_settle_exso_by_date(start_date, end_date, **kwargs):
    dfs = []
    for start_date, end_date in slice_date_range(start_date, end_date, by='month'):
        exso = KofiaSettleExSoByDateScraper()
        r = exso.scrap(start_date=start_date, end_date=end_date)
        df = pd.DataFrame(r['fund_exso_by_date'])
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)
