import numpy as np
import pandas as pd


def get_heat_corr(df):
    
    
   X_colss = [ 'TIME_PER_STRING(s)_mean',
                'BOTTOMPLATE01_TEMP_mean', 'BOTTOMPLATE01_TEMP_std',
                'BOTTOMPLATE02_TEMP_mean', 'BOTTOMPLATE02_TEMP_std',
                'BOTTOMPLATE03_TEMP_mean', 'BOTTOMPLATE03_TEMP_std',
                'BOTTOMPLATE04_TEMP_mean', 'BOTTOMPLATE04_TEMP_std',
                'BOTTOMPLATE05_TEMP_mean', 'BOTTOMPLATE05_TEMP_std',
                'BOTTOMPLATE06_TEMP_mean', 'BOTTOMPLATE06_TEMP_std',
                'BOTTOMPLATE07_TEMP_mean', 'BOTTOMPLATE07_TEMP_std',
                'BOTTOMPLATE08_TEMP_mean', 'BOTTOMPLATE08_TEMP_std',
                'BOTTOMPLATE09_TEMP_mean', 'BOTTOMPLATE09_TEMP_std',
                'BOTTOMPLATE10_TEMP_mean', 'BOTTOMPLATE10_TEMP_std']
   X_visua = df[X_colss]
    
   let_bwChart =[]
    
   corr = X_visua.corr()
   corr_mask = np.tril(corr)
   corr_mask = pd.DataFrame(corr_mask, index=corr.index, columns=corr.columns)
    
   for col1 in corr_mask.index:
       for col2 in corr_mask.columns:
            if col1 == col2:
               corr_mask.loc[col1,col2] = 0
            else:
                pass
        
    
   for col1 in corr_mask.index:
       for col2 in corr_mask.columns:
           corrin = {
                 'yData': col1,
                'xData': col2,
                'value': corr_mask.loc[col1,col2]
            }
           let_bwChart.append(corrin)
    
    
   return let_bwChart