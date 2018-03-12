from Utils.IOUtils import *

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

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


data_root_dir = 'D:/Qishi/QuantResearch/Data'
output_path = 'D:/GitHub/QishiQR/Dechang/output/'

freq = '5min' #data frequency
n = 8  #degree of model

for commodity in ['bu']:
    # dictionary to save word counts for each commodity
    word_counts_dict = {}
    for l in np.arange(1, n):
        word_counts_dict[l] = {ternary(k, l): 0 for k in np.arange(3 ** l)}

    fig = plt.figure(figsize=(20, 15))
    ax = plt.subplot(111)

    print('='*15 + commodity + '='*15)
    data_path = data_root_dir + '/' + commodity + '/' + commodity

    #for exp_date in sorted(list(set([x[2:6] for x in os.listdir(data_path+'/day')]))):
    for exp_date in ['1601', '1602']:

        print('-'*10 + 'Running:' + exp_date + '-'*10)
        instrument = commodity + exp_date
        tick_day = df_reader(instrument + '*', topdir=data_path + '/day', freq=freq, \
                             day=True, symbol=commodity).get_tick(raw=False)
        tick_night = df_reader(instrument + '*', topdir=data_path + '/night', freq=freq, \
                               day=False, symbol=commodity).get_tick(raw=False)

        tick_all = pd.concat([tick_day, tick_night])
        tick_all.sort_index(inplace=True)
        ax.plot(tick_all['LastPrice'], label=exp_date)

        tick_all['Direction'] = tick_all['LastPrice'].pct_change().apply(lambda x: 2 if x > 0 else (1 if x < 0 else 0))
        tick_all_sequence = tick_all['Direction'].astype(str).str.cat()
        #print(tick_all_sequence)
        for l in np.arange(1, n):
            # for k in np.arange(3 ** l):
            #     word_counts_dict[l][ternary(k, l)] += tick_all_sequence.count(ternary(k, l))
            for i in np.arange(len(tick_all_sequence)-l+1):
                word_counts_dict[l][tick_all_sequence[i:(i+l)]] += 1

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.xlabel('Time')

    fig.savefig(output_path + '_'.join([commodity, freq]) + '_v2.png')
    plt.show()

    word_prob_all = pd.DataFrame()
    for l in np.arange(1, n):
        tmp = word_prob(word_counts_dict[l], l)
        word_prob_all = word_prob_all.append(tmp)

    word_prob_all = word_prob_all[['prior', '0', '1', '2', 'total', 'max', 'max_pct']]
    word_prob_all.to_csv(output_path + 'test_freq.csv', index=False)
