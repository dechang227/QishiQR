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


if __name__ == "__main__":
    data_dir = '../tests/'
    data = pd.read_csv(data_dir + 'ag_1712_5min.csv')
    slm = pd.read_csv(data_dir + 'ag_5min_freq.csv')[['prior', 'max']]
    slm = slm.rename(columns={'max': 'signal'})
    signals = SLMStrategy(data, slm, 5).generatingsignal()
    signals['match'] = signals.apply(lambda row: 1 if row['signal'] == row['Direction'] else 0, axis=1)
    #print(signals['match'].describe())
    signals.to_csv(data_dir + 'ag_5min_signal.csv', index=False)

    """
    test paper strategy for SHA index
    """
    sha_data = pd.read_csv(data_dir + 'sha000001.csv')
    sha_data['Date'] = pd.to_datetime(sha_data['Date'], format="%m/%d/%Y")
    sha_data = sha_data[(sha_data['Date'] >= '2005-01-04') & (sha_data['Date'] <= '2013-12-31')]
    sha_data = sha_data.sort_values(by=['Date'])
    sha_strategy = pd.read_csv(data_dir + 'sha_strategy_6.csv')
    sha_signals = SLMStrategy(sha_data, sha_strategy, 5, price='ClosePrice').generatingsignal()
    sha_signals['change_pct'] = sha_signals['change_pct'].astype(float)
    sha_signals['strategy'] = sha_signals.apply(lambda row: row['change_pct'] if row['signal']==2 else (-1*row['change_pct'] if row['signal']==1 else 0), axis=1)
    sha_signals['cum_gain'] = sha_signals['strategy'].cumsum()
    sha_signals.to_csv(data_dir + 'sha_strategy_gain.csv')
    fig, ax1 = plt.subplots()
    ax1.plot(sha_signals['ClosePrice'])
    ax2 = ax1.twinx()
    ax2.plot(sha_signals['cum_gain'], color='red')
    fig.tight_layout()
    plt.show()



