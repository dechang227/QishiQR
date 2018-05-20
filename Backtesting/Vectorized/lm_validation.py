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
    def __init__(self, slm, start='2016-7-1', end='2016-10-1',symbol='ag', data_dir=r'../../Output', valid_dir=r'../../Validation', max_order=8, offsets_average = False, n_offsets = 5, **kwargs):
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
        self._max_order = max_order
        self._offsets_average = offsets_average
        self._average_return = None
        self._n_offsets = n_offsets
        self._start = start
        self._end = end
        self._price_threshold = kwargs.get('px_th', 0)

    def gen_find(self):
        '''
        Find all filenames in a directory tree that match a shell wildcard pattern.
        '''
        for path, dirlist, filelist in os.walk(self._data_dir):
            for name in fnmatch.filter(filelist, self._symbol + '*'):
                yield name

    def run(self, tcas=None):
        filenames = self.gen_find()
        for filename in filenames:
            print(filename)
            data = pd.read_csv(self._data_dir + '/' + filename, index_col=0)
            data = data[(pd.to_datetime(data.index) >= pd.to_datetime(self._start)) & (pd.to_datetime(data.index) < pd.to_datetime(self._end))]
            if len(data) == 0:
                continue
            else:
                signals = [SLMStrategy(data, self._slm, m, px_th=self._price_threshold).generatingsignal() for m in np.arange(1, self._max_order + 1)]
                validator_ensemble = ensembler(vectorizedbacktest, signals, tcas=tcas)
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
                        self._average_return = [df['strategy'] for df in validator_ensemble.results]
                        average_performance = performance
                        average_benchmark = validator_ensemble.results[0]['LastPrice']
                    else:
                        self._average_return = [df1.add(df2['strategy'], fill_value=0) for (df1, df2) in zip(self._average_return, validator_ensemble.results)]
                        average_performance = average_performance.add(performance, fill_value=0)
                        average_benchmark = average_benchmark.add(validator_ensemble.results[0]['LastPrice'], fill_value=0)
        '''
        average return of all offsets
        '''
        if self._offsets_average and (self._average_return is not None):
            self._average_return = [(1+df.divide(self._n_offsets)).cumprod() for df in self._average_return]
            average_benchmark = average_benchmark/average_benchmark[0]
            average_benchmark = average_benchmark.to_frame()
            average_benchmark['Date'] = pd.to_datetime(average_benchmark.index)
            #print(average_benchmark)
            fig = plt.figure()
            plt.plot(average_benchmark.Date, average_benchmark.LastPrice,label='benchmark')
            for avg_return, label in zip(self._average_return, np.arange(2, 2+len(self._average_return))):
                #avg_return.plot(label=label)
                df = avg_return.to_frame()
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





