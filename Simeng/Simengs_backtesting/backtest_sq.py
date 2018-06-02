import numpy as np
import pandas as pd
from Simengs_utils.IOUtils_sq import *
from Simengs_backtesting.Strategy_sq import *


class vectorizedbacktest:
    def __init__(self, data, tca = 'None', tca_spread = 0.5, tca_fix=0.00012):
        self.data = data # price history data
        self.tca = tca # trading cost to be applied
        self.result = 'please run backtest first'
        self.performance = 'please calculate performance first'
        self.tca_spread = tca_spread
        self.tca_fix = tca_fix

    def runtest(self):
        self.result = self.data

#        self.result['tradeID'] = (~(self.result['signal']==self.result['signal'].shift(1))).cumsum()
        self.result['return'] = np.log(self.result['LastPrice']/self.result['LastPrice'].shift(1))
        ##SQ version considering the instrument change
        ##SQ self.result['return'][0] = 0.0
        self.result['InstrumentID_prior'] = self.result['InstrumentID'].shift(1)
        self.result.loc[self.result['InstrumentID']!= self.result['InstrumentID_prior'], 'return'] = 0


        self.result['signal_bar'] = self.result['signal'].apply(lambda x: 1 if x == 2 else (-1 if x == 1 else 0))
#        self.result['signal_bar'][0] = 0

        ## SQ
        self.result.loc[(abs(self.result['signal_bar'])==1) | (self.result.flag_start_trade == 1),'pos'] = self.result[(abs(self.result['signal_bar'])==1) | (self.result.flag_start_trade == 1)]['signal_bar']
        self.result.loc[self.result.flag_end_trade == 1, 'pos'] = 0
        self.result['pos'].fillna(method='ffill',inplace=True) ##SQ fill when signal_bar = 0

        self.result['tradeVolume'] = abs(self.result['pos'] - self.result['pos'].shift(1))
        self.result.loc[self.result.index[0],'tradeVolume'] = 1
        self.result['tradeID'] = (self.result['tradeVolume']>0).cumsum()

        
        
#        self.result['signal_chg_size'] = abs(self.result['signal_bar'] - self.result['signal_bar'].shift(1))
#        self.result['signal_chg'] = (~(self.result['signal']==self.result['signal'].shift(1)))
        self.result['strategy'] = self.result['return'] * self.result['signal_bar']
 
        # This step is to take into account of transaction cost. For every order, return reduced by half of the spread
        
        ##SQ Trading Cost need to be double check
        if(self.tca == 'Spread' or self.tca =='Compound'):
            self.result['strategy'] = self.result['strategy'] - self.tca_spread * np.log(self.result['AskPrice1']/self.result['BidPrice1']) * self.result['tradeVolume']
        #  
        if(self.tca == 'Fixed' or self.tca == 'Compound'):
            self.result['strategy'] = self.result['strategy'] - self.tca_fix * self.result['tradeVolume']
        
#        self.result.index = self.data.index
        return self.result
 
    def calperformance(self):
        self.result['benchmark'] = self.result['return'].cumsum() + 1
        self.result['equitycurve'] = self.result['strategy'].cumsum() + 1
        self.result['drawdown'] = self.result['equitycurve']/(self.result['equitycurve'].expanding().max())-1
        drawdown_max = self.result['drawdown'].min()
        # regroup to calculate daily return, this is used to calculate the annualized std and sharpe ratio
        daily_returns = self.result['strategy'].groupby(self.result['Date']).sum()
        daily_bm_returns = self.result['return'].groupby(self.result['Date']).sum()
        #daily_excess_returns = daily_returns - daily_bm_returns
        #self.daily_return = daily_returns.aggregate(np.sum)
        vol = daily_returns.std() * ((250)**0.5)
        average_daily_return_log = daily_returns.mean()
        average_daily_return = np.exp(average_daily_return_log)
        total_return = np.exp(self.result['equitycurve'].iloc[-1]-1)
        with np.errstate(divide='raise'):
            try:
                sharpe = (average_daily_return_log * 250) / vol
            except Warning:
                sharpe = 0
        
        #average_daily_excess_return = daily_exess_return.mean()
        #excess_vol = daily_excess_return.std() * ((250)**0.5)
        #ir = (average_daily_excess_return * 250)/ excess_vol
        # trade analysis
        trades = self.result[['strategy', 'tradeID']].groupby('tradeID')
        self.trade = trades.aggregate(np.sum)
        total_count = self.trade['strategy'].count()

#        total_count = self.result['tradeVolume'].sum()
        positive_count = (self.trade['strategy'][self.trade['strategy']>0]).count()
        winning_rate = positive_count/total_count
        #negative_count = (self.trade['strategy'][self.trade['strategy']&lt;0]).count() winning_rate = float(positive_count) / total_count average_positive_return = (self.trade['strategy'][self.trade['strategy']&gt;0]).mean()
        average_negative_return = np.exp((self.trade['strategy'][self.trade['strategy']<0]).mean())
        average_positive_return = np.exp((self.trade['strategy'][self.trade['strategy']>0]).mean())
        profit_factor = - average_positive_return / average_negative_return
        average_return = np.exp(self.trade['strategy'].mean())
        max_trade = np.exp(self.trade['strategy'].max())
        min_trade = np.exp(self.trade['strategy'].min())
 
        # store trade metrics
        self.performance = {'Total Number of Trades': total_count, 
        'Winning Rate': winning_rate, 
        'Profit Factor': profit_factor, 
        'Average Daily Return': average_daily_return,
        'Average Return per Trade': average_return, 
        'Average Positive Return': average_positive_return, 
        'Average Negative Return': average_negative_return, 
        'Max Drawdown': drawdown_max, 
        'Total Return': total_return, 
        'Annualized Volatility(log)': vol,
        'Sharpe Ratio(log)': sharpe,
        #'Information Ratio':ir,
        'Largest Winning Trade': max_trade, 
        'Largest Losing Trade': min_trade}
