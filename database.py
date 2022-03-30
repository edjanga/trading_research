import sqlite3
import pandas as pd

class DB(object):

    """
    Wrapper that eases connection to assets.db
    """
    def __init__(self, db_name):
        try:
            self.conn = sqlite3.connect(db_name)
            self.cur = self.conn.cursor()
        except sqlite3.OperationalError:
            print('Error while accessing the database')

    def assets_df(self,freq='daily'):
        query = "SELECT * FROM assets"
        self.cur.execute(query)
        col_ls = [name[0] for name in self.cur.description]
        row_ls = self.cur.fetchall()
        df = pd.DataFrame(data=row_ls,columns=col_ls)
        df = df.set_index('Date')
        df.index = pd.to_datetime(df.index)
        if freq == 'weekly':
            df = df.resample(rule='W-Fri', convention='s').agg('first')
        df = df.astype(float)
        return df

    def summary(self):
        df = self.assets_df()
        print(df.info())
        print(df.describe())