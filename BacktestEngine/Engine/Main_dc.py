import os
import json
import pandas as pd
import pickle
import matplotlib.pyplot as plt
from itertools import product
import argparse
import sys
sys.path.append("D:/GitHub/QishiQR/BacktestEngine")

from Utils.MajorContract_split import MajorContracts
#from Utils.MajorContract_Offsets import MajorContracts
from Backtesting.Vectorized.models import MajorSeriesTest
from Backtesting.Vectorized.Strategy import SLM

from local_config_dc import AgConfig, BuConfig, RbConfig, RuConfig, ZnConfig


if __name__ == '__main__':
    __spec__ = "ModuleSpec(name='builtins', loader=<class '_frozen_importlib.BuiltinImporter'>)"

    # ==================================================================== #
    parser = argparse.ArgumentParser(description='Parameter sweep tool')
    parser.add_argument('-o', dest='output_dir', default='Results', help='Folder path to save Backtest model')
    parser.add_argument('-c', dest='configFile', default=None, help='Name of configuration json files')

    args = parser.parse_args()

    # ==================================================================== #
    #                        Set parameters                                #
    output_dir = args.output_dir


    if not args.configFile:
        Parameters = {
            'symbol': ["bu"],

            # Model parameters
            "SignalPrice": ["AvePrice2"],
            "TrainPrice":["AvePrice2"],
            "TestPrice":["MidPrice"],

            "frequency": [5, ],
            "price_threshold": [0, ],
            "threshold": [0,],
            "tca": [-1],
            "fixed_cost": [0.0002],
            "offset":[0.1,],

            "start": ["2016-01-01"],
            "split": ["2016-07-01"],
            "valid_split": ["2016-10-01"],
            "end": ["2016-12-31"]

            ##  Add other parameters below as a dict element. ##

            # The key string should match the members in config.py
            # The values should be lists
        }
    else:
        with open(args.configFile,'r') as f:
            Parameters = json.load(f)

    configDict = {
        'ag': AgConfig,
        'bu': BuConfig,
        'rb': RbConfig,
        'ru': RuConfig,
        'zn': ZnConfig
    }

    try:
        config = configDict[Parameters['symbol'][0]]
    except NotImplementedError:
        print("Configuration not set")



    # # --------------- Helper function used ---------------------------- #

    def SingleRun(params, TesterType='Insample'):
        #  Run 
        major_series = MajorContracts(symbol=params.symbol, split_time=params.split, 
                                    topdir=params.tick_path, maturity=params.maturity, 
                                    transitions=params.transition, price = params.TrainPrice,
                                    freq=params.frequency, offset=params.offset, px_th = params.price_threshold)

        mj_train, mj_test, ptb = major_series.create_major_overlap()
        mj_val = mj_test[mj_test.index <= params.valid_split]
        mj_test = mj_test[mj_test.index > params.valid_split]

        ptb_df = pd.concat(ptb)
        ptb_df.index = ptb_df.index.droplevel(level=0).set_names('RawPrior')
        slm = ptb_df.groupby(['prior']).sum().reset_index()
        slm = SLM(slm, threshold=params.threshold, th_type=params.threshold_type).run()

        tester = {
            "insample": MajorSeriesTest(mj_val, params.output_path, slm, signal_price=params.SignalPrice, test_price=params.TestPrice, px_th = params.price_threshold),
            "outsample": MajorSeriesTest(mj_test, params.output_path, slm, signal_price=params.SignalPrice, test_price=params.TestPrice, px_th = params.price_threshold)
        }

        tester["insample"].build(params.max_model_order, params.frequency, params.start, params.end, params.offset,params.tca, params.fixed_cost)
        tester["insample"].run()
        tester["outsample"].build(params.max_model_order, params.frequency, params.start, params.end, params.offset,params.tca, params.fixed_cost)
        tester["outsample"].run()


        return tester


    # # ------------------------- Main Routine ---------------------------- #
    print("OUTPUTDIR --> {}".format(output_dir))

    try:
        os.mkdir("./{}".format(output_dir))
    except FileExistsError:
        pass

    for idx, paras in enumerate(product(*Parameters.values())):
        current_params = {}
        for key, value in zip(Parameters.keys(), paras):
            current_params[key] = value
        
        params = config(**current_params)
        
        print("\n")
        print(current_params)
        print("="*20)

        singleRunResult = SingleRun(params)
        Results = {
            "insample": singleRunResult["insample"],
            "outsample": singleRunResult["outsample"],
            "globalPara": params,
            "localPara": current_params
        }

        with open(output_dir+"/Result_{}.pkl".format(idx), "wb") as f:
            pickle.dump(Results, f)
            
            

