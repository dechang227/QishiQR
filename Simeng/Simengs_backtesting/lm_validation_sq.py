import numpy as np
import matplotlib.pyplot as plt
import os

#from Utils.IOUtils import *
#from Backtesting.Vectorized.Strategy import SLMStrategy
#from Backtesting.Vectorized.backtest import vectorizedbacktest
#from Backtesting.Vectorized.cross_compare import ensembler

from Simengs_utils.IOUtils_sq import *
from Simengs_backtesting.Strategy_sq import SLMStrategy
from Simengs_backtesting.backtest_sq import vectorizedbacktest
from Simengs_backtesting.cross_compare_sq import ensembler




class LmValidation:
    def __init__(self, slm, start='2016-7-1', end='2016-10-1',symbol='ag', data_dir=r'../../Output', valid_dir=r'../../Validation', max_order=8, offsets_average=False, n_offsets=5):
        '''
        :param slm: language model dataframe having at least two columns: prior and signal
        :param symbol:
        :param data_dir: directory of testing files
        :param max_order: max order of model to test
        :param start,end: the starting and ending time stamp, defines the testing time interval ##SQ
        :param offsets_average: average all offset testing results
        :param n_offsets: number of total offsets. Used to get offset average
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
    
    def gen_find(self):
        '''
        Find all filenames in a directory tree that match a shell wildcard pattern.
        '''
        for path, dirlist, filelist in os.walk(self._data_dir):
            for name in fnmatch.filter(filelist, self._symbol + '*'):
                yield name
                print(name)

    def run(self, tcas=None):
        filenames = self.gen_find()
        for filename in filenames:  ##SQ offsets
            data = pd.read_csv(self._data_dir + '/' + filename, index_col=0)
            data = data[(pd.to_datetime(data.index) >= pd.to_datetime(self._start)) & (pd.to_datetime(data.index) < pd.to_datetime(self._end))]
            if len(data) == 0:
                continue
            else:
                
                ##SQ: add start trade and end trade flag
                data['TimeStamp']=pd.to_datetime(data.index)
                data['tm2preTrade'] = (data['TimeStamp']-data['TimeStamp'].shift(1))/ np.timedelta64(1, 'm')
                data['flag_start_trade'] = 0
                data.loc[(data.tm2preTrade > 300) | data.tm2preTrade.isnull(),'flag_start_trade'] = 1

                data['tm2nextTrade'] = (data['TimeStamp'].shift(-1)-data['TimeStamp'])/ np.timedelta64(1, 'm')
                data['flag_end_trade'] = 0
                data.loc[(data.tm2nextTrade > 300) | data.tm2nextTrade.isnull(),'flag_end_trade'] = 1
                data.drop(['tm2nextTrade', 'tm2preTrade'], axis=1, inplace=True)


                signals = [SLMStrategy(data, self._slm, m).generatingsignal() for m in np.arange(1, self._max_order + 1)]
                ##SQ: signals is a list, each element is a data.frame of signals with model of order m
                validator_ensemble = ensembler(vectorizedbacktest, signals, tcas=tcas)
                validator_ensemble.build()
                validator_ensemble.run()
                ##SQ: generate validator_ensemble.results, a list, each component corresponding to each signal component (order of LM)

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
                
                
                ##SQ: combining 'strategy', 'performance', 'bentchmark' from each offsets
                if self._offsets_average:
                    if not self._average_return:
                        self._average_return = [df['strategy'] for df in validator_ensemble.results]
                        average_performance = performance
                        # average_benchmark = validator_ensemble.results[0]['LastPrice']
                        ## SQ change to 'return' to keep consistency
                        average_benchmark = validator_ensemble.results[0]['return']

                    else:
                        self._average_return = [df1.add(df2['strategy'], fill_value=0) for (df1, df2) in zip(self._average_return, validator_ensemble.results)]
                        average_performance = average_performance.add(performance, fill_value=0)
                        
                        ## average_benchmark = average_benchmark.add(validator_ensemble.results[0]['LastPrice'], fill_value=0)
                        ## SQ change to 'return' to keep consistency
                        average_benchmark = average_benchmark.add(validator_ensemble.results[0]['return'], fill_value=0)
    
                ##SQ till now
                ##  self.average_return is a list, each element is a df corresponding to an order
                ##  the order within each df is grouped by offset
                ##  average_benchmark is also grouped by offset, needed to sort by index
#            return [average_benchmark,average_performance]

        '''
            average return of all offsets
            '''
        if self._offsets_average and (self._average_return is not None):
            average_benchmark = average_benchmark[average_benchmark.index!=0].to_frame()
            average_benchmark['Date'] = pd.to_datetime(average_benchmark.index)
            average_benchmark.sort_values(['Date'],inplace=True)
            ## average_benchmark['return'] = 1 + np.log(average_benchmark['LastPrice']/average_benchmark['LastPrice'].iloc[0])
            ## SQ change to 'return' to keep consistency
            average_benchmark['return'] = 1+average_benchmark['return'].divide(5, fill_value=0).cumsum()

            fig = plt.figure()
            plt.plot(average_benchmark['Date'], average_benchmark['return'],label='benchmark')
            for avg_return, label in zip(self._average_return, np.arange(2, 2+len(self._average_return))):
                avg_return = avg_return[avg_return.index!=0]
                avg_return = avg_return.to_frame()
                avg_return['Date'] = pd.to_datetime(avg_return.index)
                avg_return.sort_values(['Date'],inplace=True)
                avg_return['av_return'] = 1+avg_return['strategy'].divide(5, fill_value=0).cumsum()

                plt.plot(avg_return.Date, avg_return.av_return, label=label)
            fig.autofmt_xdate()
            plt.legend(loc='upper left')
            plt.title('Average Equity Curve Over All Offsets')
            plt.show()
            fig.savefig(self._valid_dir + '/performance_' + self._symbol + '.png')
            plt.close()

            average_performance = average_performance.divide(self._n_offsets)
            print(average_performance)
            average_performance.to_csv(self._valid_dir + '/performance_' + self._symbol + '.csv')


#        if self._offsets_average and (self._average_return is not None):
#            self._average_return = [(1+df.divide(self._n_offsets)).cumprod() for df in self._average_return]
#            average_benchmark = average_benchmark/average_benchmark[0]
#            average_benchmark = average_benchmark.to_frame()
#            average_benchmark['Date'] = pd.to_datetime(average_benchmark.index)
#            #print(average_benchmark)
#            fig = plt.figure()
#            plt.plot(average_benchmark.Date, average_benchmark.LastPrice,label='benchmark')
#            for avg_return, label in zip(self._average_return, np.arange(2, 2+len(self._average_return))):
#                #avg_return.plot(label=label)
#                avg_return = avg_return[avg_return.index!=0]
#                df = avg_return.to_frame()
#                df['Date'] = pd.to_datetime(df.index)
#                plt.plot(df.Date, df.strategy, label=label)
#            fig.autofmt_xdate()
#            plt.legend(loc='upper left')
#            plt.title('Equity Curve')
#            plt.show()
#            fig.savefig(self._valid_dir + '/performance_' + self._symbol + '.png')
#            plt.close()
#
#            average_performance = average_performance.divide(self._n_offsets)
#            print(average_performance)
#            average_performance.to_csv(self._valid_dir + '/performance_' + self._symbol + '.csv')







