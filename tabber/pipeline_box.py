import pandas as pd

def box_plot_params(df):
    
   X_cols_str_mean = ['TIME_PER_STRING(s)_mean']
   X_colss_temp_mean = [
            'BOTTOMPLATE01_TEMP_mean',
            'BOTTOMPLATE02_TEMP_mean', 
            'BOTTOMPLATE03_TEMP_mean',
            'BOTTOMPLATE04_TEMP_mean', 
            'BOTTOMPLATE05_TEMP_mean', 
            'BOTTOMPLATE06_TEMP_mean', 
            'BOTTOMPLATE07_TEMP_mean', 
            'BOTTOMPLATE08_TEMP_mean', 
            'BOTTOMPLATE09_TEMP_mean', 
            'BOTTOMPLATE10_TEMP_mean']
   X_colss_temp_std = [ 
             'BOTTOMPLATE01_TEMP_std',
             'BOTTOMPLATE02_TEMP_std',
            'BOTTOMPLATE03_TEMP_std',
            'BOTTOMPLATE04_TEMP_std',
            'BOTTOMPLATE05_TEMP_std',
            'BOTTOMPLATE06_TEMP_std',
             'BOTTOMPLATE07_TEMP_std',
            'BOTTOMPLATE08_TEMP_std',
             'BOTTOMPLATE09_TEMP_std',
             'BOTTOMPLATE10_TEMP_std']
   
   
   
   
   X_visua1 = df[X_cols_str_mean]
   X_visua2 = df[X_colss_temp_mean]
   X_visua3 = df[X_colss_temp_std]
   #df_listt = [X_visua1, X_visua2, X_visua3]
   box_params1 = [] 
   box_params2 = [] 
   box_params3 = [] 
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
        
   return box_params1, box_params2, box_params3