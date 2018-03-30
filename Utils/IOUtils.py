import pandas as pd
import sys
import os
import re
import fnmatch
from datetime import datetime
from datetime import timedelta  

class df_reader:
    '''
    Read ticks from all csv files satisfying some patterns in a directory.
    offset in minutes.
    '''
    
    def __init__(self, filepat, topdir, offset=0, freq='30S', day=True, symbol='rb'):
        self._filepat = filepat
        self._topdir  = topdir
        self._offset  = offset
        self._freq    = freq
        self._day     = day
        self._symbol  = symbol.lower()

    def get_tick(self, raw=False):
        """ Get ticks from csv file
        Args:
            raw: boolean. Whether to return raw tick or the forward filled data.
        Returns:
            A DataFrame contains the tick
        """
        if raw is True:
            lognames = self.gen_find()
            return self._get_raw_tick(lognames)
        else:
            lognames = self.gen_find()
            df = self.gen_df(lognames)
            return df
    
    ############################################################################
    #                   Methods about reading raw tick                         # 
    #--------------------------------------------------------------------------#
    
    def _get_raw_tick(self, filenames):
        """ Obtain the raw tick
        Obtain the raw tick from csv files
        
        Args:
            filenames: contains names of files to read
        Returns:
            raw_tick: A DataFrame contain the raw ticks from the csv files
        """
        
        raw_tick = pd.DataFrame()
        for filename in filenames:
            tmp = pd.read_csv(filename)
            tmp = self._reindex_time(tmp)
            raw_tick = raw_tick.append(tmp)
        return raw_tick.sort_index()

    
    ###########################################################################
    #                 Methods about reading f-filled tick                     # 
    #-------------------------------------------------------------------------#
        
    def create_dt(self, df, ID='InstrumentID', f1='Date', f2='UpdateTime', dt='dt'):
        '''create datetime index.'''
        # create datetime as index
        df[dt] = df[f1].astype(str) + " " + df[f2].astype(str)
        df[dt] = pd.to_datetime(df[dt], format="%Y%m%d %H:%M:%S.%f")
    
        df.sort_values(by=[dt], inplace=True)
    
        # df.drop([f1, f2], axis=1, inplace=True)
    
        df.set_index(dt, inplace=True)

        # drop duplicate index
        df = df[~df.index.duplicated(keep='last')]
            
        return df

    def clean_df(self, df, cols=['LastPrice', 'AskPrice1', 'AskVolume1', \
                                 'BidPrice1', 'BidVolume1']):
    
        '''Clean the dataframe - postive prcies/volume quote.
        '''
        for c in cols:
            df = df[df[c]>0]
    
        return df
        
    def f_fill(self, filename):
        '''read in the data from filename, create time series index, forward fill the data.
        then return dataframe given offset, and at selected freq.'''
        
        # read in data
        df = pd.read_csv(filename)
        if df.empty:
            print(filename + " is empty")
            return df
        # Obtain the trading dates in the file
        dates = [str(day) for day in df['Date'].unique()]  
        self.dates = dates
        #print(dates)
        # clean data
        df = self.clean_df(df)

       
        # add offset in minutes
        if self._day:  # day time
            start = pd.to_datetime(dates[0] + ' 09:00:00.0') + timedelta(minutes=self._offset)
            index1 = pd.date_range(start, dates[0]+' 10:15:00.0', freq=self._freq)
            start_mid = pd.to_datetime(dates[0]+' 10:30:00.0') + timedelta(minutes=self._offset)
            index2 = pd.date_range(start_mid, dates[0]+' 11:30:00.0', freq=self._freq)
            start_aft = pd.to_datetime(dates[0] + ' 13:30:00.0') + timedelta(minutes=self._offset)
            index3 = pd.date_range(start_aft, dates[0]+' 15:00:00.5', freq=self._freq)
            
            index = index1.append(index2).append(index3)
        else:    
            # night start time: 21pm for all 4 kinds of future assets
            night_start = ' 21:00:00.0'
            # night start time:
            night_end = {
                'ag': ' 2:30:00.0',        # Ag: 02:30am
                'bu': ' 1:00:00.0',        # Bu: 01:00am
                'rb': ' 23:00:00.0',        # Rb: 23:00pm
                'ru': ' 23:00:00.0',        # Ru: 23:00pm
                'zn': ' 1:00:00.0'         # Zn: 01:00am
            }

            try:
                start = pd.to_datetime(dates[0] + night_start) + timedelta(minutes=self._offset)
                index=pd.date_range(start, dates[-1] + night_end[self._symbol], freq=self._freq)
            except KeyError:
                print ('Symbol {} not recoginized !!!'.format(self._symbol))
                sys.exit()
    
        df = self.create_dt(df)
                
        # reindex and forward fill, start from offset position
        df = df.reindex(index, method='ffill')
        
        return df.dropna()
    
    def gen_df(self, filenames):
        '''
        Open a sequence of filenames one at a time producing a file object.
        The file is closed immediately when proceeding to the next iteration.
        '''
        df = pd.DataFrame()
        for filename in filenames:

            tmp = self.f_fill(filename)
            
            df = df.append(tmp)     
        
            #print (tmp.head())
            
        return df.sort_index()
    
        


    ########################################################################
    #                       Utilities                                      # 
    ########################################################################
    @staticmethod
    def count_word(tick_sequence: str, pattern: str):
        """
        Employ regular expressions (?=) to count the
        the total occurence of pattern in the tick_sequence
        NOTE: this function is equvalent to
        tick_sequence.count(r'(?={})'.format(ternary(k, n)))

        Args:
            tick_sequence: Tick sequences to be searched
            pattern: pattern to be searched.
        """
        return len(re.findall(r"(?={0})".format(pattern), tick_sequence))
    
    def gen_find(self):
        '''
        Find all filenames in a directory tree that match a shell wildcard pattern.
        '''
        for path, dirlist, filelist in os.walk(self._topdir):
            for name in fnmatch.filter(filelist, self._filepat):
                yield os.path.join(path,name)

    def _reindex_time(self, df, DateCol='Date', TimeCol='UpdateTime'):
        """ Reindex the dataframe
        Create datetime index for the csv files
        
        Args:
            df: pandas.DataFrame. Df where we want to extract time
        Return:
            df: pandas DataFrame. New Df with time as index
        """
        TimeString = df[DateCol].apply(str) + df[TimeCol].apply(str)
        df['Time'] = TimeString.apply(lambda time_string: datetime.strptime(time_string, '%Y%m%d%H:%M:%S.%f'))
        return df.set_index('Time')
