
import matplotlib.pyplot as plt
import numpy as np
import datetime
import pandas as pd


class backtester:
    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)
        pass
    @staticmethod
    def run(**kwargs):
        time_start = pd.to_datetime('20160101')
        time_end = pd.to_datetime('20160701')
        index = pd.date_range(time_start, time_end, freq="1d")
        PnL = np.random.randn(len(index))
        df = pd.DataFrame(data=PnL, index=index, columns=['Return'])
        return df



class ensembler:
    def __init__(self, backtester: backtester, para_list):
        """
        Create an ensembler that includes backtester ensemble with different parameters

        Args:
            backtester: the back tester
            para_list: iterable that includes dicts of parameters.
                       Example: [{'file':'Ag_20160101', 'Language_Order': 2},
                                 {'file':'Ag_20160102', 'Language_Order': 3}]
        """
        self.backtester = backtester
        self.para_list = para_list

    def build(self):
        """
        Build the backtester ensemble

        Returns:
            backtester ensembles
        """

        # TODO: May change to generator to save memory
        self.ensembles = [backtester(**para) for para in self.para_list]
        return self.ensembles

    def run(self):
        """
        Run all the backtesters in the ensembles

        Returns:

        """
        myreturn =  myfunc(**kwargs)
        return myreturn.head(1)

    def plot_return(self):
        pass

myensembler = ensembler(backtester, [{'key1':1}])
