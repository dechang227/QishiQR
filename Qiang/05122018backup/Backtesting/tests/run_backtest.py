import sys
import os
sys.path.append('/home/rz14/Documents/QR_Qishi/QishiQR/Backtesting/')
#sys.path.append('/Users/z_runmin/Documents/QishiQR/Backtesting')
print(sys.path)

from Backtesting.Vectorized.random_forecast import MovingAverageCrossStrategy, MarketOnOpenPortfolio
import quandl

symbol = 'MSFT'
bars = quandl.get("WIKI/%s" % symbol, collapse="daily")

# Create a set of random forecasting signals for SPY
# rfs = RandomForecastingStrategy(symbol, bars)
rfs = MovingAverageCrossStrategy(symbol, bars)
signals = rfs.generate_signals()

# Create a portfolio of SPY
portfolio = MarketOnOpenPortfolio(symbol, bars, signals, initial_capital=100000.0)
positions = portfolio.generate_positions(bars)
returns = portfolio.backtest_portfolio()

##returns.tail(10)
bars.tail(10)

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.figure(figsize=(20,10))
plt.plot(returns['acc. returns'])
plt.ylabel('PnL')
plt.show()