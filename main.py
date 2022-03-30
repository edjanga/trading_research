from database import DB
from strategies import Rule
from backtesting import Visualisation
import pandas as pd

if __name__ == '__main__':

    db_name = 'commodities.db'
    db_obj = DB(db_name)
    db_obj.summary()
    universe_df = db_obj.assets_df(freq='weekly')
    ret_df = universe_df.pct_change().dropna(axis=0)
    allocator_obj = Rule(ret_df)
    full_strategies_df = pd.DataFrame()
    equally_weighted_s = allocator_obj.equally_weighted()
    min_variance_s = allocator_obj.min_variance()
    #efficient_portfolio_s = allocator_obj.efficient_portfolio()
    momentum1_s = allocator_obj.momentum1()
    mean_reversion1_s = allocator_obj.mean_reversion1()
    ls = [equally_weighted_s, min_variance_s, momentum1_s,mean_reversion1_s]
    for strategy, df in enumerate(ls):
        full_strategies_df = pd.concat([full_strategies_df, df], axis=1)
    first_valid_date_s = full_strategies_df.apply(pd.Series.first_valid_index)
    first_valid_date_s = first_valid_date_s.sort_values(ascending=False)
    full_strategies_df = full_strategies_df.loc[first_valid_date_s[0]:, :]
    full_strategies_df = full_strategies_df / full_strategies_df.iloc[0, :]
    print(full_strategies_df.describe())
    backtesting_obj = Visualisation(full_strategies_df)
    backtesting_obj.plot()
    db_obj.close()