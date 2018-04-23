import os
import numpy as np
import matplotlib.pyplot as plt

from Utils.IOUtils import *
from Utils.lm import *
from Backtesting.Vectorized.Strategy import MovingAverageStrategy, SLMStrategy
from Backtesting.Vectorized.backtest import vectorizedbacktest
from Backtesting.Vectorized.cross_compare import ensembler


class LmValidation:
    def __init__(self, slm, symbol='ag', data_dir=r'../../Output', valid_dir=r'../../Validation', max_order=8):
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


class OneContractTest:
    """
    Test ONE contract with different orders
    """
    def __init__(self, DATA_DIR, OUTPUT_DIR, prob_table):
        """
        Read in Data and the probability table
        """
        self._DATA_DIR = DATA_DIR
        self._OUTPUT_DIR = OUTPUT_DIR
        self.test_data = None
        self.signals = None
        self.prob_table = prob_table

    def compile_data(self, commodity, exp_date, offset=0, freq='5min', start='20160701', end='20161031'):
        instrument = commodity + exp_date
        tick_day = df_reader(instrument + '*', topdir=self._DATA_DIR + commodity + '/day', offset=offset, freq=freq,day=True, symbol=commodity).get_tick(raw=False)
        tick_night = df_reader(instrument + '*', topdir=self._DATA_DIR + commodity + '/night', offset=offset, freq=freq, day=False, symbol=commodity).get_tick(raw=False)
        
        tick_all = pd.concat([tick_day, tick_night])
        tick_all.sort_index(inplace=True)
        return tick_all[(tick_all.index >= start) & (tick_all.index < end)]

    def compile_signal(self, data, slm, max_order=8):
        """
        Generate signals for different orders
        """
        signals = [SLMStrategy(data, slm, m).generatingsignal() for m in np.arange(1, max_order+1)]
        return signals

    def build(self, commodity, exp_date, model_order=7, freq='5min', offset=0, start='20160701', end='20161031', tca=None):
        self.test_data = self.compile_data(commodity, exp_date,   start = start, end=end)
        self.signals = self.compile_signal(self.test_data, self.prob_table, max_order=model_order)
        self.ensemble = ensembler(vectorizedbacktest, self.signals, tcas=tca)
        self.ensemble.build()

    def run(self):
        self.results = self.ensemble.run()
        self.performance = self.ensemble.calperformance()

    def plot(self, target_col="equitycurve", ax=None):
        return self.ensemble.plot(target_col, ax)

class NoisyOneContractTest(OneContractTest):
    def __init__(self, DATA_DIR, OUTPUT_DIR, prob_table, noise=0.1):
        OneContractTest.__init__(self, DATA_DIR, OUTPUT_DIR, prob_table)
        self.noise = noise

    def compile_data(self, commodity, exp_date, offset=0, freq='5min', start='20160701', end='20161031'):
        instrument = commodity + exp_date
        tick_day = df_reader(instrument + '*', topdir=self._DATA_DIR + commodity + '/day', offset=offset, freq=freq,day=True, symbol=commodity).get_tick(raw=False)
        tick_night = df_reader(instrument + '*', topdir=self._DATA_DIR + commodity + '/night', offset=offset, freq=freq, day=False, symbol=commodity).get_tick(raw=False)
        
        tick_all = pd.concat([tick_day, tick_night])
        tick_all.sort_index(inplace=True)
        tick_all['LastPrice'] = tick_all['LastPrice'].map(lambda x: x*(1+np.random.uniform(-self.noise, self.noise)))
        return tick_all[(tick_all.index >= start) & (tick_all.index < end)]


class MultiContractTest:
    """
    Test Multiple contract with one orders
    """
    def __init__(self, DATA_DIR, OUTPUT_DIR, prob_table):
        """
        Read in Data and the probability table
        """
        self._DATA_DIR = DATA_DIR
        self._OUTPUT_DIR = OUTPUT_DIR
        self.prob_table = prob_table
        self.test_data = None
        self.signals = None
    def compile_data(self, commodity, exp_list, offset=0, freq='5min', start='20160701', end='20161031'):
        all_instruments = [commodity + exp_date for exp_date in exp_list]

        def get_instrument(instrument):
            tick_day = df_reader(instrument + '*', topdir=self._DATA_DIR + commodity + '/day', offset=offset, freq=freq,day=True, symbol=commodity).get_tick(raw=False)
            tick_night = df_reader(instrument + '*', topdir=self._DATA_DIR + commodity + '/night', offset=offset, freq=freq, day=False, symbol=commodity).get_tick(raw=False)
            tick_all = pd.concat([tick_day, tick_night])
            tick_all.sort_index(inplace=True)
            return tick_all[(tick_all.index >= start) & (tick_all.index < end)]
        return [get_instrument(instrument) for instrument in all_instruments]

    def compile_signal(self, data, slm, model_order=4):
        """
        Generate signals for different orders
        """
        signals = [SLMStrategy(instrument, slm, model_order).generatingsignal() for instrument in data]
        return signals

    def build(self, commodity, exp_date, model_order=4, freq='5min', offset=0, start='20160701', end='20161031', tca=None):
        self.test_data = self.compile_data(commodity, exp_date,   start = start, end=end)
        self.signals = self.compile_signal(self.test_data, self.prob_table, model_order)
        self.ensemble = ensembler(vectorizedbacktest, self.signals, tcas=tca, labels=exp_date)
        self.ensemble.build()

    def run(self):
        self.results = self.ensemble.run()
        self.performance = self.ensemble.calperformance()

    def plot(self, target_col="equitycurve", ax=None):
        return self.ensemble.plot(target_col, ax)


class MultiFrequencyTest:
    """
    Test Multiple contract with one orders
    """
    def __init__(self, DATA_DIR, OUTPUT_DIR, prob_table):
        """
        Read in Data and the probability table
        """
        self._DATA_DIR = DATA_DIR
        self._OUTPUT_DIR = OUTPUT_DIR
        self.prob_table = prob_table
        self.test_data = None
        self.signals = None
    def compile_data(self, commodity, exp_list='1705', offset=0, freq=['{}min'.format(i) for i in range(1, 5)], start='20160701', end='20161031'):
        instrument = commodity + exp_list
        def get_instrument(instrument, freq):
            tick_day = df_reader(instrument + '*', topdir=self._DATA_DIR + commodity + '/day', offset=offset, freq=freq,day=True, symbol=commodity).get_tick(raw=False)
            tick_night = df_reader(instrument + '*', topdir=self._DATA_DIR + commodity + '/night', offset=offset, freq=freq, day=False, symbol=commodity).get_tick(raw=False)
            tick_all = pd.concat([tick_day, tick_night])
            tick_all.sort_index(inplace=True)
            return tick_all[(tick_all.index >= start) & (tick_all.index < end)]
        return [get_instrument(instrument, f) for f in freq]

    def compile_signal(self, data, slm, model_order=4):
        """
        Generate signals for different orders
        """
        signals = [SLMStrategy(instrument, slm, model_order).generatingsignal() for instrument in data]
        return signals

    def build(self, commodity, exp_date, model_order=4, freq=['{}min' for i in range(1, 5)], offset=0, start='20160701', end='20161031', tca=None):
        self.test_data = self.compile_data(commodity, exp_date, freq=freq,   start = start, end=end)
        self.signals = self.compile_signal(self.test_data, self.prob_table, model_order)
        self.ensemble = ensembler(vectorizedbacktest, self.signals, tcas=tca, labels=freq)
        self.ensemble.build()

    def run(self):
        self.results = self.ensemble.run()
        self.performance = self.ensemble.calperformance()

    def plot(self, target_col="equitycurve", ax=None):
        return self.ensemble.plot(target_col, ax)