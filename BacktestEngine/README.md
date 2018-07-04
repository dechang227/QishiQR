# BacktestEngine
---
A demo: `./Engine/Demo.ipynb`

## Command
The main routine file `main.py` is in folder `Engine`.  
To run the backtest, call

```python
python Main.py -o PATH_TO_OUTPUT -c PATH_TO_CONFIG
```

where:  
`PATH_TO_OUTPUT`: a folder to save backtest files (`pickle` files). Default valule is `./Results`
`PATH_TO_CONFIG`: path to the configuration file. Default configurations can be found in `main.py`

## Configuration file
Put them 
Format
```json
{
    "symbol": ["bu"],

    "SignalPrice": ["AvePrice2"],
    "TrainPrice":["AvePrice2"],
    "TestPrice":["MidPrice"],

    "frequency": [5, 10, 15],           // Sample frequency
    "threshold": [0],                   // Threshold value
    "threshold_type":[1],               // Threshold type used in Backtesting.Vectorized.Strategy.SLM
    "tca": [-1],                        // Trading costs: -1, 'fixed', 'spread'
    "offset":[0.1],                     // Offset

    "start": ["2016-01-01"],            // start time
    "split": ["2016-07-01"],            // Train-valid split time
    "valid_split": ["2016-10-01"],      // Valid-test split time
    "end": ["2016-12-31"]               // End date
}
```

Each parameter should be a list/tuple, so that the engine can do an outproduct of them and repeat the single parameter accordingly.
