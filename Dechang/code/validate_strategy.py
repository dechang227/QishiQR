# import importlib
# importlib.reload(some_module)

import pandas as pd
from Backtesting.Vectorized.lm_validation import LmValidation

ag_strategy = pd.read_csv(r'../../Strategy/ag_5min_strategy.csv')
slm = ag_strategy[['prior', '0', '1', '2', 'total']].groupby(['prior']).sum().reset_index()
slm['signal'] = slm.loc[:, '0':'2'].idxmax(axis=1)

lm_validation = LmValidation(slm, symbol='ag*', data_dir=r'../../Output', valid_dir=r'../../Validation', max_order=8)
lm_validation.run()