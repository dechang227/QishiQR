import os

from Utils.lm import *

# train model and generate new with varying frequencies
lm_model = LM_model(m=3, n=11, data_root_dir=r'../../Data', output=r'../../Output')
# t = ['1601', '1602'] # for testing
# ag_strategy_1701 = lm_model.LM_set(commodity='ag', exp_list=t, flg='train', freq=5, interval=1)

#sorted(list(set([x[2:6] for x in os.listdir(r'Data/ag/day')]))) # extract all contracts
ag_contracts = ['1601', '1602', '1603', '1604', '1605', '1606', '1607', '1608', '1609', '1610', '1611', '1612', '1701',
                '1702', '1703', '1704', '1705', '1706', '1707', '1708', '1709', '1710', '1711', '1712']
ag_strategy = lm_model.LM_set(commodity='ag', exp_list=ag_contracts, flg='train', freq=5, interval=1)
ag_strategy.to_csv(r'../../Strategy/ag_5min_strategy.csv', index=False)
