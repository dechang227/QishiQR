import datetime


class Config:
    root_path = "/home/runmin/Documents/Qishi/QishiQR"
    tick_path = "/home/runmin/Documents/Qishi/tick2016/"
    dataset_path = "./data"
    strategy_path = "/home/runmin/Documents/Qishi/Strategy"
    major_path = "/home/runmin/Documents/Qishi/Major_Series"
    validate_path = "/home/runmin/Documents/Qishi/Validate"
    output_path = "/home/runmin/Documents/Qishi/Output"

    state_number = 3
    max_model_order = 7
    frequency = 5
    offset = 0
    tca = -1

    start = datetime.date(2016, 1, 1)
    split = datetime.date(2016, 7, 31)
    end = datetime.date(2016, 10, 31)


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

    def __init__(self, frequency = 5):
        super(BuConfig, self).__init__()
        self.frequency = frequency


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

    def __init__(self, frequency = 5):
        super(RbConfig, self).__init__()
        self.frequency = frequency
        
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

    def __init__(self, frequency = 5):
        super(RuConfig, self).__init__()
        self.frequency = frequency