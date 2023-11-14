from sklearn.metrics import  accuracy_score
import pandas as pd
import joblib

#df_real = # 1 일치 'OK/NG' from dbtable1(실시간품질예측결과 저장디비)
#df_pred = # 1 일치 'OK/NG_pred' from dbtable1(실시간품질예측결과 저장디비)

def accuracy_tabber(df):
    df_ret = pd.DataFrame(columns = ['일자','전체예측건수','NG 예측','PLC NG', '예측정확도'])
    df_ret['일자'] = df['TIME'].unique()
    le = joblib.load('./autosoldering/pkl/y_scaler/y_le_tps.gz')

    for date in df['TIME'].unique():
        
        df_ret1 = df[df['TIME']==date]

        df_ret.loc[df_ret['일자']==date,'전체예측건수'] = len(df_ret1.index)
    
        df_ret.loc[df_ret['일자']==date,'NG 예측'] = (df_ret1['OK/NG']=='NG').sum()
        df_ret.loc[df_ret['일자']==date,'PLC NG'] = (df_ret1['OK/NG_pred']=='NG').sum()

        df_real_sc = le.transform(df_ret1['OK/NG'])
        df_pred_sc = le.transform(df_ret1['OK/NG_pred'])
        df_ret.loc[df_ret['일자']==date,'예측정확도'] = accuracy_score(df_real_sc, df_pred_sc).round(2)*100
    return df_ret