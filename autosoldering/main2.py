from pipeline2 import target_optimization
import pandas as pd

torr, torr2 = target_optimization('TABBER01A', './pkl/model/model_xgb_tps.pkl', './pkl/ohe/ohe_tps.gz', './pkl/scaler/scaler_tps.gz', 
                                 'Shinsung_Tabber_minmax table.xlsx')

print(torr)
