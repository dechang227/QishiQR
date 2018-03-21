
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class backtester:
    def __init__(self, **kwargs):
        self.label = None
        self.__dict__.update(**kwargs)  # Update parameters from **kwargs

    def run(self):
        time_start = pd.to_datetime('20160101')
        time_end = pd.to_datetime('20160701')
        index = pd.date_range(time_start, time_end, freq="1d")
        PnL = np.exp((0.01 + np.random.normal(0, 0.1, len(index)))
                     *np.linspace(0,1,num=len(index)))
        df = pd.DataFrame(data=PnL.cumprod(), index=index, columns=[self.label])
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
        self.ensembles = None
        self.test_result = None

    def build(self):
        """
        Build the backtester ensemble with different parameters

        Returns:
            a list of backtester ensembles
        """

        # TODO: May change to generator to save memory

        self.ensembles = [backtester(**para) for para in self.para_list]
        return self.ensembles

    def run(self):
        """
        Run all the backtesters in the ensembles. We assume that each tester has method
        tester.run(), and it will return a pd.DataFram that includes the backtesting results

        Returns:
            pd.DataFrame, the backtesting results
        """
        return_pool = [tester.run() for tester in self.ensembles]

        # TODO: To be implemented - Convert return_pool to a single dataframe
        # Need to implement the details

        self.test_result = pd.concat(return_pool, axis=1)
        return self.test_result


    def plot(self, target_col="all", ax=None, **kwargs):
        if ax is None:
            fig = plt.figure()
            ax = plt.gca()

        if target_col is "all":
            self.test_result.plot(ax=ax)
        else:
            try:
                self.test_result[target_col].plot(ax=ax, **kwargs)
            except IndexError:
                print("Cols not found!")

        return ax

# === Debug ======
if __name__ == "__main__":
    myensembler = ensembler(backtester, [{'label':"Return 1"}, {'label': "Return 2"}])
    myensembler.build()
    myensembler.run()
    myensembler.plot()
    plt.show()