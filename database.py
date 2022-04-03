import sqlite3
import pandas as pd
import glob

class DB(object):

    """
    Wrapper that eases connection to etf.db
    """
    def __init__(self, db_name):
        try:
            self.conn = sqlite3.connect(db_name)
            self.cur = self.conn.cursor()
        except sqlite3.OperationalError:
            print('Error while accessing the database')

    def close(self):
        self.conn.close()

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


class FX_data(object):

    def __init__(self):
        pass

    @staticmethod
    def fx_data(instrument='spot'):
        fx_conn = sqlite3.connect('fx.db')
        if instrument in ['spot','fwdp']:
            data_df = pd.DataFrame()
            path = glob.glob('data/*_%s.csv' %instrument)
            for i, file in enumerate(path):
                print('%s: Treating %s' %(i,file))
                temp = pd.read_csv(file)
                currency = file.split('/')[-1].split('_')[0]
                temp['Date'] = pd.to_datetime(temp['Date'])
                temp = temp.set_index('Date')
                temp = temp.rename(columns={temp.columns[0]:currency})
                data_df = pd.concat([data_df,temp],axis=1)
            data_df = data_df.sort_index(ascending=True)

        elif instrument == 'VIX':
            file = 'data/VIX.csv'
            data_df = pd.read_csv(file)
            data_df['Date'] = pd.to_datetime(data_df['Date'])
            data_df = data_df.set_index('Date')
            data_df = data_df.rename(columns={data_df.columns[0]: instrument})
            data_df = data_df.sort_index(ascending=True)

        elif instrument == 'dates':
            file = 'data/RebalanceDates.csv'
            data_df = pd.read_csv(file)
            data_df['Date'] = pd.to_datetime(data_df['Date'])
            data_df = data_df.rename(columns={'Date': 'RebalanceDate'})
            data_df = data_df.sort_values(by='RebalanceDate', ascending=True)

        elif instrument == 'info':
            file = 'data/info.csv'
            data_df = pd.read_csv(file)
        data_df.to_sql(name=instrument, if_exists='fail', con=fx_conn)
        print('%s has been inserted to fx.db.' %instrument)
        return True

if __name__ == '__main__':
    fx_obj = FX_data()
    fx_obj.fx_data('spot')
    fx_obj.fx_data('fwdp')
    fx_obj.fx_data('VIX')
    fx_obj.fx_data('dates')
    fx_obj.fx_data('info')