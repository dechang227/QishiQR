import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import importlib
import Backtesting.Vectorized.backtest
importlib.reload(Backtesting.Vectorized.backtest)

from Utils.IOUtils import *
from Utils.lm import *
from Backtesting.Vectorized.Strategy import MovingAverageStrategy, SLMStrategy
from Backtesting.Vectorized.backtest import vectorizedbacktest

class ensembler:
    def __init__(self, tester, signals, tcas=None, labels=None, window = 32, hcl_th = 0.55):
        """
        Create an ensembler that includes backtester ensemble with different parameters

        Args:
            backtester: the back tester
            signasl: Signals to used in the backtester.
        """
        self.backtester = tester
        self.signals = signals
        self.tcas = tcas
        try:
            assert len(labels) == len(self.signals), 'Labels does not match signal'
            self.labels = labels
        except TypeError:
            self.labels = list(range(2, len(signals)+2))

        self.ensembles = None
        self.results = None
        self._window = window
        self._hcl_th = hcl_th 

    def build(self):
        """
        Build the backtester ensemble with different parameters

        Returns:
            a list of backtester ensembles
        """

        # TODO: May change to generator to save memory
        if self.tcas is not None:
            self.ensembles = [vectorizedbacktest(signal, window = self._window, pct_th =self._hcl_th, tca = tca) for signal, tca in zip(self.signals, self.tcas)]
        else:
            self.ensembles = [vectorizedbacktest(signal, self._window, pct_th =self._hcl_th) for signal in self.signals]

        return self.ensembles

    def run(self):
        """
        Run all the backtesters in the ensembles. 

        Returns:
            lists of the backtesting results with different signals
        """
        self.results = [tester.runtest() for tester in self.ensembles]
        return self.results

    def calperformance(self):
        """
        Analyze the performance
        """
        [tester.calperformance() for tester in self.ensembles]
        try:
            self.performance = pd.DataFrame([tester.performance for tester in self.ensembles])
            # if not self.labels:
            #     self.performance.index = labels
        except:
            print('Failed to build the performance DataFrame')
        return self.performance

    def plot(self, target_col="equitycurve", ax=None):
        """
        Make plots

        Args:
            target_col: str. The name of values to be plotted.
            ax: matplotlib.axes. Axes of the target plot.
        Return:
            ax: return the figure axes.
        """
        if ax is None:
            fig = plt.figure()
            ax = plt.gca()
        try:
            for result, label in zip(self.results, self.labels):
                result[target_col].plot(ax=ax, label=label)
        except IndexError:
            print("Cols not found!")

        ax.legend()
        ax.set_title(target_col)
        return ax


def compile_signal(data, slm, max_order=8):
    slm = slm[['prior', 'max']]
    slm = slm.rename(columns={'max': 'signal'})
    signals = [SLMStrategy(data, slm, m).generatingsignal() for m in np.arange(1, max_order+1)]
    return signals


class tester:
    def __init__(self, DATA_DIR, OUTPUT_DIR, prob_table):
        self._DATA_DIR = DATA_DIR
        self._OUTPUT_DIR = OUTPUT_DIR
        self.prob_table = prob_table

    def build(self, commodity, exp_date, model_order=7, freq='5min', offset=0, start='20160701', end='20161031', tca=None):
        self.config = {
            'commodity': commodity,
            'exp_date': exp_date,
            'model_order': model_order,
            'freq:': freq,
            'offset': offset,
            'start_day': start,
            'end_day': end,
            'tca': tca
        }

        self.test_data = vectorizedbacktest.compile_data(self._DATA_DIR, commodity, exp_date,   start = start, end=end)
        signals = compile_signal(self.test_data, self.prob_table, max_order=model_order)
        self.ensemble = ensembler(vectorizedbacktest, signals, tcas=tca)
        self.ensemble.build()

    def run(self):
        self.results = self.ensemble.run()
        self.performance = self.ensemble.calperformance()

    def plot(self, target_col="equitycurve", ax=None):
        return self.ensemble.plot(target_col, ax)