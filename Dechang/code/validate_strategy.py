# import importlib
# importlib.reload(some_module)

import pandas as pd
from Backtesting.Vectorized.lm_validation import LmValidation

ag_strategy = pd.read_csv(r'../../Strategy/ag_5min_strategy.csv')
slm = ag_strategy[['prior', '0', '1', '2', 'total']].groupby(['prior']).sum().reset_index()
slm['signal'] = slm.loc[:, '0':'2'].idxmax(axis=1)
'''
ag_contracts = ['1601', '1602', '1603', '1604', '1605', '1606', '1607', '1608', '1609', '1610', '1611', '1612', '1701',
                '1702', '1703', '1704', '1705', '1706', '1707', '1708', '1709', '1710', '1711', '1712']
'''
ag_contracts = ['1612', '1701']
for contract in ag_contracts:
    lm_validation = LmValidation(slm, symbol='ag_'+contract, data_dir=r'../../Output', valid_dir=r'../../CodeTest', max_order=8, offsets_average = True, n_offsets = 5)
    lm_validation.run()