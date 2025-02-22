import numpy as np
import matplotlib.pyplot as plt

import importlib
import Backtesting.Vectorized.cross_compare
importlib.reload(Backtesting.Vectorized.cross_compare)

from Utils.IOUtils import *
import os
from Backtesting.Vectorized.Strategy import SLMStrategy
from Backtesting.Vectorized.backtest import vectorizedbacktest
from Backtesting.Vectorized.cross_compare import ensembler

class LmValidation:
    def __init__(self, slm, start='2016-7-1', end='2016-10-1',symbol='ag', data_dir=r'../../Output', valid_dir=r'../../Validation', min_order=2, max_order=8, offsets_average = False, n_offsets = 5, tca = None, price='LastPrice', fixed_cost = 0.00052,**kwargs):
        '''
        :param slm: language model dataframe having at least two columns: prior and signal
        :param symbol:
        :param data_dir: directory of testing files
        :param max_order: max order of model to test
        '''
        self._slm = slm
        self._symbol = symbol
        self._data_dir = data_dir
        self._valid_dir = valid_dir
        self._min_order = min_order
        self._max_order = max_order
        self._offsets_average = offsets_average
        self._average_return = None
        self._n_offsets = n_offsets
        self._start = start
        self._end = end
        self._price_threshold = kwargs.get('px_th', 0)
        self._price=price
        self._tca = tca
        self._fixed_cost = fixed_cost

    def gen_find(self):
        '''
        Find all filenames in a directory tree that match a shell wildcard pattern.
        '''
        for path, dirlist, filelist in os.walk(self._data_dir):
            for name in fnmatch.filter(filelist, self._symbol + '*'):
                yield name

    def run(self):
        filenames = self.gen_find()
        for filename in filenames:
            print(filename)
            data = pd.read_csv(self._data_dir + '/' + filename, index_col=0)
            data = data[(pd.to_datetime(data.index) >= pd.to_datetime(self._start)) & (pd.to_datetime(data.index) < pd.to_datetime(self._end))]
            if len(data) == 0:
                continue
            else:
                signals = [SLMStrategy(data, self._slm, m-1, px_th=self._price_threshold).generatingsignal() for m in np.arange(self._min_order, self._max_order+1)]
                #tcas = [self._tca for m in np.arange(self._min_order + 1, self._max_order + 1)]
                tcas = [self._tca]*(self._max_order - self._min_order + 1)
                validator_ensemble = ensembler(vectorizedbacktest, signals, price=self._price, tcas = tcas, fixed_cost=self._fixed_cost)
                validator_ensemble.build()
                validator_ensemble.run()

                performance = validator_ensemble.calperformance()
                performance.to_csv(self._valid_dir + '/performance_' + filename)
                validator_ensemble.plot()
                plt.savefig(self._valid_dir + '/performance_' + re.sub('.csv', '.png', filename))
                plt.close()
                # validator_ensemble.plot(target_col="benchmark")
                # plt.savefig(self._valid_dir + '/benchmark_' + re.sub('.csv', '.png', filename))
                # plt.close()
                fig = plt.figure()
                #benchmark = validator_ensemble.results[0]['return'].cumsum() + 1
                benchmark = validator_ensemble.results[0]['benchmark']
                #print(len(benchmark.index))
                #initial_value = benchmark[0]
                #benchmark = benchmark/initial_value
                benchmark.plot()
                plt.title('Benchmark')
                fig.savefig(self._valid_dir + '/benchmark_' + re.sub('.csv', '.png', filename))
                plt.close()

                if self._offsets_average:
                    if not self._average_return:
                        self._average_return = [df['strategy'].reset_index(drop=True) for df in validator_ensemble.results]
                        average_performance = performance
                        average_benchmark = validator_ensemble.results[0]['benchmark']
                        #avg_equitycurve = [df['equitycurve'].reset_index(drop=True) for df in validator_ensemble.results]
                    else:
                        self._average_return = [df1.add(df2['strategy'].reset_index(drop=True), fill_value=0) for (df1, df2) in zip(self._average_return, validator_ensemble.results)]
                        average_performance = average_performance.add(performance, fill_value=0)
                        #avg_equitycurve = [df1.add(df2['equitycurve'].reset_index(drop=True), fill_value=0) for (df1, df2) in zip(avg_equitycurve, validator_ensemble.results)]
                        #average_benchmark = average_benchmark.add(validator_ensemble.results[0]['LastPrice'], fill_value=0)
        '''
        average return of all offsets
        '''
        if self._offsets_average and (self._average_return is not None):
            self._average_return = [(1+df.divide(self._n_offsets)).cumprod() for df in self._average_return]
            #avg_equitycurve = [df.divide(self._n_offsets) for df in avg_equitycurve]
            #average_benchmark = average_benchmark/average_benchmark[0]
            average_benchmark = average_benchmark.to_frame()
            average_benchmark['Date'] = pd.to_datetime(average_benchmark.index)
            #print(average_benchmark)
            fig = plt.figure()
            plt.plot(average_benchmark.Date, average_benchmark.benchmark, label='b')
            for avg_return, label in zip(self._average_return, np.arange(self._min_order, self._max_order+1)):
            #for avg_return, label in zip(avg_equitycurve, np.arange(2, 2 + len(avg_equitycurve))):
                #avg_return.plot(label=label)
                df = avg_return.to_frame()
                df = df.set_index(average_benchmark.index)
                df['Date'] = pd.to_datetime(df.index)
                plt.plot(df.Date, df.strategy, label=label)
            fig.autofmt_xdate()
            plt.legend(loc='upper left')
            plt.title('Equity Curve')
            plt.show()
            fig.savefig(self._valid_dir + '/performance_' + self._symbol + '.png')
            plt.close()

            average_performance = average_performance.divide(self._n_offsets)
            print(average_performance)
            average_performance.to_csv(self._valid_dir + '/performance_' + self._symbol + '.csv')





