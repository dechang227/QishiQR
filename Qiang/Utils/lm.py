# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 21:08:46 2018

"""

from Utils.IOUtils import *
import calendar
import pandas as pd
import numpy as np
import sys
from datetime import datetime  
from datetime import timedelta 

class LM_model:
    def __init__(self, m=3, n=8, data_root_dir = r'../Data', output = r'../Output'):
        self._m = m # states
        self._n = n # length of words
        self._data_root_dir = data_root_dir
        self._output = output
        self._sel_mode = 'MajorContract'
    
    def ternary (self, k, l):
        if k == 0:
            return '0'*l
        nums = []
        while k:
            k, r = divmod(k, self._m)
            nums.append(str(r))
        return ('0'*(l-len(nums))) + ''.join(reversed(nums))
    
    
    # create word frequency data frame word counts dictionary
    def word_prob(self, word_counts_dict, l):
        word_counts = pd.DataFrame(list(word_counts_dict.items()), columns = ['word', 'freq'])
        word_counts['prior'] = word_counts['word'].str.slice(0, l-1)
        word_counts['move'] = word_counts['word'].str.slice(l-1, l)
        word_counts_t = word_counts.pivot(index='prior', columns='move', values='freq')
        
        # hard coded for self._m=3
        
        word_counts_t['total'] = word_counts_t['0'] + word_counts_t['1'] + word_counts_t['2']
        word_counts_t['max'] = word_counts_t.loc[:, '0':'2'].idxmax(axis = 1)
        word_counts_t['max_pct'] = word_counts_t.loc[:, '0':'2'].max(axis = 1)/word_counts_t['total']
        word_counts_t['prior'] = 'p'+word_counts_t.index.map(str)
        return word_counts_t
    
    
    def LM(self, commodity='rb', exp_list=['1701'], offset=0, freq='5min', flg='train'):
        
        # dictionary to save word counts for each commodity
        word_counts_dict = {}
        for l in np.arange(1, self._n):
            word_counts_dict[l] = {self.ternary(k, l): 0 for k in np.arange(self._m ** l)}


        print('='*12 + commodity + ' '+ flg + '='*12)
        data_path = self._data_root_dir + '/' + commodity

        #for exp_date in sorted(list(set([x[2:6] for x in os.listdir(data_path+'/day')]))):
        tick_maj = pd.DataFrame()
        for exp_date in exp_list:
            tick_tmp = pd.DataFrame()
            print('-'*10 + 'Running:' + exp_date + '-'*10)
            
            instrument = commodity + exp_date
            tick_day = df_reader(instrument + '*', topdir=data_path + '/day', offset=offset, freq=freq,day=True, symbol=commodity).get_tick(raw=False)
            tick_night = df_reader(instrument + '*', topdir=data_path + '/night', offset=offset, freq=freq, day=False, symbol=commodity).get_tick(raw=False)

            tick_all = pd.concat([tick_day, tick_night])
            tick_all.sort_index(inplace=True)

            tick_all.to_csv(self._output + '/' + '_'.join([commodity, exp_date, freq, str(offset)]) + '.csv')
            
            #exp_date_tmp = '20'+exp_date+'15'+' 09:00:00.0'
            year_month = '20'+exp_date
            year_month_int = int(year_month)
            year_int = year_month_int//100
            month_int = year_month_int%100
            month_tot = year_int*12+month_int
            sel_start = '2016-1-1 09:00:00.0'
            sel_end = '2016-1-1 09:00:00.0'
            if(year_month_int>201602):
                month_tot = month_tot-2
                year_int = month_tot//12
                month_int = month_tot%12
                if month_int ==0 :
                    year_int = year_int -1
                    month_int = 12
                _, num_days = calendar.monthrange(year_int, month_int)
                sel_start = str(year_int)+'-'+str(month_int)+'-1 09:00:00.0'
                sel_end   = str(year_int)+'-'+str(month_int)+'-'+str(num_days)+' 23:59:59.0'
                print("select data of "+exp_date+" start from "+sel_start+" to "+sel_end)
                      
                if (self._sel_mode == 'MajorContract'):
                    tick_tmp = tick_all[(tick_all.index < sel_end) & (tick_all.index > sel_start)]
           
            # select train data: hard coded.
           
            if flg=='train':
                tick_all = tick_all[(tick_all.index < '2016-7-1 09:00:00.0')]
            elif flg=='valid':
                tick_all = tick_all[(tick_all.index >= '2016-7-1 09:00:00.0') & (tick_all.index < '2016-10-1 09:00:00.0')]
            else:
                print ('Unknown flg')
                sys.eixt()
            print('total lines: '+str(tick_all.shape[0])+', with '+str(tick_tmp.shape[0])+' lines selected as major contract')    
            tick_maj = tick_maj.append(tick_tmp)
            tick_maj.to_csv(self._output + '/' + '_'.join([commodity, freq, exp_date, str(offset)]) + 'part.csv')

            tick_all['Direction'] = tick_all['LastPrice'].pct_change().apply(lambda x: 2 if x > 0 else (1 if x < 0 else 0))
            tick_all_sequence = tick_all['Direction'].astype(str).str.cat()
            #print(tick_all_sequence)
            for l in np.arange(1, self._n):
                for k in np.arange(self._m ** l):
                     word_counts_dict[l][self.ternary(k, l)] += df_reader.count_word(tick_all_sequence, self.ternary(k, l))
 
        word_prob_all = pd.DataFrame()
        tick_maj.to_csv(self._output + '/' + '_'.join([commodity, freq, str(offset)]) + 'all.csv')
        for l in np.arange(1, self._n):
            tmp = self.word_prob(word_counts_dict[l], l)
            word_prob_all = word_prob_all.append(tmp)

        word_prob_all = word_prob_all[['prior', '0', '1', '2', 'total', 'max', 'max_pct']]
        word_prob_all['offset'] = offset
#        print (word_prob_all)
        
        return word_prob_all
    
    def LM_set(self, commodity='rb', exp_list=['1701'], flg='train', freq=5, interval=0.5):
        ''' 
        freq and interval (of offset) in minutes.
        '''
        prob_all = pd.DataFrame()
               
        for offset in np.arange(0, freq, interval):
            print(str(offset)+'min')
            tmp = self.LM(commodity=commodity, exp_list=exp_list, offset = float(offset), freq=str(freq)+'min', flg=flg)
            
            prob_all = prob_all.append(tmp)
        
        return prob_all
    
        #prob_all.to_csv('LM_'+freq+'min'+commodity+'_'+flg+'.csv')

    def t_tests(self, df_train, df_valid, num):
        
        from scipy import stats
        
        total_lm = pd.merge(df_train, df_valid, left_on=['prior', 'offset'], \
                            right_on=['prior', 'offset'],  suffixes=('_train','_valid'))
        

        total_lm['max_train']=total_lm['max_train'].astype(int)
        total_lm['max_valid']=total_lm['max_valid'].astype(int)

        # mean         
        lm_mean = total_lm.groupby(['prior'])['max_train', 'max_valid'].mean()        
        lm_mean.rename(columns={'max_train':'max_train_mean', 'max_valid':'max_valid_mean'}, inplace=True)
        
        # std
        lm_std = total_lm.groupby(['prior'])['max_train', 'max_valid'].std()
        lm_std.rename(columns={'max_train':'max_train_std', 'max_valid':'max_valid_std'}, inplace=True)

        lm_stats = lm_mean.join(lm_std)        
                
        
        # 1. t-score in training set
        lm_stats['max_train'] = np.round(lm_stats['max_train_mean'])
        lm_stats['t_score_train'] = (lm_stats['max_train_mean'] - lm_stats['max_train'])*np.sqrt(num)/lm_stats['max_train_std']
        
        # 2. Welch t-test between train and valid sets.
        lm_stats['dof'] = (lm_stats['max_train_std']**2/num+lm_stats['max_valid_std']**2/num)**2/ \
                    ((lm_stats['max_train_std']**2/num)**2/(num-1)+(lm_stats['max_valid_std']**2/num)**2/(num-1))
                    
        lm_stats['t_score'] = (lm_stats['max_train_mean']-lm_stats['max_valid_mean'])/np.sqrt(lm_stats['max_train_std']**2/num \
                    + lm_stats['max_valid_std']**2/num)
        
        # nan p-value indicates zero std, = zero t-score
        lm_stats.fillna(value=0, inplace=True)
        
        # extract two-sided t-test p-value
        lm_stats['pvalue_train'] = stats.t.sf(lm_stats['t_score_train'], num-1)*2

        lm_stats['pvalue_cx'] = stats.t.sf(lm_stats['t_score'], np.round(lm_stats['dof']))*2
        
        return lm_stats
    
    def run(self, commodity='rb', exp_list=['1701'], freq=5, interval=0.5):
        
        df_train= self.LM_set(commodity=commodity, exp_list=exp_list, flg='train', freq=freq, interval=interval)
        df_valid= self.LM_set(commodity=commodity, exp_list=exp_list, flg='valid', freq=freq, interval=interval)
        
        num = round(freq/interval)
        
        return self.t_tests(df_train, df_valid, num)
