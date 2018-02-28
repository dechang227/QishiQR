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
df_reader('bu1601*', topdir='../tick2016/bu/day/').get_tick(raw=True)
```
| Time                       | InstrumentID   |     Date |   TimeStamp |   LastPrice |   HighPrice |   LowPrice |   Volume |   Turnover |   AccVolume |   AccTurnover |   SettlePrice |   OpenInterest |   AskPrice1 |   AskPrice2 |   AskPrice3 |   AskPrice4 |   AskPrice5 |   AskVolume1 |   AskVolume2 |   AskVolume3 |   AskVolume4 |   AskVolume5 |   BidPrice1 |   BidPrice2 |   BidPrice3 |   BidPrice4 |   BidPrice5 |   BidVolume1 |   BidVolume2 |   BidVolume3 |   BidVolume4 |   BidVolume5 |   Type |   AveragePrice |   UpperLimitPrice |   LowerLimitPrice | UpdateTime   |
|:---------------------------|:---------------|---------:|------------:|------------:|------------:|-----------:|---------:|-----------:|------------:|--------------:|--------------:|---------------:|------------:|------------:|------------:|------------:|------------:|-------------:|-------------:|-------------:|-------------:|-------------:|------------:|------------:|------------:|------------:|------------:|-------------:|-------------:|-------------:|-------------:|-------------:|-------:|---------------:|------------------:|------------------:|:-------------|
| 2016-01-04 18:33:30.967000 | bu1601         | 20160104 |  1.4519e+12 |        1630 |        1630 |       1630 |        0 |         -1 |           0 |             0 |            -1 |          20284 |           0 |           0 |           0 |           0 |           0 |            0 |            0 |            0 |            0 |            0 |           0 |           0 |           0 |           0 |           0 |            0 |            0 |            0 |            0 |            0 |     -1 |              0 |              1734 |              1536 | 18:33:30.967 |
| 2016-01-04 18:33:31.500000 | bu1601         | 20160104 |  1.4519e+12 |        1630 |        1630 |       1630 |        0 |          0 |           0 |             0 |            -1 |          20284 |           0 |           0 |           0 |           0 |           0 |            0 |            0 |            0 |            0 |            0 |           0 |           0 |           0 |           0 |           0 |            0 |            0 |            0 |            0 |            0 |     -1 |              0 |              1734 |              1536 | 18:33:31.500 |