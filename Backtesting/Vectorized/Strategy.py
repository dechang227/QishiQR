from copy import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class Strategy:
    """
    Base class of strategy to generate signals
    """
    def __init__(self, data):
        self.data = deepcopy(data)  # original data set is not changed so that we can always go back

    def generatingsignal(self):
        # self.data['signal'] = 0  # initiate all signal position to 0
        return self.data


class SLMStrategy(Strategy):
    """
    Statistical language model strategy
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
        self.data = pd.merge(self.data, self.slm[['prior', 'signal']], left_on=['prior'], right_on=['prior'],
                             how='left')
        self.data['signal'] = self.data['signal'].fillna(0).astype(int)
        #set last point before closing to be 0
        #set the first m points after opening to be 0
        return self.data
