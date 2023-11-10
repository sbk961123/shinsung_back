
import pandas as pd
import joblib
import numpy as np


""" 
신성이엔지 태버공정 품질판정(OK/NG) 예측 파이프라인 함수

신성이엔지 시스템의 [실시간 품질예측 조회 > 품질예측 조회] 화면에서 태버공정 결과물의 품질판정(양불판정) 값을 예측함
(arg)    df: 한 LOT의 태버공정 공정운영 데이터; Dataframe
(return) pred: 예측 품질팜정값(OK/NG); string
"""

def quality_predict(df):

    '''
    대상 컬럼 지정
    '''
    '''
    df.rename(columns={
             'AUTOSOLDERING.MAIN_Z-LEFT':'MAIN_Z-LEFT',
             'AUTOSOLDERING.MAIN_Z-MIDDLE':'MAIN_Z-MIDDLE', 
             'AUTOSOLDERING.MAIN_Z-RIGHT':'MAIN_Z-RIGHT',
             'AUTOSOLDERING.SUB1_CYCLE_TIME':'SUB1_CYCLE_TIME', 
             'AUTOSOLDERING.SUB1_MAX_TEMP':'SUB1_MAX_TEMP', 
             'AUTOSOLDERING.SUB1_PV_TEMP':'SUB1_PV_TEMP', 
             'AUTOSOLDERING.SUB2_CYCLE_TIME':'SUB2_CYCLE_TIME', 
             'AUTOSOLDERING.SUB2_MAX_TEMP':'SUB2_MAX_TEMP',
             'AUTOSOLDERING.SUB2_PV_TEMP':'SUB2_PV_TEMP', 
             'AUTOSOLDERING.SUB3_CYCLE_TIME':'SUB3_CYCLE_TIME', 
             'AUTOSOLDERING.SUB3_MAX_TEMP':'SUB3_MAX_TEMP', 
             'AUTOSOLDERING.SUB3_PV_TEMP':'SUB3_PV_TEMP',
             'AUTOSOLDERING.SUB4_CYCLE_TIME':'SUB4_CYCLE_TIME', 
             'AUTOSOLDERING.SUB4_MAX_TEMP':'SUB4_MAX_TEMP', 
             'AUTOSOLDERING.SUB4_PV_TEMP':'SUB4_PV_TEMP', 
             'AUTOSOLDERING.SUB5_CYCLE_TIME':'SUB5_CYCLE_TIME', 
             'AUTOSOLDERING.SUB5_MAX_TEMP':'SUB5_MAX_TEMP', 
             'AUTOSOLDERING.SUB5_PV_TEMP':'SUB5_PV_TEMP',
             'AUTOSOLDERING.SUB6_CYCLE_TIME':'SUB6_CYCLE_TIME',
             'AUTOSOLDERING.SUB6_MAX_TEMP':'SUB6_MAX_TEMP', 
             'AUTOSOLDERING.SUB6_PV_TEMP':'SUB6_PV_TEMP',
            'AUTOSOLDERING.PLC_COUNTER1':'PLC_COUNTER1'
            }, inplace=True)
    '''

    
    input_cols = ['MAIN_Z-LEFT', 'MAIN_Z-MIDDLE', 'MAIN_Z-RIGHT',
                    'SUB1_CYCLE_TIME', 'SUB1_MAX_TEMP', 'SUB1_PV_TEMP', 
                    'SUB2_CYCLE_TIME', 'SUB2_MAX_TEMP', 'SUB2_PV_TEMP', 
                    'SUB3_CYCLE_TIME', 'SUB3_MAX_TEMP', 'SUB3_PV_TEMP',
                    'SUB4_CYCLE_TIME', 'SUB4_MAX_TEMP', 'SUB4_PV_TEMP', 
                    'SUB5_CYCLE_TIME', 'SUB5_MAX_TEMP', 'SUB5_PV_TEMP',
                    'SUB6_CYCLE_TIME', 'SUB6_MAX_TEMP', 'SUB6_PV_TEMP']
    


    df2 = df[input_cols]



    """
    데이터 전처리 - 데이터 통계압축
    """
    # 컬럼별 통계값 계산
    mean, std = df2.mean(), df2.std()

    # 인덱스명 변경
    mean.rename(lambda x: x + '_' + 'mean', inplace=True)
    std.rename(lambda x: x + '_' + 'std', inplace=True)

    # 데이터프레임 형태로 변경
    df_stat = pd.concat([mean, std], axis=0).to_frame().T.sort_index(axis=1)

    # 표준편차 값이 NaN인 경우(통계압축전 데이터개수=1) 0으로 대치
    df_stat.fillna(0, inplace=True)
    

    auto_bound = pd.read_excel('auto_bound.xlsx', index_col=0)

    ## 컬럼별로 읽어내며 컬럼 전체가 이상치 여부 확인 for loop
    isoutlier_df = ((df_stat > auto_bound['upper']) | (df_stat < auto_bound['lower'])).astype(int)

    ## 각 행의 이상치 개수 합계 계산
    isoutlier_df['이상치개수'] = isoutlier_df.apply(np.sum, axis=1)

    df_stat2 = df_stat.copy()
    ## 원래 데이터프레임에 옮기기
    df_stat2['이상치개수']=isoutlier_df['이상치개수']


    if df_stat2.loc[0,'이상치개수'] >=5:
        df_stat2.loc[0,'OK/NG'] = 'NG'
    else:
        df_stat2.loc[0,'OK/NG'] = 'OK'
        
    """
    예측
    """
    # 예측에 사용할 독립변수 정의

    dr_cols = ['SUB2_CYCLE_TIME_std',
                'SUB3_CYCLE_TIME_std',
                'SUB4_CYCLE_TIME_std',
                'SUB4_PV_TEMP_mean',
                'SUB5_CYCLE_TIME_std',
                'SUB5_PV_TEMP_mean',
                'SUB5_PV_TEMP_std',
                'SUB6_CYCLE_TIME_std',
                'SUB6_PV_TEMP_mean',
                'SUB6_PV_TEMP_std']


    Xcols = df_stat.drop(columns = dr_cols).columns


    # 예측에 사용할 변수 데이터 추출
    X = df_stat2[Xcols]
  
    
    # 데이터 표준화 - 원핫인코딩 된 부분 포함 전체에 적용
    scaler = joblib.load('./pkl/scaler/scaler_tps.gz')
    X_sc = scaler.transform(X)


    # 품질판정 예측
    model = pd.read_pickle('./pkl/model/model_xgb_tps.pkl')

    pred = model.predict(X_sc)



    # 예측결과 인버스인코딩 진행
    le = joblib.load('./pkl/y_scaler/y_le_tps.gz')
    pred = le.inverse_transform(pred)[0]

    X['OK/NG_pred']=''
    X['OK/NG']=''
    X['OK/NG_pred']=pred
    X['OK/NG']=df_stat2['OK/NG'][0]
    X['TO_TIME']=''
    X['TO_TIME']=df['TO_TIME']
    X['FR_TIME']=''
    X['FR_TIME']=df['FR_TIME']
    X['check']=''
    if pred == df_stat2['OK/NG'][0]:
        X['check'] = 'OK'
    else:
        X['check'] = 'check'



    X[Xcols] = X[Xcols].round(2)


    return X