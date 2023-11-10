import numpy as np
import pandas as pd


def get_heat_corr(df):
    
    
   X_colss =  ['MAIN_Z-LEFT_mean', 'MAIN_Z-LEFT_std', 'MAIN_Z-MIDDLE_mean',
                'MAIN_Z-MIDDLE_std', 'MAIN_Z-RIGHT_mean', 'MAIN_Z-RIGHT_std',
                'SUB1_CYCLE_TIME_mean', 'SUB1_CYCLE_TIME_std', 'SUB1_MAX_TEMP_mean',
                'SUB1_MAX_TEMP_std', 'SUB1_PV_TEMP_mean', 'SUB1_PV_TEMP_std',
                'SUB2_CYCLE_TIME_mean', 'SUB2_CYCLE_TIME_std', 'SUB2_MAX_TEMP_mean',
                'SUB2_MAX_TEMP_std', 'SUB2_PV_TEMP_mean', 'SUB2_PV_TEMP_std',
                'SUB3_CYCLE_TIME_mean', 'SUB3_CYCLE_TIME_std', 'SUB3_MAX_TEMP_mean',
                'SUB3_MAX_TEMP_std', 'SUB3_PV_TEMP_mean', 'SUB3_PV_TEMP_std',
                'SUB4_CYCLE_TIME_mean', 'SUB4_CYCLE_TIME_std', 'SUB4_MAX_TEMP_mean',
                'SUB4_MAX_TEMP_std', 'SUB4_PV_TEMP_mean', 'SUB4_PV_TEMP_std',
                'SUB5_CYCLE_TIME_mean', 'SUB5_CYCLE_TIME_std', 'SUB5_MAX_TEMP_mean',
                'SUB5_MAX_TEMP_std', 'SUB5_PV_TEMP_mean', 'SUB5_PV_TEMP_std',
                'SUB6_CYCLE_TIME_mean', 'SUB6_CYCLE_TIME_std', 'SUB6_MAX_TEMP_mean',
                'SUB6_MAX_TEMP_std', 'SUB6_PV_TEMP_mean', 'SUB6_PV_TEMP_std']
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