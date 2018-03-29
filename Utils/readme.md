## To use lm.py:

`from lm import *`

`model1 = LM_model(m=3, n=4) # where states # = m and maximum length = n`

`lm1 = model1.run(commodity='rb', exp_list=['1701'], freq=5, interval=0.5)`

given commodity, expiration list, freq (minutes), and interval for incremental offset, 
for example here the starting time is 0, 0.5, ...., 4.5 minutes after trade start.

### 1. Hard code: training period is before 2016-7-1, and validation period is 2016 3rd quarter. 

### 2. states # m =3 is fixed.

### 3. The t-test is performed on the 'max' = most probable subsequent state for training set, and between training set and validation set. It might also be useful to look at 'max_pct' = likelihood of most probable state when 'max' state is the same in training and validation sets.


### 4. columns in lm1: move (prior),	max_train_mean,	max_valid_mean,	max_train_std,	max_valid_std,	max_train,	t_score_train,	pvalue_train,	dof (degree of freedom in test for training and validation sets),	t_score,	pvalue_cx

