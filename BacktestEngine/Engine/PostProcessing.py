import sys
sys.path.append("/home/runmin/Documents/Qishi/QishiQR/BacktestEngine")

from glob import glob
import pickle
import matplotlib.pyplot as plt
import Backtesting
import pandas as pd
import re

def GetResult(RESULT_DIR):
    files = sorted(glob(RESULT_DIR+"/*.pkl"), key=lambda x: int(re.findall('Result_(\d+)',x)[0]))

    Tester_Results = []
    file_path = []
    for idx, file in enumerate(files):
        with  open(file,"rb") as f:
            Tester_Results.append(pickle.load(f))
        print("\n================================================================")
        print("Tester=",idx, "|file_path = ", file)
    return Tester_Results




class OffSetAverage:
    """
    ONLY work on Offset Average
    """
    def __init__(self, Tester_Results):
        self.Tester_Results = Tester_Results
        self.AveEquityCurve = {'insample':None, 'outsample':None}
        self.Benchmark = {'insample':None, 'outsample':None}
        self.AvePerformance = {'insample':0, 'outsample':0}

    def GetBenchmark(self):
        self.Benchmark['insample'] = self.Tester_Results[0]["insample"].ensemble.ensembles[0].result.benchmark
        self.Benchmark['outsample'] = self.Tester_Results[0]["outsample"].ensemble.ensembles[0].result.benchmark
        return self.Benchmark
    
    def GetAveEquityCurve(self):
        totalNum_of_Offset =len(self.Tester_Results)

        for DataType in ['insample', 'outsample']:
            StrategyReturn = pd.DataFrame()
            for single_offset_data in self.Tester_Results:
                for model_order, data in enumerate(single_offset_data[DataType].ensemble.ensembles, start=2):
                    try:
                        StrategyReturn[model_order] = StrategyReturn[model_order].add(data.result.strategy.reset_index(drop=True)/totalNum_of_Offset, fill_value=0)
                    except KeyError:
                        TimeIndex = data.result.index
                        StrategyReturn[model_order] = data.result.strategy.values/totalNum_of_Offset

            StrategyReturn.index = TimeIndex
            StrategyReturn.index.name='Date'
            
            self.AveEquityCurve[DataType] = (StrategyReturn+1).cumprod()
        return self.AveEquityCurve

    def GetAvePerformance(self):
        totalNum_of_Offset =len(self.Tester_Results)
        for DataType in ['insample', 'outsample']:
            tmp_Performance = 0
            for idx,single_offset_data in enumerate(self.Tester_Results):
                tmp_Performance += single_offset_data[DataType].performance
            self.AvePerformance[DataType] = tmp_Performance/ totalNum_of_Offset
        return self.AvePerformance
