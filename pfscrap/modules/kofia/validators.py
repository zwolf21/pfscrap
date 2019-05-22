from .scrap_column_mappings import FUND_LIST_COLUMNS, FUND_DETAIL_COLUMNS


def validate_fund_list(df_fund_list):
    df_columns = set(df_fund_list.columns)

    fund_list_columns = set(FUND_LIST_COLUMNS.values())
    fund_list_detail_columns = set(
        list(FUND_LIST_COLUMNS.values()) + list(FUND_DETAIL_COLUMNS.values())
    )
    if set(fund_list_columns) == set(df_columns):
        return True
    if set(fund_list_detail_columns) == set(df_columns):
        return True
    return False
