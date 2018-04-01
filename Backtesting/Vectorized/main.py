# Remember to update your path
import sys
sys.path.append('/home/rz14/Documents/QR_Qishi/QishiQR/')

from pathlib import Path

from Backtesting.Vectorized.cross_compare import *

import warnings
warnings.filterwarnings(action='ignore')

# ====== Initial Configuration ========

ROOT_DIR = "/home/rz14/Documents/QR_Qishi/QishiQR/"
DATA_DIR = "/home/rz14/Documents/QR_Qishi/tick2016/"
OUTPUT_DIR = "/home/rz14/Documents/QR_Qishi/QishiQR/Output/"
ASSET = 'ag'
ASSET_PATH = Path(OUTPUT_DIR, ASSET)
ASSET_PATH.mkdir(exist_ok=True, parents=True)

model_order = 7
freq = '5min'
offset = 0
tca = None

start = '20160701'
end = '20161031'
commodity = ASSET
exp_date = '1701'

# === Main Routine ===

test1 = tester(DATA_DIR, OUTPUT_DIR)
test1.build(commodity, exp_date, model_order, freq, offset, start, end, tca)
test1.run()
test1.plot()