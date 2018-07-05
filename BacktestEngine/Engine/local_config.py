import datetime


class Config:
    """ Global base configuration. Original in Backtesting.Vectorized.config """

    root_path = "/home/runmin/Documents/Qishi/QishiQR/"
    tick_path = "/home/runmin/Documents/Qishi/tick2016/"
    strategy_path = "/home/runmin/Documents/Qishi/Strategy/"
    validate_path = "/home/runmin/Documents/Qishi/Validate/"
    output_path = "/home/runmin/Documents/Qishi/QishiQR/Output/"
    
    TrainPrice="AvePrice2"
    SignalPrice = "AvePrice2"
    TestPrice = "MidPrice"
    
    state_number = 3
    max_model_order = 7
    frequency = 5
    offset = 0
    tca = -1
  
    threshold = 5*1e-4
    threshold_type = 1

    # start = datetime.date(2016, 1, 1)
    # split = datetime.date(2016, 7, 1)
    # valid_split = datetime.date(2016, 10, 1)
    # end = datetime.date(2016, 12, 31)

    start = "2016-01-01"
    split = "2016-07-01"
    valid_split = "2016-10-01"
    end = "2016-12-31"

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            self.__setattr__(key, value)


class BuConfig(Config):
    symbol = 'bu'

    maturity = {'1606': ['2015-11-1', '2016-5-1'],
                '1609': ['2016-2-1', '2016-8-1'],
                '1612': ['2016-6-1', '2016-11-15'],
                '1706': ['2016-10-15', '2017-1-31']}

    transition = {'1606': '2016-3-1',
                  '1609': '2016-7-1',
                  '1612': '2016-11-1',
                  '1706': '2017-1-1'}

    def __init__(self, **kwargs):
        super(BuConfig, self).__init__(**kwargs)


class RbConfig(Config):
    symbol = 'rb'

    maturity = {'1605': ['2015-11-1', '2016-5-1'],
                '1610': ['2016-2-1', '2016-8-1'],
                '1701': ['2016-6-1', '2016-12-15'],
                '1705': ['2016-10-15', '2017-1-31']}

    transition = {'1605': '2016-3-1',
                  '1610': '2016-7-1',
                  '1701': '2016-12-1',
                  '1705': '2017-1-1'}

    def __init__(self, **kwargs):
        super(RbConfig, self).__init__(**kwargs)


class RuConfig(Config):
    symbol = 'ru'

    maturity = {'1605': ['2015-11-1', '2016-5-16'],
                '1609': ['2016-2-1', '2016-8-19'],
                '1701': ['2016-6-1', '2016-12-15'],
                '1705': ['2016-11-15', '2017-1-31']}

    transition = {'1605': '2016-3-17',
                  '1609': '2016-8-1',
                  '1701': '2016-11-23',
                  '1705': '2017-1-1'}

    def __init__(self, **kwargs):
        super(RuConfig, self).__init__(**kwargs)


class AgConfig(Config):
    symbol = 'ag'

    maturity = {'1606': ['2015-11-1', '2016-5-1'],
                '1612': ['2016-3-1', '2016-11-1'],
                '1706': ['2016-6-1', '2017-1-31']}

    transition = {'1606': '2016-4-1',
                  '1612': '2016-10-15',
                  '1706': '2017-1-1'}

    def __init__(self, **kwargs):
        super(AgConfig, self).__init__(**kwargs)


class ZnConfig(Config):
    symbol = 'zn'

    maturity = {
        '1603':['2016-1-1','2016-2-29'],
        '1604':['2016-2-1','2016-3-31'],
        '1605':['2016-3-1','2016-4-30'],
        '1606':['2016-4-1','2016-5-31'],
        '1607':['2016-5-1','2016-6-30'],
        '1608':['2016-6-1','2016-7-31'],
        '1609':['2016-7-1','2016-8-31'],
        '1610':['2016-8-1','2016-9-30'],
        '1611':['2016-9-1','2016-10-31'],
        '1612':['2016-10-1','2016-11-30'],
        '1701':['2016-11-1','2016-12-31'],
        '1702':['2016-12-1','2017-1-31']
    }

    transition = {
        '1603':'2016-2-1', 
        '1604':'2016-3-1',
        '1605':'2016-4-1',
        '1606':'2016-5-1',
        '1607':'2016-6-1',
        '1608':'2016-7-1',
        '1609':'2016-8-1',
        '1610':'2016-9-1',
        '1611':'2016-10-1',
        '1612':'2016-11-1',
        '1701':'2016-12-1',
        '1702':'2017-1-1'
    }

    def __init__(self, **kwargs):
        super(ZnConfig, self).__init__(**kwargs)
