import os
import re
import json
import math
from pprint import pprint
from urllib.parse import unquote
from datetime import datetime, timedelta

from scrapgo import LinkRelayScraper, urlpattern, url, root

from .payloaders import (
    get_fund_list_payload,
    get_fund_detail_payload,
    get_fund_etc_payload,
    get_price_change_progress_payload,
    get_fund_exso_payload,
    get_fund_exso_payload_by_date,
)
from .scrap_column_mappings import (
    FUND_LIST_COLUMNS,
    FUND_DETAIL_COLUMNS,
    PRICE_PROGRESS_COLUMNS,
    SETTLE_EXSO_COLUMNS,
    SETTLE_EXSO_BY_DATE_COLUMNS,
)
from pfscrap.utils.soup_parser import parse_xml_table_tag


class KofiaScraper(LinkRelayScraper):
    # CACHE_BACKEND = 'redis'
    CACHE_NAME = 'PROFP_SCRAP_CACHE'
    REQUEST_DELAY = 0
    RETRY_INTERVAL_SECONDS = 10, 100, 1000,
    # REQUEST_LOGGING = False


class KofiaFundListScraper(KofiaScraper):
    LINK_RELAY = [
        url(
            'http://dis.kofia.or.kr/proframeWeb/XMLSERVICES/',
            payloader='fund_list_payloader',
            parser='fund_list_parser',
            name='fund_list'
        )
    ]

    def fund_list_payloader(self, start_date, end_date):
        log = f"Retrieve FundList by Date Range: {start_date}~{end_date}"
        print(log)
        payload = get_fund_list_payload(start_date, end_date)
        yield payload

    def fund_list_parser(self, response, **kwargs):
        soup = response.scrap.soup
        fund_list = parse_xml_table_tag(soup, 'selectmeta', FUND_LIST_COLUMNS)
        self.fund_std_code_list = [row['표준코드'] for row in fund_list]
        return fund_list


class KofiaFundInfoScraper(KofiaScraper):
    # REQUEST_LOGGING = False
    LINK_RELAY = [
        url(
            'http://dis.kofia.or.kr/proframeWeb/XMLSERVICES/',
            payloader='fund_detail_payloader',
            parser='fund_detail_parser',
            name='fund_detail'
        ),
        url(
            'http://dis.kofia.or.kr/proframeWeb/XMLSERVICES/',
            payloader='fund_etc_payloader',
            parser='fund_etc_parser',
            name='fund_etc',
        ),
    ]

    def fund_detail_payloader(self, fund_std_code):
        log = f"Retrieve FundDetailInfo by FundCode: {fund_std_code}"
        print(log)
        payload = get_fund_detail_payload(fund_std_code)
        # self.fund_std_code = fund_std_code
        yield payload

    def fund_detail_parser(self, response, fund_std_code, **kwargs):
        soup = response.scrap.soup
        fund = parse_xml_table_tag(
            soup, 'comfundbasinfooutdto', FUND_DETAIL_COLUMNS,
            many=False
        )
        fund['표준코드'] = fund_std_code
        self.company_code = fund['회사코드']
        return fund

    def fund_etc_payloader(self, fund_std_code):
        payload = get_fund_etc_payload(fund_std_code, self.company_code)
        yield payload

    def fund_etc_parser(self, response, fund_std_code):
        soup = response.scrap.soup
        etc = parse_xml_table_tag(
            soup, 'comfundstdcotinfodto', FUND_DETAIL_COLUMNS,
            many=False
        )
        etc['표준코드'] = fund_std_code
        # etc['회사코드'] = self.company_code
        return etc


class KofiaPriceProgressScraper(KofiaScraper):
    CACHE_NAME = 'PROFP_SCRAP_CACHE_PRICE_PROGRESS'
    LINK_RELAY = [
        url(
            'http://dis.kofia.or.kr/proframeWeb/XMLSERVICES/',
            payloader='price_progress_payloader',
            parser='price_progress_parser',
            refresh=True,
            name='price_progress',
        )
    ]

    def price_progress_payloader(self, fund_std_code, company_code, initial_date):
        start_date = initial_date
        end_date = datetime.today().strftime("%Y%m%d")
        payload = get_price_change_progress_payload(
            fund_std_code, company_code,
            start_date=start_date,
            end_date=end_date
        )
        yield payload

    def price_progress_parser(self, response, fund_std_code, company_code, **kwargs):
        soup = response.scrap.soup
        price_progresses = parse_xml_table_tag(
            soup, 'pricemodlist', PRICE_PROGRESS_COLUMNS
        )
        for progress in price_progresses:
            progress['표준코드'] = fund_std_code
            # progress['회사코드'] = company_code
        return price_progresses


class KofiaSettleExSoScraper(KofiaScraper):
    LINK_RELAY = [
        url(
            'http://dis.kofia.or.kr/proframeWeb/XMLSERVICES/',
            payloader='fund_exso_payloader',
            parser='fund_exso_parser',
            refresh=True,
            name='fund_exso',
        ),
    ]

    def fund_exso_payloader(self, fund_std_code, company_code):
        payload = get_fund_exso_payload(fund_std_code, company_code)
        return payload

    def fund_exso_parser(self, response, fund_std_code, **kwargs):
        soup = response.scrap.soup
        exsos = parse_xml_table_tag(
            soup, 'settleexlist', SETTLE_EXSO_COLUMNS)
        for exso in exsos:
            exso['표준코드'] = fund_std_code
        return exsos


class KofiaSettleExSoByDateScraper(KofiaScraper):
    LINK_RELAY = [
        url(
            'http://dis.kofia.or.kr/proframeWeb/XMLSERVICES/',
            payloader='fund_exso_by_date_payloader',
            parser='fund_exso_by_date_parser',
            refresh=True,
            name='fund_exso_by_date',
        ),
    ]

    def fund_exso_by_date_payloader(self, start_date, end_date):
        payload = get_fund_exso_payload_by_date(start_date, end_date)
        log = f"Retrieve Fund Exso by Date Range: {start_date}~{end_date}"
        print(log)
        return payload

    def fund_exso_by_date_parser(self, response, **kwargs):
        soup = response.scrap.soup
        exsos = parse_xml_table_tag(
            soup, 'selectmeta',
            many=True,
            column_mapping=SETTLE_EXSO_BY_DATE_COLUMNS
        )
        return exsos
