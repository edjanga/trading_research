import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


class Visualisation(object):

    def __init__(self, df):
        self.df = df

    @property
    def df(self):
        return self.__df

    @df.setter
    def df(self, df):
        self.__df = df

    def plot(self):
        plt.style.use('ggplot')
        fig, axes = plt.subplots(nrows=3,ncols=1, gridspec_kw={'height_ratios': [3, 1, 1]})
        self.df.plot(ax=axes[0], grid=True, title='Equity curves', figsize=(20, 7))
        axes[0].axhline(1, linestyle='--', color='#000000', linewidth=1)
        plt.xticks(rotation=2)
        mean_df = pd.DataFrame(self.df.mean()).reset_index().rename(columns={'index': 'strategy', 0: 'mean_return'})
        sns.barplot(x='mean_return', y='strategy', data=mean_df, ax=axes[1])
        std_df = pd.DataFrame(self.df.std()).reset_index().rename(columns={'index': 'strategy', 0: 'std_return'})
        sns.barplot(x='std_return', y='strategy', data=std_df, ax=axes[2])
        fig.tight_layout()
        plt.show()
