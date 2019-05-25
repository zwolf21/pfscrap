from collections import abc
import sqlite3

import pandas as pd
import pymysql

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

    def filter_df_not_exists(self, table, df, filter_by):
        table_index = []
        df_index = []
        if isinstance(filter_by, abc.Mapping):
            tablebydf = filter_by.items()
        elif isinstance(filter_by, (list, tuple)):
            tablebydf = filter_by
        else:
            raise ValueError('filter by must be list, tuple or dict')

        for db_col, df_col in tablebydf:
            table_index.append(db_col)
            df_index.append(df_col)

        df_table = self.get_df(table, columns=table_index)
        df_table = df_table.set_index(table_index)
        df = df.set_index(df_index)
        mask = ~df.index.isin(df_table.index)
        df = df[mask]
        df = df.reset_index()
        return df

    def get_max(self, table, column):
        query = f"SELECT MAX({column}) FROM {table}"
        df_max = pd.read_sql(query, self.con)
        return df_max.loc[0, f"MAX({column})"]

    def get_min(self, table, column):
        query = f"SELECT MIN({column}) FROM {table}"
        df_min = pd.read_sql(query, self.con)
        return df_min.loc[0, f"MIN({column})"]

    def delete_table(self, table, where=None):
        if where is None:
            query = f"DELETE FROM {table} WHERE 1>0"
        else:
            query = f"DELETE FROM {table} {where}"
        self.con.execute(query)

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

    def close(self):
        self.con.close()

    def __del__(self):
        self.con.close()
