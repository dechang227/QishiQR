# -*- coding: utf-8 -*-
"""
Created on Sat Apr  7 20:04:48 2018

@author: Gang Shen
"""

import pandas as pd

from IOUtils import df_reader

class MajorContracts():
    ''' Generate the time series of major contracts for given commodity.
    '''
    
    def __init__(self, symbol='rb', topdir=r'../data', maturity={'1605':['2015-11-1','2016-3-1'],
                                              '1609':['2016-3-1','2016-6-1'],
                                              '1701':['2016-7-1','2016-11-1'],
                                              '1705':['2016-11-1','2017-3-1']},
                        **kwargs):
        
        self._symbol  = symbol
        self._topdir  = topdir
        self._offset  = kwargs.get('offset', 0.1)
        self._freq    = kwargs.get('freq', 15)       
        
        # transition time between major contracts. eg, 'transitions' = {'1605': '2016-2-1', ...}
        self._transitions  = kwargs.get('transitions', None)  
    
        
        self._maturity = maturity
        
    def create_major(self):
        ''' major contracts without overlap time.'''
        
        majorcontracts = pd.DataFrame()
        for exp, trade_range in self._maturity.items():
            
            instrument = self._symbol + exp
            print (instrument, self._topdir + '/'+self._symbol+ '/day')
            
            tick_day = df_reader(instrument + '*', topdir=self._topdir + '/'+self._symbol+ '/day', offset=self._offset, freq=str(self._freq)+'min',day=True, symbol=self._symbol).get_tick(raw=False)
            tick_night = df_reader(instrument + '*', topdir=self._topdir + '/'+self._symbol+ '/night', offset=self._offset, freq=str(self._freq)+'min', day=False, symbol=self._symbol).get_tick(raw=False)

            tick_all = pd.concat([tick_day, tick_night])
            tick_all.sort_index(inplace=True)
            
            tick_all = tick_all[(tick_all.index >= trade_range[0]) & (tick_all.index < trade_range[1])]

            tick_all['Direction'] = tick_all['LastPrice'].pct_change().apply(lambda x: 2 if x > 0 else (1 if x < 0 else 0))
            
            majorcontracts = majorcontracts.append(tick_all)
            
        return majorcontracts.sort_index()
    
    def create_major_overlap(self):
        ''' major contracts with overlap time.
        
        example: 
            
        rb_mj = MajorContracts(topdir='C:/Qishi_QR/data', maturity={'1609':['2015-11-1','2016-8-1'], \
                            '1705':['2016-6-1','2017-3-1']}, transitions={'1609':'2016-7-1', '1705':'2017-2-1'}) 
        
        df = rb_mj.create_major_overlap()
        
        '''
        
        # if there is no transition provided, return vanilla version.
        if self._transitions == None: return self.create_major()
        
        majorcontracts = pd.DataFrame()
        
        first_day= '2016-1-1'
        last_day = '2016-12-31'
        last_transition = '1900-1-1'
        for exp, trade_range in self._maturity.items():
            
            # laod data
            instrument = self._symbol + exp
            print (instrument, self._topdir + '/'+self._symbol+ '/day')
            
            tick_day = df_reader(instrument + '*', topdir=self._topdir + '/'+self._symbol+ '/day', offset=self._offset, freq=str(self._freq)+'min',day=True, symbol=self._symbol).get_tick(raw=False)
            tick_night = df_reader(instrument + '*', topdir=self._topdir + '/'+self._symbol+ '/night', offset=self._offset, freq=str(self._freq)+'min', day=False, symbol=self._symbol).get_tick(raw=False)

            tick_all = pd.concat([tick_day, tick_night])
            tick_all.sort_index(inplace=True)
            
            # create trade direction
            tick_all['Direction'] = tick_all['LastPrice'].pct_change().apply(lambda x: 2 if x > 0 else (1 if x < 0 else 0))

            # slice major contracts trading period
            assert self._transitions[exp] < trade_range[1] and self._transitions[exp] > trade_range[0]
            
            start_time = max(pd.to_datetime(first_day), pd.to_datetime(last_transition), pd.to_datetime(trade_range[0]))
            end_time   = min(pd.to_datetime(self._transitions[exp]), pd.to_datetime(last_day))
            
            print ('ID', 'trade_range', 'transition_begin', 'transition_end')
            print (exp, trade_range, start_time, end_time)
            
            tick_all = tick_all[(tick_all.index >= start_time) & (tick_all.index < end_time)]
            
            majorcontracts = majorcontracts.append(tick_all)

            last_transition = end_time
            
        return majorcontracts.sort_index()
    
    # todo: calculate probability table.
    
    
