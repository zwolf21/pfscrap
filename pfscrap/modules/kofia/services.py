import pandas as pd

from .scrapers import (
    KofiaFundListScraper,
    KofiaFundInfoScraper,
    KofiaPriceProgressScraper,
    KofiaSettleExSoScraper
)


def get_kofia_fund_list(start_date, end_date):
    kflist = KofiaFundListScraper()
    r = kflist.scrap(start_date=start_date, end_date=end_date)
    df = pd.DataFrame(r['fund_list'])
    return df


def get_kofia_fund_detail(fund_std_code, **kwargs):
    kfinfo = KofiaFundInfoScraper()
    r = kfinfo.scrap(fund_std_code=fund_std_code)
    df_detail = pd.DataFrame(r['fund_detail'])
    df_etc = pd.DataFrame(r['fund_etc'])
    df_detail = pd.merge(df_detail, df_etc)
    return df_detail


def apply_fund_list(df_fund_list, apply, merge_on=None):
    columns = df_fund_list.columns
    dfs = []
    if '표준코드' not in columns:
        raise ValueError('The Column name of 표준코드 not found')
    # elif '회사코드' in columns and '설정일' in columns:
    #     for fund_std_code, company_code, initial_date in df_fund_list[['표준코드', '회사코드', '설정일']].values:
    elif '설정일' in columns:
        for fund_std_code, initial_date in df_fund_list[['표준코드', '설정일']].values:
            df = apply(
                fund_std_code,
                # company_code=company_code,
                initial_date=initial_date
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
