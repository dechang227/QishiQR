import datetime


class Config:
    root_path = "D:/GitHub/QishiQR"
    tick_path = "D:/GitHub/QishiQR/Data"
    dataset_path = "D:/GitHub/QishiQR/Data"
    strategy_path = "D:/GitHub/QishiQR/Strategy"
    major_path = "D:/GitHub/QishiQR/Major_Series"
    validate_path = "D:/GitHub/QishiQR/Validate"
    output_path = "D:/GitHub/QishiQR/Output"

    state_number = 3
    max_model_order = 7
    frequency = 5
    offset = 0
    tca = -1

    start = datetime.date(2016, 1, 1)
    split = datetime.date(2016, 7, 1)
    end = datetime.date(2016, 12, 31)


class BuConfig(Config):
    symbol = 'bu'

    maturity = {'1606': ['2015-11-1', '2016-5-1'],
                '1609': ['2016-2-1', '2016-8-1'],
                '1612': ['2016-6-1', '2016-11-15'],
                '1706': ['2016-10-15', '2017-1-31']}

    transition = {'1606': '2016-4-1',
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

class AgConfig(Config):
    symbol = 'ag'

    maturity = {'1606': ['2015-11-1', '2016-5-1'],
                '1612': ['2016-3-1', '2016-11-1'],
                '1706': ['2016-6-1', '2017-1-31']}

    transition = {'1606': '2016-4-1',
                  '1612': '2016-7-1',
                  '1706': '2017-1-1'}

    def __init__(self, frequency = 5):
        super(AgConfig, self).__init__()
        self.frequency = frequency
