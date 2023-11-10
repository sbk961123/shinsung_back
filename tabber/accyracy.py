from sklearn.metrics import  accuracy_score
import pandas as pd
import joblib

#df_real = # 1 일치 'OK/NG' from dbtable1(실시간품질예측결과 저장디비)
#df_pred = # 1 일치 'OK/NG_pred' from dbtable1(실시간품질예측결과 저장디비)



def accuracy_tabber(df_real, df_pred):

    le = joblib.load('./tabber/pkl/y_scaler/y_le_tps.gz')
    df_real_sc = le.transform(df_real)
    df_pred_sc = le.transform(df_pred)
    acu = accuracy_score(df_real_sc, df_pred_sc)

    return acu