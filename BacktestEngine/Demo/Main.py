import os
import json
import pandas as pd
import pickle
import matplotlib.pyplot as plt
import sys
sys.path.append("/home/runmin/Documents/Qishi/QishiQR/BacktestEngine")

from Utils.MajorContract_split import MajorContracts
from Backtesting.Vectorized.models import MajorSeriesTest
from Backtesting.Vectorized.Strategy import SLM

from local_config import BuConfig, RbConfig

from itertools import product


def SingleRun(params):
    #  Run 

    major_series = MajorContracts(symbol=params.symbol, split_time=params.split, 
                                topdir=params.tick_path, maturity=params.maturity, 
                                transitions=params.transition, price = params.TrainPrice,
                                freq=params.frequency, offset=params.offset)
    mj_train, mj_test, ptb = major_series.create_major_overlap()


    ptb_df = pd.concat(ptb)
    ptb_df.index = ptb_df.index.droplevel(level=0).set_names('RawPrior')
    slm = ptb_df.groupby(['prior']).sum().reset_index()
    slm = SLM(slm, threshold=params.threshold, th_type=params.threshold_type).run()

    tester = MajorSeriesTest(mj_test, params.output_path, slm, price=params.SignalPrice)
    tester.build( params.max_model_order, params.offset, params.start.strftime("%Y%m%d"), params.end.strftime("%Y%m%d"), params.tca)

    tester.run()

    return tester
    
# --------------------------------------------------------------- #

Parameters = {

    # Model parameters
    "SignalPrice": ["MidPrice"],
    "TrainPrice":["AvePrice2"],
    
    "frequency": [5, ],
    "threshold": [0,],
    "tca": [-1],
    "offset":[0.1,1.1,2.1,3.1,4.1]
#     "frequency": [5,],
#     "threshold": [0,],
#     "tca": [-1]



    ##  Add other parameters below as a dict element. ##

    # The key string should match the members in config.py
    # The values should be lists

}

try:
    os.mkdir("./Results")
except FileExistsError:
    pass


for idx, paras in enumerate(product(*Parameters.values())):
    current_params = {}
    for key, value in zip(Parameters.keys(), paras):
        current_params[key] = value

    params = BuConfig(**current_params)
    
    print("\n")
    print(current_params)
    print("="*20)

    Results = {
        "model": SingleRun(params),
        "globalPara": params,
        "localPara": current_params
    }


    with open("./Results/Result_{}.pkl".format(idx), "wb") as f:
        pickle.dump(Results, f)
