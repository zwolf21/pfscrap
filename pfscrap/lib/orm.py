import pandas as pd
import pymysql
import sqlite3

from sqlalchemy import create_engine


class DBOrm:

    def __init__(self, **kwargs):
        self.con = self._get_connection(**kwargs)
    
    def _get_connection(self, **kwargs):
        db_backend = kwargs.get('backend', 'sqlite3')
        if db_backend == 'sqlite3':
            con = sqlite3.connect(**kwargs)
        elif db_backend == 'mysql':
            con_str_fmt = "mysql+pymysql://{user}:{passwd}@{host}:{port}/{db}?charset={charset}"
            con_str = con_str_fmt.format(**kwargs)
            engin = create_engine(con_str, encoding='utf-8')
            con = engin.connect()
        return con
        
    def _get_now(self):
        return pd.Timestamp.now()

    def insert_db(self, df, table, if_exists='append', column_mapping=None, updated=None, created=None):
        if column_mapping is not None:
            df = df.rename(columns=column_mapping)
        if created is not None:
            df[created] = self._get_now()
        if updated is not None:
            df[updated] = self._get_now()
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

