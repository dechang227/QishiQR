import numpy as np
import pandas as pd


class vectorizedbacktest:
    def __init__(self, data, window = 0, pct_th =0.52, tca = 'None'):
        self.data = data # price history data
        self.tca = tca # trading cost to be applied
        self.result = 'please run backtest first'
        self.performance = 'please calculate performance first'
        self.window = window
        self.pct_th = pct_th
        
    def runtest(self):
        self.result = self.data
        self.result['return'] = np.log(self.result['LastPrice']/self.result['LastPrice'].shift(1))
        self.result['return'].iloc[0] = 0.0
        self.result['correct'] = [direct == signal for direct, signal in zip(self.result['Direction'], self.result['signal'])]
        if self.window>0:
            signal_bar = [0]*self.window
            self.result['correct_pct'] = self.result['correct'].shift(1).rolling(window = self.window).sum()/self.window
        
            total_rows = self.result.shape[0]
        
            for index in range(self.window, total_rows):
                next_signal = 0 if (self.result['correct_pct'][index] > self.pct_th) else (1 if (self.result['signal'][index] == 2) else (-1 if (self.result['signal'][index] == 1)  else signal_bar[-1]))
                signal_bar.append(next_signal)
            self.result['signal_bar'] = signal_bar
            
        elif self.window == 0:
            signal_bar = [0]
            total_rows = self.result.shape[0]

            for index in range(1, total_rows):
                next_signal = 1 if (self.result['signal'][index] ==2) else (-1 if (self.result['signal'][index] == 1) 
                                                                            else signal_bar[-1])
                signal_bar.append(next_signal)
                
            self.result['signal_bar'] = signal_bar
            
        else:
            self.result['signal_bar'] = self.result['signal'].apply(lambda x: 1 if x == 2 else (-1 if x == 1 else 0))
            self.result['signal_bar'][0] = 0            
        
        self.result['tradeID'] = (~(self.result['signal']==self.result['signal'].shift(1))).cumsum()
        self.result['signal_chg_size'] = abs(self.result['signal_bar'] - self.result['signal_bar'].shift(1))
        self.result['signal_chg'] = (~(self.result['signal']==self.result['signal'].shift(1)))
        self.result['strategy'] = self.result['return'] * self.result['signal_bar']
 
        # This step is to take into account of transaction cost. For every order, return reduced by half of the spread
        if(self.tca == 'Spread' or self.tca =='Compound'):
            #
            self.result['strategy'] = self.result['strategy']-0.5*np.log(self.result['AskPrice1']/self.result['BidPrice1'])*self.result['signal_chg_size']
        #  
        if(self.tca == 'Fixed' or self.tca == 'Compound'):
            #0.00012 is trading cost, 0.0004 is for bid-ask spread to count
            self.result['strategy'] = self.result['strategy']-0.00052*self.result['signal_chg']
        
        self.result.index = self.data.index
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
        average_daily_return = daily_returns.mean()
        total_return = self.result['equitycurve'].iloc[-1]
        with np.errstate(divide='raise'):
            try:
                sharpe = (average_daily_return * 250) / vol
            except Warning:
                sharpe = 0
        
        #average_daily_excess_return = daily_exess_return.mean()
        #excess_vol = daily_excess_return.std() * ((250)**0.5)
        #ir = (average_daily_excess_return * 250)/ excess_vol
        # trade analysis
        trades = self.result[['strategy', 'tradeID']].groupby('tradeID')
        self.trade = trades.aggregate(np.sum)
        total_count = self.trade['strategy'].count()
        positive_count = (self.trade['strategy'][self.trade['strategy']>0]).count()
        winning_rate = positive_count/total_count
        #negative_count = (self.trade['strategy'][self.trade['strategy']&lt;0]).count() winning_rate = float(positive_count) / total_count average_positive_return = (self.trade['strategy'][self.trade['strategy']&gt;0]).mean()
        average_negative_return = (self.trade['strategy'][self.trade['strategy']<0]).mean()
        average_positive_return = (self.trade['strategy'][self.trade['strategy']>0]).mean()
        profit_factor = - average_positive_return / average_negative_return
        average_return = self.trade['strategy'].mean()
        max_trade = self.trade['strategy'].max()
        min_trade = self.trade['strategy'].min()
 
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
        'Annualized Volatility': vol, 
        'Sharpe Ratio': sharpe, 
        #'Information Ratio':ir,
        'Largest Winning Trade': max_trade, 
        'Largest Losing Trade': min_trade}
