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
    
    def __init__(self, symbol='rb', maturity={'1605':['2015-11-1','2016-3-1'],
                                              '1609':['2016-3-1','2016-6-1'],
                                              '1701':['2016-7-1','2016-11-1'],
                                              '1705':['2016-11-1','2017-3-1']},
                        **kwargs):
        
        self._symbol  = symbol
        self._topdir  = kwargs.get('topdir', r'../data')
        self._offset  = kwargs.get('offset', 0.1)
        self._freq    = kwargs.get('freq', 15)       
        self._transitions  = kwargs.get('transitions', None)  # 
        
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
            
            majorcontracts = majorcontracts.append(tick_all)
            
        return majorcontracts
    
    # todo: add overlapping maturities, calculate probability table
    
    
    
