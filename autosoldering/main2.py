from pipeline2 import target_optimization
import pandas as pd

torr, torr2 = target_optimization('./pkl/model/model_xgb_tps.pkl', './pkl/scaler/scaler_tps.gz', 
                                 'Shinsung_AutoSoldering_minmax table.xlsx')

print(torr)
