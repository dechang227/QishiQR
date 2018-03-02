# QishiQR

## `IOUtils.py` Usage
### Obtain raw ticks
---
Example: obtaining all ticks in csv files starting with `bu1601` in the directory `/tick2016/bu/`
```
from IOUtils import *
df_reader('bu1601*', topdir='../tick2016/bu/').get_tick(raw=True)
```
Results:

| Time                       | InstrumentID   |     Date |   TimeStamp |   LastPrice |   HighPrice |   LowPrice |   Volume |   Turnover |   AccVolume |   AccTurnover |   SettlePrice |   OpenInterest |   AskPrice1 |   AskPrice2 |   AskPrice3 |   AskPrice4 |   AskPrice5 |   AskVolume1 |   AskVolume2 |   AskVolume3 |   AskVolume4 |   AskVolume5 |   BidPrice1 |   BidPrice2 |   BidPrice3 |   BidPrice4 |   BidPrice5 |   BidVolume1 |   BidVolume2 |   BidVolume3 |   BidVolume4 |   BidVolume5 |   Type |   AveragePrice |   UpperLimitPrice |   LowerLimitPrice | UpdateTime   |
|:---------------------------|:---------------|---------:|------------:|------------:|------------:|-----------:|---------:|-----------:|------------:|--------------:|--------------:|---------------:|------------:|------------:|------------:|------------:|------------:|-------------:|-------------:|-------------:|-------------:|-------------:|------------:|------------:|------------:|------------:|------------:|-------------:|-------------:|-------------:|-------------:|-------------:|-------:|---------------:|------------------:|------------------:|:-------------|
| 2016-01-04 18:33:30.967000 | bu1601         | 20160104 |  1.4519e+12 |        1630 |        1630 |       1630 |        0 |         -1 |           0 |             0 |            -1 |          20284 |           0 |           0 |           0 |           0 |           0 |            0 |            0 |            0 |            0 |            0 |           0 |           0 |           0 |           0 |           0 |            0 |            0 |            0 |            0 |            0 |     -1 |              0 |              1734 |              1536 | 18:33:30.967 |
| 2016-01-04 18:33:31.500000 | bu1601         | 20160104 |  1.4519e+12 |        1630 |        1630 |       1630 |        0 |          0 |           0 |             0 |            -1 |          20284 |           0 |           0 |           0 |           0 |           0 |            0 |            0 |            0 |            0 |            0 |           0 |           0 |           0 |           0 |           0 |            0 |            0 |            0 |            0 |            0 |     -1 |              0 |              1734 |              1536 | 18:33:31.500 |



### Obtain forward-filled ticks

__Note__: It doesn't work for night market ticks yet.

Line 91: In `df_reader.f_fill`, the sampling index is hard-coded for day markets.


```
from IOUtils import *
df_reader('bu1601*', topdir='../tick2016/bu/day/').get_tick(raw=false)
```
|                     | InstrumentID   |        Date |   TimeStamp |   LastPrice |   HighPrice |   LowPrice |   Volume |   Turnover |   AccVolume |    AccTurnover |   SettlePrice |   OpenInterest |   AskPrice1 |   AskPrice2 |   AskPrice3 |   AskPrice4 |   AskPrice5 |   AskVolume1 |   AskVolume2 |   AskVolume3 |   AskVolume4 |   AskVolume5 |   BidPrice1 |   BidPrice2 |   BidPrice3 |   BidPrice4 |   BidPrice5 |   BidVolume1 |   BidVolume2 |   BidVolume3 |   BidVolume4 |   BidVolume5 |   Type |   AveragePrice |   UpperLimitPrice |   LowerLimitPrice | UpdateTime   |
|:--------------------|:---------------|------------:|------------:|------------:|------------:|-----------:|---------:|-----------:|------------:|---------------:|--------------:|---------------:|------------:|------------:|------------:|------------:|------------:|-------------:|-------------:|-------------:|-------------:|-------------:|------------:|------------:|------------:|------------:|------------:|-------------:|-------------:|-------------:|-------------:|-------------:|-------:|---------------:|------------------:|------------------:|:-------------|
| 2016-01-04 09:00:00 | bu1601         | 2.01601e+07 | 1.45187e+12 |        1702 |        1702 |       1702 |        4 |      68080 |           4 | 68080          |            -1 |          22640 |        1718 |           0 |           0 |           0 |           0 |            3 |            0 |            0 |            0 |            0 |        1700 |           0 |           0 |           0 |           0 |            1 |            0 |            0 |            0 |            0 |     -1 |           1702 |              1812 |              1606 | 08:59:00.500 |
| 2016-01-04 09:00:30 | bu1601         | 2.01601e+07 | 1.45187e+12 |        1706 |        1724 |       1702 |        0 |          0 |          70 |     1.2012e+06 |            -1 |          22666 |        1708 |           0 |           0 |           0 |           0 |            8 |            0 |            0 |            0 |            0 |        1706 |           0 |           0 |           0 |           0 |            1 |            0 |            0 |            0 |            0 |     -1 |           1716 |              1812 |              1606 | 09:00:30.000 |


__use_case__: df_reader(filepat='ag1712*', topdir='../ag/day', offset=5, freq='30S'), where offset is in minutes (offset=5 means that it starts 5 minutes after opening 9 AM) and frequency is in 30 seconds.
