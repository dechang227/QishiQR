from Utils.IOUtils import *

import matplotlib.pyplot as plt
plt.switch_backend('agg')
import numpy as np
import pandas as pd
import os

from numba import jit

#rpresent number as ternary
def ternary (n, l):
    if n == 0:
        return '0'*l
    nums = []
    while n:
        n, r = divmod(n, 3)
        nums.append(str(r))
    return ('0'*(l-len(nums))) + ''.join(reversed(nums))

# create word frequency data frame from word counts dictionary
def word_prob(word_counts_dict, n):
    word_counts = pd.DataFrame(list(word_counts_dict.items()), columns = ['word', 'freq'])
    word_counts['prior'] = word_counts['word'].str.slice(0, n-1)
    word_counts['move'] = word_counts['word'].str.slice(n-1, n)
    word_counts_t = word_counts.pivot(index='prior', columns='move', values='freq')
    word_counts_t['total'] = word_counts_t['0'] + word_counts_t['1'] + word_counts_t['2']
    word_counts_t['max'] = word_counts_t.loc[:, '0':'2'].idxmax(axis = 1)
    word_counts_t['max_pct'] = word_counts_t.loc[:, '0':'2'].max(axis = 1)/word_counts_t['total']
    word_counts_t['prior'] = 'p'+word_counts_t.index.map(str)
    return word_counts_t

data_root_dir = '/home/rz14/Documents/QR_Qishi/tick2016'
output_path = '/home/rz14/Documents/QR_Qishi/QishiQR/Runmin/Output/'

freq = '5min' #data frequency
n = 8  #degree of model


def freq_generator(commodities=['ag','bu','rb'], timespan=['201601010900','201607010900']):
    for commodity in commodities:
        # dictionary to save word counts for each commodity
        word_counts_dict = {}
        for l in np.arange(1, n):
            word_counts_dict[l] = {ternary(k, l): 0 for k in np.arange(3 ** l)}

        fig, ax = plt.subplots(1, 1, figsize=(20, 15))

        print('='*15 + commodity + '='*15)
        data_path = data_root_dir + '/' + commodity

        for exp_date in sorted(list(set([x[2:6] for x in os.listdir(data_path+'/day')]))):
            print('-'*10 + 'Running:' + exp_date + '-'*10)
            instrument = commodity + exp_date
            tick_day = df_reader(instrument + '*', topdir=data_path + '/day', freq=freq, \
                                day=True, symbol=commodity).get_tick(raw=False)
            tick_night = df_reader(instrument + '*', topdir=data_path + '/night', freq=freq, \
                                day=False, symbol=commodity).get_tick(raw=False)

            tick_all = pd.concat([tick_day, tick_night])
            tick_all.sort_index(inplace=True)
            tick_all = tick_all[pd.to_datetime(timespan[0]):pd.to_datetime(timespan[1])]
            ax.plot(tick_all['LastPrice'], label=exp_date)

            tick_all['Direction'] = tick_all['LastPrice'].pct_change().apply(lambda x: 2 if x > 0 else (1 if x < 0 else 0))
            tick_all_sequence = tick_all['Direction'].astype(str).str.cat()

            for l in np.arange(1, n):
                for k in np.arange(3 ** l):
                    word_counts_dict[l][ternary(k, l)] += df_reader.count_word(tick_all_sequence, ternary(k, l))

        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.xlabel('Time')

        fig.savefig(output_path + '_'.join([commodity, freq]) + '_v2.png')
        # plt.show()

        word_prob_all = pd.DataFrame()
        for l in np.arange(1, n):
            tmp = word_prob(word_counts_dict[l], l)
            word_prob_all = word_prob_all.append(tmp)

        word_prob_all = word_prob_all[['prior', '0', '1', '2', 'total', 'max', 'max_pct']]
        word_prob_all.to_csv(output_path + '_'.join([commodity, freq]) + '_freq.csv', index=False)

if __name__ == "__main__":
    freq_generator()


