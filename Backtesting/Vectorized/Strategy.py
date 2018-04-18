import copy
import pandas as pd
import numpy as np
from Utils.lm import *

class Strategy:
    """
    Base class of strategy to generate signals
    """
    def __init__(self, data):
        self.data = copy.deepcopy(data)  # original data set is not changed so that we can always go back

    def generatingsignal(self):
        # self.data['signal'] = 0  # initiate all signal position to 0
        return self.data


class MovingAverageStrategy(object):
    """
    Strategy: Moving Average
    Reference: https://www.investopedia.com/university/movingaverage/movingaverages4.asp

    Args:
        data: DataFrame, Input tick data
        short_window: int, size of the moving window for short position
        long_window: int, size of the long window for short position
    """
    def __init__(self, data, short_window=5, long_window=20):
        self.data = copy.deepcopy(data)  # original data set is not changed so that we can always go back
        self.short_window = short_window
        self.long_window = long_window

    def generatingsignal(self):
        self.data['signal'] = 0  # initiate all signal position to 0
        # self.data['closeMid'] = (self.data['closeBid'] + self.data['closeAsk']) / 2
        # use the open price to predict the price change and place order before the market closing
        self.data['fastma'] = self.data['LastPrice'].shift(1).rolling(window=self.short_window).mean()
        self.data['slowma'] = self.data['LastPrice'].shift(1).rolling(window=self.long_window).mean()
        self.data = self.data.dropna()
        self.data['signal'] = np.where(self.data['fastma'] > self.data['slowma'], 1, -1)
        return self.data


class SLMStrategy(Strategy):
    """
    Strategy: Statistical language model
    Arguments:
        SLM: word frequency data frame
        m: model degree
    """
    def __init__(self, data, slm, m, price='LastPrice'):
        Strategy.__init__(self, data)
        self.slm = slm
        self.m = m
        self.price = price
        # self.n = len(slm['signal'].unique())

    def generatingsignal(self):
        self.data = super(SLMStrategy, self).generatingsignal()
        self.data['Direction'] = self.data[self.price].pct_change().apply(lambda x: 2 if x > 0 else (1 if x < 0 else 0))
        sequence = self.data['Direction'].astype(str).str.cat()
        prior_ls = ['p'] * self.m + ['p' + sequence[i:i + self.m] for i in np.arange(len(sequence) - self.m)]
        # print(len(prior_ls))
        self.data['prior'] = prior_ls
        # self.data = pd.merge(self.data, self.slm[['prior', 'signal']], left_on=['prior'], right_on=['prior'],
        #                      how='left')
        self.data = self.data.reset_index().merge(self.slm[['prior', 'signal']],left_on=['prior'], right_on=['prior'],
                             how='left').set_index('index')
        self.data['signal'] = self.data['signal'].fillna(0).astype(int)
        #set last point before closing to be 0
        #set the first m points after opening to be 0
        return self.data
