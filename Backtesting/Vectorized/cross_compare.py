import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .backend import vectorized_backtest

class ensembler:
    def __init__(self, tester, signals, tcas=None, labels=None):
        """
        Create an ensembler that includes backtester ensemble with different parameters

        Args:
            backtester: the back tester
            para_list: iterable that includes dicts of parameters.
                       Example: [{'file':'Ag_20160101', 'Language_Order': 2},
                                 {'file':'Ag_20160102', 'Language_Order': 3}]
        """
        self.backtester = tester
        self.signals = signals
        self.tcas = tcas
        try:
            assert len(labels) == len(self.signals), 'Labels does not match signal'
            self.labels = labels
        except:
            self.labels = list(range(1, len(signals)+1))
            
        self.ensembles = None
        self.results = None

    def build(self):
        """
        Build the backtester ensemble with different parameters

        Returns:
            a list of backtester ensembles
        """

        # TODO: May change to generator to save memory
        if self.tcas is not None:
            self.ensembles = [vectorized_backtest(signal, tca) for signal, tca in zip(self.signals, self.tcas)]
        else:
            self.ensembles = [vectorized_backtest(signal) for signal in self.signals]

        return self.ensembles

    def run(self):
        """
        Run all the backtesters in the ensembles. We assume that each tester has method
        tester.run(), and it will return a pd.DataFram that includes the backtesting results

        Returns:
            pd.DataFrame, the backtesting results
        """
        self.results = [tester.runtest() for tester in self.ensembles]
        return self.results

    def cal_performance(self):
        [tester.cal_performance() for tester in self.ensembles]
        try:
            self.performance = pd.DataFrame([tester.performance for tester in self.ensembles], index=self.labels)
            self.performance.index.name = 'Model Order'
        except:
            print('Failed to build the performance DataFrame')

    def plot(self, target_col="equitycurve", ax=None, **kwargs):
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