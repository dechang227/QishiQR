import datetime


class Config:
    root_path = "/home/rz14/Documents/QR_Qishi/QishiQR/"
    tick_path = "/home/rz14/Documents/QR_Qishi/tick2016/"
    strategy_path = "/home/rz14/Documents/QR_Qishi/Strategy/"
    validate_path = "/home/rz14/Documents/QR_Qishi/Validate/"
    output_path = "/home/rz14/Documents/QR_Qishi/QishiQR/Output/"

    price = "AveragePrice"
    state_number = 3
    max_model_order = 7
    frequency = 5
    offset = 0
    tca = -1

    start = datetime.date(2016, 1, 1)
    split = datetime.date(2016, 7, 31)
    end = datetime.date(2016, 10, 31)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            self.__setattr__(key, value)
