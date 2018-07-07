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
    
class RandomForecastingStrategy(Strategy):
    # random generated signal for bactekster validation
    def __init__(self, data, m = 0):
        Strategy.__init__(self, data)
        self._m = m #module order
    def generatingsignal(self):
        signal_len = self.data.shape[0]
        self.data['signal'] = np.random.random_integers(0,2,signal_len)
        self.data['signal'][0:5] = 0
        self.data['max_pct'] = 0
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


class SLMStrategy:
    """
    Strategy: Statistical language model
    Arguments:
        SLM: word frequency data frame
        m: model degree
    """
    def __init__(self, data, slm, m, price='LastPrice', **kwargs):
        #super(SLMStrategy, self).__init__(self, data)
        self.data = copy.deepcopy(data)  # original data set is not changed so that we can always go back
        self.slm = slm
        self.m = m
        self.price = price
        self._price_threshold = kwargs.get('px_th', 0)
        # self.n = len(slm['signal'].unique())

    def generatingsignal(self):
        #self.data = super(SLMStrategy, self).generatingsignal()
        #self.data = super().generatingsignal()
        if self._price_threshold >= 1:
            self.data['Direction'] = self.data[self.price].diff().apply(
                lambda x: 2 if x > self._price_threshold else (1 if x < -self._price_threshold else 0))
        else:
            self.data['Direction'] = self.data[self.price].pct_change().apply(lambda x: 2 if x > self._price_threshold else (1 if x < -self._price_threshold else 0))

        sequence = self.data['Direction'].astype(str).str.cat()
        prior_ls = ['p'] * self.m + ['p' + sequence[i:i + self.m] for i in np.arange(len(sequence) - self.m)]
        # print(len(prior_ls))
        self.data['prior'] = prior_ls
        # self.data = pd.merge(self.data, self.slm[['prior', 'signal']], left_on=['prior'], right_on=['prior'],
        #                      how='left')
        self.data = self.data.reset_index().merge(self.slm[['prior','max_pct', 'signal']],left_on=['prior'], right_on=['prior'],
                             how='left').set_index('index')
        self.data['signal'] = self.data['signal'].fillna(0).astype(int)
        #set last point before closing to be 0
        #set the first m points after opening to be 0
        return self.data


class SLM:
    def __init__(self, slm, threshold, th_type=0):
        self._slm = copy.deepcopy(slm)
        self._threshold = threshold
        self._type = th_type

    def run(self):
        self._slm['max'] = self._slm.loc[:, '0':'2'].idxmax(axis=1)
        self._slm['max_pct'] = self._slm.loc[:, '0':'2'].max(axis=1) / self._slm['total']
        self._slm['min'] = self._slm.loc[:, '0':'2'].idxmin(axis=1)
        self._slm['min_pct'] = self._slm.loc[:, '0':'2'].min(axis=1) / self._slm['total']
        # difference of top 2 probablities
        self._slm['threshold'] = 2 * self._slm['max_pct'] + self._slm['min_pct'] - 1
        self._slm['order'] = self._slm['prior'].apply(len)
        self._slm = self._slm.sort_values(by='order').reset_index(drop=True)#.drop(columns=['index'])
        assert self._threshold < 1
        if self._type == 1:
            # type 1: simple threshold cutoff, 0.5
            self._slm['signal'] = self._slm[['max', 'max_pct']].apply(lambda x: x['max'] if x['max_pct'] > self._threshold else 0, axis=1).astype(int)
        elif self._type == 2:
            # type 2: threshold for the difference of top 2 probs, 0.1
            self._slm['signal'] = self._slm.apply(lambda x: x['max'] if x['threshold'] > self._threshold else 0, axis=1).astype(int)
        elif self._type == 3:
            # type 3: consider only threshold for case of 1 and 2 are top 2 probs, 0.1
            self._slm['signal'] = self._slm.apply(lambda x: 0 if (x['threshold'] <= self._threshold and x['min'] == '0') else x['max'], axis=1).astype(int)
        else:
            self._slm['signal'] = self._slm['max']
        return self._slm#[['prior', 'max_pct', 'min_pct', 'signal']]
