import pandas as pd

def box_plot_params(df):
    
   z_mean = ['MAIN_Z-LEFT_mean','MAIN_Z-MIDDLE_mean', 'MAIN_Z-RIGHT_mean']
   z_std = ['MAIN_Z-LEFT_std', 'MAIN_Z-MIDDLE_std', 'MAIN_Z-RIGHT_std']
   cycle_mean = ['SUB1_CYCLE_TIME_std','SUB2_CYCLE_TIME_std','SUB3_CYCLE_TIME_std',
               'SUB4_CYCLE_TIME_std','SUB5_CYCLE_TIME_std','SUB6_CYCLE_TIME_std']
   cycle_std = ['SUB1_CYCLE_TIME_mean','SUB2_CYCLE_TIME_mean','SUB3_CYCLE_TIME_mean',
               'SUB4_CYCLE_TIME_mean','SUB5_CYCLE_TIME_mean','SUB6_CYCLE_TIME_mean']
   max_mean = ['SUB1_MAX_TEMP_mean','SUB2_MAX_TEMP_mean','SUB3_MAX_TEMP_mean',
             'SUB4_MAX_TEMP_mean','SUB5_MAX_TEMP_mean','SUB6_MAX_TEMP_mean']
   max_std = ['SUB1_MAX_TEMP_std','SUB2_MAX_TEMP_std','SUB3_MAX_TEMP_std',
              'SUB4_MAX_TEMP_std','SUB5_MAX_TEMP_std','SUB6_MAX_TEMP_std']
   pv_mean = ['SUB1_PV_TEMP_mean','SUB2_PV_TEMP_mean','SUB3_PV_TEMP_mean',
            'SUB4_PV_TEMP_mean','SUB5_PV_TEMP_mean','SUB6_PV_TEMP_mean']
   pv_std = ['SUB1_PV_TEMP_std','SUB2_PV_TEMP_std','SUB3_PV_TEMP_std',
           'SUB4_PV_TEMP_std','SUB5_PV_TEMP_std','SUB6_PV_TEMP_std']
   
   X_visua1 = df[z_mean]
   X_visua2 = df[z_std]
   X_visua3 = df[max_mean]
   X_visua4 = df[max_std]
   X_visua5 = df[pv_mean]
   X_visua6 = df[pv_std]

   #df_listt = [X_visua1, X_visua2, X_visua3]
   box_params1 = [] 
   box_params2 = [] 
   box_params3 = [] 
   box_params4 = [] 
   box_params5 = [] 
   box_params6 = [] 
   #box_listt = [box_params1, box_params2, box_params3]
   
   for col in X_visua1.columns:
            box_Q1 = X_visua1[col].quantile(0.25).round(2)
            box_Q2 = X_visua1[col].quantile(0.50).round(2)
            box_Q3 = X_visua1[col].quantile(0.75).round(2)
            box_IQR = box_Q3-box_Q1
            lower = (box_Q1-box_IQR).round(2)
            upper = (box_Q3+box_IQR).round(2)
            test_list = {'TAG': col,
                            'high': upper,
                            'open': box_Q3,
                            'mediana': box_Q2,
                            'close': box_Q1,
                            'low': lower}
            box_params1.append(test_list)
            
   for col in X_visua2.columns:
            box_Q1 = X_visua2[col].quantile(0.25).round(2)
            box_Q2 = X_visua2[col].quantile(0.50).round(2)
            box_Q3 = X_visua2[col].quantile(0.75).round(2)
            box_IQR = box_Q3-box_Q1
            lower = (box_Q1-box_IQR).round(2)
            upper = (box_Q3+box_IQR).round(2)
            test_list = {'TAG': col,
                            'high': upper,
                            'open': box_Q3,
                            'mediana': box_Q2,
                            'close': box_Q1,
                            'low': lower}
            box_params2.append(test_list)
            
   for col in X_visua3.columns:
            box_Q1 = X_visua3[col].quantile(0.25).round(2)
            box_Q2 = X_visua3[col].quantile(0.50).round(2)
            box_Q3 = X_visua3[col].quantile(0.75).round(2)
            box_IQR = box_Q3-box_Q1
            lower = (box_Q1-box_IQR).round(2)
            upper = (box_Q3+box_IQR).round(2)
            test_list = {'TAG': col,
                            'high': upper,
                            'open': box_Q3,
                            'mediana': box_Q2,
                            'close': box_Q1,
                            'low': lower}
            box_params3.append(test_list)

   for col in X_visua4.columns:
            box_Q1 = X_visua4[col].quantile(0.25).round(2)
            box_Q2 = X_visua4[col].quantile(0.50).round(2)
            box_Q3 = X_visua4[col].quantile(0.75).round(2)
            box_IQR = box_Q3-box_Q1
            lower = (box_Q1-box_IQR).round(2)
            upper = (box_Q3+box_IQR).round(2)
            test_list = {'TAG': col,
                            'high': upper,
                            'open': box_Q3,
                            'mediana': box_Q2,
                            'close': box_Q1,
                            'low': lower}
            box_params4.append(test_list)

   for col in X_visua5.columns:
            box_Q1 = X_visua5[col].quantile(0.25).round(2)
            box_Q2 = X_visua5[col].quantile(0.50).round(2)
            box_Q3 = X_visua5[col].quantile(0.75).round(2)
            box_IQR = box_Q3-box_Q1
            lower = (box_Q1-box_IQR).round(2)
            upper = (box_Q3+box_IQR).round(2)
            test_list = {'TAG': col,
                            'high': upper,
                            'open': box_Q3,
                            'mediana': box_Q2,
                            'close': box_Q1,
                            'low': lower}
            box_params5.append(test_list)


   for col in X_visua6.columns:
            box_Q1 = X_visua6[col].quantile(0.25).round(2)
            box_Q2 = X_visua6[col].quantile(0.50).round(2)
            box_Q3 = X_visua6[col].quantile(0.75).round(2)
            box_IQR = box_Q3-box_Q1
            lower = (box_Q1-box_IQR).round(2)
            upper = (box_Q3+box_IQR).round(2)
            test_list = {'TAG': col,
                            'high': upper,
                            'open': box_Q3,
                            'mediana': box_Q2,
                            'close': box_Q1,
                            'low': lower}
            box_params6.append(test_list)
        
   return box_params1, box_params2, box_params3, box_params4, box_params5, box_params6