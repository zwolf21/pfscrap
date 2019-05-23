import pandas as pd
import pymysql

from sqlalchemy import create_engine


class DBOrm:

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if k.lower() in ['port']:
                kwargs[k] = int(v)
            else:
                kwargs[k] = str(v)
        con_str = "mysql+pymysql://{user}:{passwd}@{host}:{port}/{db}?charset={charset}".format(
            **kwargs)
        engin = create_engine(con_str, encoding='utf-8')
        self.con = engin.connect()

    def _get_now(self):
        return pd.Timestamp.now()

    def insert_db(self, df, table, if_exists='append', column_mapping=None):
        if column_mapping:
            df = df.rename(columns=column_mapping)
        df.to_sql(table, self.con, if_exists=if_exists, index=False)

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
