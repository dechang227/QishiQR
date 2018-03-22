To use lm.py:

from lm import *

model1 = LM_model(m=3, n=4) # where states # = m and maximum length = n

# given commodity, expiration list, freq (minutes), and interval for incremental offset, 
# for example here the starting time is 0, 0.5, ...., 4.5 minutes.

lm1 = model1.run(commodity='rb', exp_list=['1701'], freq=5, interval=0.5)


