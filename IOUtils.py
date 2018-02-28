import pandas as pd
import sys
import os
import fnmatch

from datetime import datetime

class df_reader:
    '''
    Read ticks from all csv files satisfying some patterns in a directory
    '''
    
    def __init__(self, filepat, topdir, offset=0, freq='30S'):
        self._filepat = filepat
        self._topdir  = topdir
        self._offset  = offset
        self._freq    = freq

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
        
    def create_dt_conv_num(self, df, ID='InstrumentID', f1='Date', f2='UpdateTime', dt='dt'):
        '''create datetime and convert to numeric values.'''
    
        # create datetime as index
        df[dt] = df[f1].astype(str) + " " + df[f2].astype(str)
        df[dt] = pd.to_datetime(df[dt], format="%Y%m%d %H:%M:%S.%f")
    
        df.sort_values(by=[dt], inplace=True)
    
        # df.drop([f1, f2], axis=1, inplace=True)
    
        df.set_index(dt, inplace=True)

        # drop duplicate index
        df = df[~df.index.duplicated(keep='last')]
        
        # convert to nuemric values
        #num_col = [col for col in df.columns if col!=ID and col!=dt]
    
        #df[num_col] = df[num_col].convert_objects(convert_numeric=True)
    
        return df

    def f_fill(self, filename):
        '''read in the data from filename, create time series index, forward fill the data.
        then return dataframe given offset, and at selected freq.'''
        
        df = pd.read_csv(filename)
    
        dates = filename.split('_')[1].split('.')[0]
    
        index1=pd.date_range(dates+' 09:00:00.0', dates+' 11:30:00.0', freq='500L')
        index2=pd.date_range(dates+' 13:30:00.0', dates+' 15:00:00.5', freq='500L')
        index=index1.append(index2)
    
        df = self.create_dt_conv_num(df)
                
        #print (filename, len(df))
    
        return df.reindex(index, method='ffill').resample(self._freq).asfreq().dropna()

    
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