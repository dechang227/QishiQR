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
        self._transitions  = kwargs.get('transitions', None)  # transition time between major contracts
        
        self._maturity = maturity
        
    def create_major(self):
        
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
            
        return majorcontracts.sort_index(inplace=True)
    
    # todo: add overlapping trade_range, use transition information to switch major contracts; and calculate probability table.
    
    
    
