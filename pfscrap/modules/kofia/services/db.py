import pandas as pd
import numpy as np
from datetime import datetime

from pfscrap.utils.date_str import get_today_str_date
from pfscrap.lib.orm import DBOrm

from ..constants import (
    FUNDINFO_TABLE_NAME,
    FUNDSETTLE_EXSO_TABLE_NAME, RW_FUNDINDEX_TABLE_NAME
)
from .db_column_mappings import RW_FUNDINFO, RW_FUNDINDEX, RW_FUNDSETTLE_BY_DATE
from .api import *


def _print_db_progress(total_count, index, print_on=1000, prefix=""):
    if index % print_on == 0:
        now = datetime.now()
        pct = round((index*100)/total_count, 2)
        log = f"{prefix}{pct}%(완료시각: {now.strftime('%Y%m%d %H:%M:%S')})"
        print(log)


def insert_db_table_kofia_price_progress(table_name=RW_FUNDINDEX_TABLE_NAME, info_table_name=FUNDINFO_TABLE_NAME, mapping=RW_FUNDINDEX, info_mapping=RW_FUNDINFO, **db_connection_info):
    설정일 = info_mapping['설정일']
    회사코드 = info_mapping['회사코드']
    표준코드 = info_mapping['표준코드']
    스크랩여부 = info_mapping['스크랩여부']
    기준일자 = mapping['기준일자']
    db = DBOrm(**db_connection_info)
    # DB의 기존 펀드리스트 테이블을 얻는다
    df_fund_list_table = db.get_df(
        info_table_name,
        columns=[표준코드, 설정일, 회사코드],
        # where=f'{스크랩여부}="Y"' # 일단은 스크랩 여부 관계 없이 다 받아봄
    )
    # DB의 기존 지수테이블을 얻는다
    df_progress_table = db.get_df(
        table_name,
        columns=[표준코드, 기준일자]
    )
    # print('insert_db_table_kofia_price_progress test')
    # print(df_fund_list_table.shape[0])
    # print(df_progress_table)
    # 기존 펀드리스트 테이블을 순회하며 얻은 펀드 코드 값으로 각 코드마다 지정보를 구해 저장한다.
    total_count = df_fund_list_table.shape[0]

    for i, row in df_fund_list_table.iterrows():
        fund_std_code = row[표준코드]  # 조사할 펀드 코드

        # 지수 정보조회 시작일자 구하는 로직
        # - 1. 지수정보 테이블에서 해당 코드를 조회하여 가장 늦은 날짜를 지정
        # - 2. 해당 코드의 지수 정보가 비어있으면 펀드의 설정일을 지정
        # - 3. 설정일도 없을경우 기본 세팅날짜 FIRST_INITIAL_DATE 로 지정

        mask = df_progress_table[표준코드] == fund_std_code  # 해당코드로 지수정보 필터링
        해당코드의지수정보 = df_progress_table[mask]
        if 해당코드의지수정보.empty:  # 지수정보를 갖고 있지 않는다면
            지수조회시작일자 = row[설정일] or FIRST_INITIAL_DATE
        else:
            지수조회시작일자 = 해당코드의지수정보[기준일자].max()

        # 지수조회 시작일자 부터 정보 지수 정보 가져옴
        df_progress = get_kofia_fund_price_progress(
            fund_std_code=row[표준코드],
            company_code=row[회사코드],
            initial_date=지수조회시작일자
        ).drop_duplicates(['표준코드', '기준일자'])  # 혹시모를 중복제거

        # DB에 이미 존재 하는것 제외
        df = db.filter_df_not_exists(
            table_name, df_progress,
            [(표준코드, '표준코드'), (기준일자, '기준일자')]
        )

        _print_db_progress(
            total_count, i, 1,
            prefix=f'지수정보 저장중...{fund_std_code}(조회시작일자:{지수조회시작일자})'
        )
        # DB 저장
        db.insert_db(
            df, table_name,
            column_mapping=mapping,
            created=mapping.get('created'),
            updated=mapping.get('updated')
        )


def insert_db_table_kofia_fund_list(table_name=FUNDINFO_TABLE_NAME, start_date=None, end_date=None, mapping=RW_FUNDINFO, **db_connection_info):
    설정일 = mapping['설정일']
    표준코드 = mapping['표준코드']
    db = DBOrm(**db_connection_info)
    start_date = start_date or db.get_max(table_name, 설정일)
    end_date = end_date or get_today_str_date()
    df_fund_list = get_kofia_fund_list_detail(start_date, end_date)
    df = db.filter_df_not_exists(table_name, df_fund_list, {표준코드: '표준코드'})
    print('insert_db_table_kofia_fund_list')
    print('row counts:', df.shape[0])
    db.insert_db(
        df, table_name,
        column_mapping=mapping,
        created=mapping.get('created'),
        updated=mapping.get('updated'),
    )
    return df.shape[0]


def insert_db_table_settle_exso_by_date(table_name=FUNDSETTLE_EXSO_TABLE_NAME, start_date=None, end_date=None, mapping=RW_FUNDSETTLE_BY_DATE, **db_connection_info):
    db = DBOrm(**db_connection_info)
    표준코드 = mapping['표준코드']
    회계기말 = mapping['회계기말']
    구분 = mapping['구분']
    start_date = start_date or db.get_max(table_name, 회계기말)
    end_date = end_date or get_today_str_date()
    df_exso_list = get_kofia_settle_exso_by_date(start_date, end_date)
    df = db.filter_df_not_exists(
        table_name, df_exso_list,
        [(표준코드, '표준코드'), (회계기말, '회계기말'), (구분, '구분')]
    )
    print('insert_db_table_settle_exso_by_date')
    print('row counts:', df.shape[0])
    db.insert_db(
        df, table_name,
        column_mapping=mapping,
        created=mapping.get('created'),
        updated=mapping.get('updated')
    )
    return df.shape[0]
