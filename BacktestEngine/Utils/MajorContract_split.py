# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import sys

from Utils.IOUtils import df_reader
from functools import reduce


class MajorContracts():
    ''' Generate the time series of major contracts for given commodity.
    '''

    def __init__(self, symbol='rb', split_time='2016-6-1', topdir=r'../data',
                 maturity={'1605': ['2015-11-1', '2016-3-1'],
                           '1609': ['2016-3-1', '2016-6-1'],
                           '1701': ['2016-7-1', '2016-11-1'],
                           '1705': ['2016-11-1', '2017-3-1']},
                 price='LastPrice',
                 **kwargs):

        self._symbol = symbol
        self._topdir = topdir
        self._split_time = pd.to_datetime(split_time)
        self._offset = kwargs.get('offset', 0.1)
        self._freq = kwargs.get('freq', 15)
        self._price_threshold = kwargs.get('px_th',
                                           0)  # threshold of price movements. Example: 0.01 means that an effective price movement needs 1% difference in price
        # transition time between major contracts. eg, 'transitions' = {'1605': '2016-2-1', ...}
        self._transitions = kwargs.get('transitions', None)

        self._maturity = maturity

        # states = 3. order = 8.
        self._m = 3
        self._n = 8

        self._price = price

    def ternary(self, k, l):
        if k == 0:
            return '0' * l
        nums = []
        while k:
            k, r = divmod(k, self._m)
            nums.append(str(r))
        return ('0' * (l - len(nums))) + ''.join(reversed(nums))

        # create word frequency data frame word counts dictionary

    def word_prob(self, word_counts_dict, l):
        word_counts = pd.DataFrame(list(word_counts_dict.items()), columns=['word', 'freq'])
        word_counts['prior'] = word_counts['word'].str.slice(0, l - 1)
        word_counts['move'] = word_counts['word'].str.slice(l - 1, l)
        word_counts_t = word_counts.pivot(index='prior', columns='move', values='freq')

        # hard coded for self._m=3

        word_counts_t['total'] = word_counts_t['0'] + word_counts_t['1'] + word_counts_t['2']
        word_counts_t['max'] = word_counts_t.loc[:, '0':'2'].idxmax(axis=1)
        word_counts_t['max_pct'] = word_counts_t.loc[:, '0':'2'].max(axis=1) / word_counts_t['total']
        word_counts_t['prior'] = 'p' + word_counts_t.index.map(str)
        return word_counts_t

    def session_break(self, tick_all, start_day, end_day, break_time, split_col='Direction'):
        """
        Insert breaking timepoints in the tick tick_all

        Args:
            start_day: str. yyyy-mm-dd
            break_time: str. hh:mm:ss
        """
        if type(break_time) is str:
            break_time = [break_time]
        break_indicator = []

        for bt in break_time:
            start = pd.to_datetime(start_day) + pd.to_timedelta(bt)
            end = pd.to_datetime(end_day) + pd.to_timedelta(bt)
            break_indicator.append(pd.date_range(start, end, freq='1d'))
        time_index = reduce(lambda x, y: x.append(y), break_indicator)

        for idx in time_index:
            tick_all.loc[idx, split_col] = 9

        tick_all.sort_index(inplace=True)

    def create_major_overlap(self, session_split=None):
        ''' major contracts with overlap time.
        return dataframe for the concated timeseries and probability table for each major contracts in given time period.
        
        Args:
            session_split: lists of split time. example - ['11:40:00', '17:00:00', '03:00:00']

        example: 
            
        rb_mj = MajorContracts(
                               topdir='C:/Qishi_QR/data', split_time = '2016-5-1',
                               maturity={'1609':['2015-11-1','2016-8-1'], '1705':['2016-6-1','2017-3-1']}, 
                               transitions={'1609':'2016-7-1', '1705':'2017-2-1'}
                               ) 
        
        train, test, ptb = rb_mj2.create_major_overlap()
        
        '''

        # if there is no transition provided, return vanilla version.
        if self._transitions == None:
            print('Need transition time!')
            sys.exit()

        majorcontracts = pd.DataFrame()

        first_day = '2016-1-1'
        last_day = '2016-12-31'
        last_transition = '1900-1-1'

        # dictionary for each expiration date
        word_counts_dict = {}

        probability_table = {}

        for exp, trade_range in self._maturity.items():

            # laod data
            instrument = self._symbol + exp
            print(instrument, self._topdir + '/' + self._symbol)

            tick_day = df_reader(instrument + '*', topdir=self._topdir + '/' + self._symbol + '/day',
                                 offset=self._offset, freq=str(self._freq) + 'min', day=True,
                                 symbol=self._symbol).get_tick(raw=False)
            tick_night = df_reader(instrument + '*', topdir=self._topdir + '/' + self._symbol + '/night',
                                   offset=self._offset, freq=str(self._freq) + 'min', day=False,
                                   symbol=self._symbol).get_tick(raw=False)

            tick_all = pd.concat([tick_day, tick_night])
            tick_all.sort_index(inplace=True)

            # create mid price
            tick_all['MidPrice'] = (tick_all['AskPrice1'] + tick_all['BidPrice1']) / 2.0

            if self._price is 'AvePrice2':
                tick_all['AvePrice2'] = (tick_all['AccTurnover']-tick_all['AccTurnover'].shift(1))/(tick_all['AccVolume']-tick_all['AccVolume'].shift(1))

            # create trade direction

                
            if self._price_threshold >= 1:
                tick_all['Direction'] = tick_all[self._price].diff().apply(
                        lambda x: 2 if x > self._price_threshold else (1 if x < -self._price_threshold else 0))
            else:
                tick_all['Direction'] = tick_all[self._price].pct_change().apply(lambda x: 2 if x > self._price_threshold else (1 if x < -self._price_threshold else 0))
            print(self._price_threshold)
            # slice major contracts trading period
            assert pd.to_datetime(self._transitions[exp]) < pd.to_datetime(trade_range[1]) and pd.to_datetime(
                self._transitions[exp]) > pd.to_datetime(trade_range[0])

            start_time = max(pd.to_datetime(first_day), pd.to_datetime(last_transition), pd.to_datetime(trade_range[0]))
            end_time = min(pd.to_datetime(self._transitions[exp]), pd.to_datetime(last_day))

            print('ID', 'trade_range', 'transition_begin', 'transition_end')
            print(exp, trade_range, start_time, end_time)

            tick_all = tick_all[(tick_all.index >= start_time) & (tick_all.index < end_time)]

            majorcontracts = majorcontracts.append(tick_all)

            last_transition = end_time

            ###############################################################
            ### add probability table for training data before split_time

            if start_time >= self._split_time:
                continue

            tick_all = tick_all[(tick_all.index <= self._split_time)]

            ###############################################################
            ### add break points between sessions
            if session_split is not None:
                self.session_break(tick_all, start_time.date(), end_time.date(), session_split)
            print('probability table: ', tick_all.Date.min(), tick_all.Date.max())

            tick_all_sequence = tick_all['Direction'].astype(int).astype(str).str.cat()
            # initialize
            for l in np.arange(1, self._n + 1):
                word_counts_dict[l] = {self.ternary(k, l): 0 for k in np.arange(self._m ** l)}

            # print(tick_all_sequence)
            for l in np.arange(1, self._n + 1):
                for k in np.arange(self._m ** l):
                    word_counts_dict[l][self.ternary(k, l)] += df_reader.count_word(tick_all_sequence,
                                                                                    self.ternary(k, l))

            word_prob_all = pd.DataFrame()
            for l in np.arange(1, self._n + 1):
                tmp = self.word_prob(word_counts_dict[l], l)
                word_prob_all = word_prob_all.append(tmp)

            word_prob_all = word_prob_all[['prior', '0', '1', '2', 'total', 'max', 'max_pct']]
            word_prob_all['offset'] = self._offset

            probability_table[exp] = word_prob_all

            ###############################################################

        train = majorcontracts[majorcontracts.index <= self._split_time]
        test = majorcontracts[majorcontracts.index > self._split_time]

        # note one could merge the probability table for all expiration time.
        return train, test, probability_table
