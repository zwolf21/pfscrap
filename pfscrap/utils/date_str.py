from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

DATESTR_FMT = "%Y%m%d"
DEFAULT_AGO_DAYS = 7


def get_today_str_date(fmt=DATESTR_FMT):
    today = datetime.today()
    str_today = today.strftime(fmt)
    return str_today


def get_ago_str_date(fmt=DATESTR_FMT, **kwargs):
    today = datetime.today()
    ago = today - relativedelta(**kwargs)
    str_ago = ago.strftime(fmt)
    return str_ago


def get_date_ago_range(start_date=None, end_date=None, days_ago=None, months_ago=None, years_ago=None, default_ago_days=DEFAULT_AGO_DAYS):
    end_date = end_date or get_today_str_date()

    if start_date:
        start_date = start_date
    elif days_ago:
        start_date = get_ago_str_date(days=days_ago)
    elif months_ago:
        start_date = get_ago_str_date(months=months_ago)
    elif years_ago:
        start_date = get_ago_str_date(years=years_ago)
    else:
        start_date = get_ago_str_date(days=default_ago_days)

    if start_date > end_date:
        raise ValueError('start_date > end_date')
    return start_date, end_date

