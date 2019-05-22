import pandas as pd
import pymysql

from pfscrap.settings.db import DB_CON_KWARGS


class DBOrm:

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if k.lower() in ['port']:
                kwargs[k] = int(v)
            else:
                kwargs[k] = str(v)

        self.con = pymysql.connect(**kwargs)

    def get_df(self, table, where=None, columns=None):
        cols = '*'
        if columns is not None:
            cols = ','.join(columns)
        query = f"SELECT {cols} FROM {table}"
        if where is not None:
            query = f"SELECT {cols} FROM {table} WHERE {where}"
        df = pd.read_sql(query, self.con)
        return df

    def get_values_count(self, table, key=None, value=None):
        if key and value:
            query = f'SELECT COUNT(*) FROM {table} WHERE {key}={value}'
        else:
            query = f'SELECT COUNT(*) FROM {table}'
        df_counter = pd.read_sql(query, self.con)
        count = df_counter.loc[0, 'COUNT(*)']
        return count


# orm = DBOrm(**DB_CON_KWARGS)

# count = orm.get_values_count('FM_CLIENT', 'IS_ALIAS', 2)
# print('****'*50)
# print('count', count)
# df = orm.get_df('FM_CLIENT', columns=['ID', 'FP_ID'], where='IS_ALIAS=2')
# print('****'*50)
# print('df:', df.shape)
