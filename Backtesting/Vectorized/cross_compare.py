import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .backtest import vectorizedbacktest

class ensembler:
    def __init__(self, tester, signals, tcas=None, labels=None):
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
            self.ensembles = [vectorizedbacktest(signal, tca) for signal, tca in zip(self.signals, self.tcas)]
        else:
            self.ensembles = [vectorizedbacktest(signal) for signal in self.signals]

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
            self.performance = pd.DataFrame([tester.performance for tester in self.ensembles], index=self.labels)
            self.performance.index.name = 'Model Order'
        except:
            print('Failed to build the performance DataFrame')

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