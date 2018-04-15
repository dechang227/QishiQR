import numpy as np
import matplotlib.pyplot as plt

from Utils.IOUtils import *
import os
from Backtesting.Vectorized.Strategy import SLMStrategy
from Backtesting.Vectorized.backtest import vectorizedbacktest
from Backtesting.Vectorized.cross_compare import ensembler


class LmValidation:
    def __init__(self, slm, symbol='ag', data_dir=r'../../Output', valid_dir=r'../../Validation', max_order=8, offsets_average = False, n_offsets = 5):
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
            data = pd.read_csv(self._data_dir + '/' + filename, index_col=0)
            data = data[(pd.to_datetime(data.index) >= '2016-7-1 09:00:00.0') & (pd.to_datetime(data.index) < '2016-10-1 09:00:00.0')]
            if len(data) == 0:
                continue
            else:
                signals = [SLMStrategy(data, self._slm, m).generatingsignal() for m in np.arange(1, self._max_order + 1)]
                validator_ensemble = ensembler(vectorizedbacktest, signals)
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
                        average_performace = performance
                    else:
                        self._average_return = [df1.add(df2['strategy'], fill_value=0) for (df1, df2) in zip(self._average_return, validator_ensemble.results)]
                        average_performace = average_performace.add(performance, fill_value=0)
        '''
        average return of all offsets
        '''
        if self._offsets_average:
            self._average_return = [(1+df.divide(self._n_offsets)).cumprod() for df in self._average_return]

            fig = plt.figure()
            for avg_return, label in zip(self._average_return, np.arange(2, 2+len(self._average_return))):
                avg_return.plot(label=label)
            plt.legend(loc='upper left')
            fig.savefig(self._valid_dir + '/performance_' + self._symbol + '.png')
            plt.close()

            average_performace = average_performace.divide(self._n_offsets)
            average_performace.to_csv(self._valid_dir + '/performance_' + self._symbol + '.csv')





