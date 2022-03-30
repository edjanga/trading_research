import pandas as pd
import numpy as np
from scipy.optimize import minimize


class Rule(object):

    """
    Class that provides one with different portfolio allocation techniques.
    """

    def __init__(self, df):
        self.ret = df.shift().replace(np.nan, 0)

    @property
    def ret(self):
        return self.__ret

    @ret.setter
    def ret(self, df):
        self.__ret = df

    def equally_weighted(self, type = 'equity'):
        n = self.ret.shape[1]
        if type == 'equity':
            equity_s = ((self.ret.sum(axis=1)/n)+1).cumprod()
            equity_s.name = 'equally_weighted'
            return equity_s
        else:
            ret_dist_s = self.ret.sum(axis=1) / n
            ret_dist_s.name = 'equally_weighted'
            return ret_dist_s

    def min_variance(self, type = 'equity'):

        n = self.ret.shape[1]
        cov = self.ret.expanding().cov().dropna()
        ret_copy = self.ret.copy()
        ret_copy = ret_copy.loc[cov.index.get_level_values(0).unique(), :]
        weight_ls = [[0 for _ in range(0, ret_copy.shape[1])]]

        def objective_function(weight, cov):
            return np.dot(np.transpose(weight), np.dot(cov, weight))

        #Fully invested portfolio
        cons = {'type': 'eq', 'fun': lambda x: sum(x) - 1}
        for date, row in ret_copy.iterrows():
            res = minimize(objective_function, x0=weight_ls[-1], args=cov.loc[date,:], constraints=cons)
            weight_ls.append(res.x)
        weight = pd.DataFrame(data=weight_ls[:-1], index=ret_copy.index, columns=ret_copy.columns)
        portfolio_s = ret_copy.mul(weight).sum(axis=1)
        if type == 'equity':
            equity_s = (portfolio_s+1).cumprod()
            equity_s.name = 'min_variance'
            return equity_s
        else:
            ret_dist_s = portfolio_s
            ret_dist_s.name = 'min_variance'
            return ret_dist_s

    def efficient_portfolio(self, type='equity', target=1):
        """
        Portfolio allocation that minimises the portfolio variance with a target return constraint
        """
        # Scaling annualised target
        n_weeks = float((self.ret.index[-1]-self.ret.index[0])/np.timedelta64(1, 'W'))
        target = n_weeks*(target**(1/n_weeks)-1)
        n = self.ret.shape[1]
        cov = self.ret.expanding().cov().dropna()
        ret_copy = self.ret.copy()
        ret_copy = ret_copy.loc[cov.index.get_level_values(0).unique(), :]
        weight_ls = [[0 for _ in range(0, ret_copy.shape[1])]]

        def objective_function(weight, cov):
            return np.dot(np.transpose(weight), np.dot(cov, weight))

        for date, row in ret_copy.iterrows():
            # Fully invested portoflio + Matching target
            cons = ({'type': 'eq', 'fun': lambda x: sum(x*row) - target},
                    {'type': 'eq', 'fun': lambda x: sum(x) - 1},)
            res = minimize(objective_function, x0=weight_ls[-1], args=cov.loc[date,:], constraints=cons)
            weight_ls.append(res.x)
        weight = pd.DataFrame(data=weight_ls[:-1], index=ret_copy.index, columns=ret_copy.columns)
        portfolio_s = ret_copy.mul(weight).sum(axis=1)
        if type == 'equity':
            equity_s = (portfolio_s+1).cumprod()
            equity_s.name = 'efficient_portfolio'
            return equity_s
        else:
            ret_dist_s = portfolio_s
            ret_dist_s.name = 'efficient_portfolio'
            return ret_dist_s

    def momentum1(self, type = 'equity', n=10):
        """
        Long top n performers and short n bottom performers
        Equally weighted allocation amongst each group
        """
        weight = pd.DataFrame(columns=self.ret.columns)
        for date, row in self.ret.iterrows():
            temp_s = row.sort_values(ascending=False)
            temp_s[:n] = 1/n
            temp_s[-n:] = -1/n
            temp_s[n:-n] = 0
            temp_df = pd.DataFrame(temp_s).T
            weight = pd.concat([weight,temp_df],axis=0)
        portfolio_s = self.ret.mul(weight.shift()).sum(axis=1)
        if type == 'equity':
            equity_s = (portfolio_s + 1).cumprod()
            equity_s.name = 'momentum1'
            return equity_s
        else:
            ret_dist_s = portfolio_s
            ret_dist_s.name = 'momentum1'
            return ret_dist_s

    def mean_reversion1(self, type = 'equity', n=10):
        """
        Short top n performers and long n bottom performers
        Equally weighted allocation amongst each group
        """
        weight = pd.DataFrame(columns=self.ret.columns)
        for date, row in self.ret.iterrows():
            temp_s = row.sort_values(ascending=False)
            temp_s[:n] = -1/n
            temp_s[-n:] = 1/n
            temp_s[n:-n] = 0
            temp_df = pd.DataFrame(temp_s).T
            weight = pd.concat([weight,temp_df],axis=0)
        portfolio_s = self.ret.mul(weight.shift()).sum(axis=1)
        if type == 'equity':
            equity_s = (portfolio_s + 1).cumprod()
            equity_s.name = 'mean_reversion1'
            return equity_s
        else:
            ret_dist_s = portfolio_s
            ret_dist_s.name = 'mean_reversion1'
            return ret_dist_s

    # def eigenvalue_strat(self,tau = 99, alpha = .33, beta = .66):
    #     """
    #     Implementation of trading strategy describe by Duran and Bommarito
    #     """
    #     #tau += 1
    #     #start_date = self.ret.index.loc[tau-1]
    #     #weight = pd.DataFrame(columns=self.ret.columns)
    #     weight_ls = []
    #     #for date, row in self.ret.iterrows():
    #     for i in range(101,self.ret.shape[0]):
    #         corr_past = self.ret.iloc[:i-1,:].corr()
    #         corr_current = self.ret.iloc[:i, :].corr()
    #         max_eigen = max(np.linalg.eigvals(corr_current))
    #         lower,upper = np.percentile(np.linalg.eigvals(corr_current),alpha), \
    #                       np.percentile(np.linalg.eigvals(corr_current), beta)
    #         if (max_eigen > beta) | (max_eigen < alpha):
    #             weight_ls.append([0 for _ in range(0,self.ret.shape[1])])
    #         else:
    #             mean_df = self.ret.iloc[:i,:].expanding().mean()
    #             pdb.set_trace()
    #             std_df = self.ret.iloc[:i,:].expanding().std()
    #             skew_df = self.ret.iloc[:i,:].expanding().apply(skew)
    #             kurtosis_df = self.ret.iloc[:i,:].expanding().apply(kurtosis)
    #         pdb.set_trace()



