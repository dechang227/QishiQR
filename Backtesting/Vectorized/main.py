# Remember to update your path
import sys
sys.path.append('/home/rz14/Documents/QR_Qishi/QishiQR/')

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

from Utils.IOUtils import *
from Utils.lm import *
from Backtesting.Vectorized.Strategy import MovingAverageStrategy, SLMStrategy
from Backtesting.Vectorized.backtest import vectorizedbacktest
from Backtesting.Vectorized.cross_compare import ensembler

# ====== Initial Configuration ========
ROOT_DIR = "/home/rz14/Documents/QR_Qishi/tick2016/"
DATA_DIR = "/home/rz14/Documents/QR_Qishi/QishiQR/"
OUTPUT = Path(DATA_DIR, "ag")
# =====================================

# Build DATA_PATH with Python Pathlib -- More organized than simple strings with OS library
# https://www.scivision.co/python-idiomatic-pathlib-use/

DATA_PATH = Path(ROOT_DIR, DATA_DIR)
ASSET_PATH = Path(ROOT_DIR,OUTPUT_DIR, ASSET)
ASSET_PATH.mkdir(exist_ok=True, parents=True)


## Scratch below ##

# ========= Build SLM table ==========
DATA_ROOT = Path('/home/rz14/Documents/QR_Qishi/tick2016')
OUTPUT_DIR = Path('/home/rz14/Documents/')
slm = LM_model(data_root_dir=str(DATA_ROOT))






def compile_signal(DATA_PATH, max_order=6):
    data = pd.read_csv(DATA_PATH / 'ag_1712_5min.csv')
    slm = pd.read_csv(DATA_PATH / 'ag_5min_freq.csv')[['prior', 'max']]
    slm = slm.rename(columns={'max': 'signal'})
    signals = [SLMStrategy(data, slm, m).generatingsignal() for m in np.arange(1, max_order+1)]
    return signals

signals = compile_signal(DATA_PATH, max_order=6)

tester_ensemble = ensembler(vectorizedbacktest, signals)
tester_ensemble.build()
tester_ensemble.run()