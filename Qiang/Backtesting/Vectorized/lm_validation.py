import numpy as np
import matplotlib.pyplot as plt

from Utils.IOUtils import *
import os
from Backtesting.Vectorized.Strategy import SLMStrategy
from Backtesting.Vectorized.backtest import vectorizedbacktest
from Backtesting.Vectorized.cross_compare import ensembler
from datetime import datetime  
from datetime import timedelta 

class LmValidation:
    def __init__(self, slm, symbol='ag', data_dir=r'../Output', valid_dir=r'../Validation', 
                 max_order=8, tca = 'Fixed', opt = 'CL', data_mode = 'Insample'):
        '''
        :param slm: language model dataframe having at least two columns: prior and signal
        :param symbol:
        :param data_dir: directory of testing files
        :param max_order: max order of model to test
        :param tca: transaction cost analysis applied, 'Fixed' with fixed cost of 1.2 bp, 'Spread' extimate trading cost based on bid-ask spread, 'Compound' will apply both cost
        :param opt: optimization to be applied to signal, 'CL' using signal confidence level to adjust the position size, 'Kelly' for Kelly Criterion to be applied based on past return variance
        :param data_mode: 'Insample' use data between July 1st and Sept. 30 for model and parameters selection, 'Outsample' use data between Oct. 1st and Dec. 31 for cross validation 
        '''
        self._slm = slm
        self._symbol = symbol
        self._data_dir = data_dir
        self._valid_dir = valid_dir
        self._max_order = max_order
        self._tca = tca
        self._opt = opt
        self._data_mode = data_mode
        self._sel_date = 'Span'

    def gen_find(self):
        '''
        Find all filenames in a directory tree that match a shell wildcard pattern.
        '''
        for path, dirlist, filelist in os.walk(self._data_dir):
            for name in fnmatch.filter(filelist, self._symbol + '*'):
                yield name

    def run(self):
        filenames = self.gen_find()
        
        if self._data_mode == 'Insample':
            start_time = '2016-7-1 09:00:00.0'
            end_time = '2016-10-1 09:00:00.0'
        else:
            start_time = '2016-10-1 09:00:00.0'
            end_time = '2016-12-31 23:59:59.0'
            
        for filename in filenames:
            data = pd.read_csv(self._data_dir + '/' + filename, index_col=0)
            data = data[(pd.to_datetime(data.index) >= start_time) & (pd.to_datetime(data.index) < end_time)]
            if len(data) == 0:
                continue
            else:
                signals = [SLMStrategy(data, self._slm, m).generatingsignal() for m in np.arange(1, self._max_order + 1)]
                tcas = [self._tca for m in np.arange(1, self._max_order +1)]
                opts = [self._opt for m in np.arange(1, self._max_order +1)]
                validator_ensemble = ensembler(vectorizedbacktest, signals, tcas, opts)
                validator_ensemble.build()
                validator_ensemble.run()
                performance = validator_ensemble.calperformance()
                performance.to_csv(self._valid_dir + '/performance_' + filename)
                validator_ensemble.plot()
                plt.savefig(self._valid_dir + '/performance_' + re.sub('.csv', '.png', filename))
                plt.close()
