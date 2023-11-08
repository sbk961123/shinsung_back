"""
python version = 3.8.17
xgboost version = 2.0.0
"""

import pandas as pd
import joblib


""" 
신성이엔지 태버공정 품질판정(OK/NG) 예측 파이프라인 함수

신성이엔지 시스템의 [실시간 품질예측 조회 > 품질예측 조회] 화면에서 태버공정 결과물의 품질판정(양불판정) 값을 예측함
(arg)    df: 한 LOT의 태버공정 공정운영 데이터; Dataframe
(return) pred: 예측 품질팜정값(OK/NG); string
"""

def quality_predict(df):
    """
    데이터 전처리 - 데이터 통계압축
    """
    # 컬럼별 통계값 계산
    mean, std = df.mean(numeric_only=True), df.std(numeric_only=True)
    # q1, q3 = df.quantile(0.25, numeric_only=True), df.quantile(0.75, numeric_only=True)

    # 인덱스명 변경
    mean.rename(lambda x: x + '_' + 'mean', inplace=True)
    std.rename(lambda x: x + '_' + 'std', inplace=True)

    # 데이터프레임 형태로 변경
    df_stat = pd.concat([mean, std], axis=0).to_frame().T.sort_index(axis=1)
    df_stat.insert(loc=0, column='EQUIPNUM', value=df['EQUIPNUM'][0])

    # 표준편차 값이 NaN인 경우(통계압축전 데이터개수=1) 0으로 대치
    df_stat.fillna(0, inplace=True)
    
    """
    예측
    """
    # 예측에 사용할 독립변수 정의
    Xcols = ['EQUIPNUM', 'TIME_PER_STRING(s)_mean',
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

    # 예측에 사용할 변수 데이터 추출
    X = df_stat[Xcols]

    # 범주형 변수 인코딩
    ohe = joblib.load('./tabber/pkl/ohe/ohe_tps.gz')
    cols = ['EQUIPNUM' + '_' + col for col in ohe.categories_[0]]
    X[cols] = ohe.transform(X[['EQUIPNUM']])
    X.drop('EQUIPNUM', axis=1, inplace=True)   
    
    # 데이터 표준화 - 원핫인코딩 된 부분 포함 전체에 적용
    scaler = joblib.load('./tabber/pkl/scaler/scaler_tps.gz')
    X_sc = scaler.transform(X)

    # 품질판정 예측
    model = pd.read_pickle('./tabber/pkl/model/model_xgb_tps.pkl')
    pred = model.predict(X_sc)

    # 예측결과 인버스인코딩 진행
    le = joblib.load('./tabber/pkl/y_scaler/y_le_tps.gz')
    pred = le.inverse_transform(pred)[0]

    X['OK/NG_pred']=''
    X['OK/NG']=''
    X['OK/NG_pred']=pred
    X['OK/NG']=df['OK/NG'][0]
    X['EQUIPNUM']=''
    X['EQUIPNUM']=df['EQUIPNUM'][0]
    X['TO_TIME']=''
    X['TO_TIME']=df['TO_TIME']
    X['FR_TIME']=''
    X['FR_TIME']=df['FR_TIME']
    X['check']=''
    if pred == df['OK/NG'][0]:
        X['check'] = 'OK'
    else:
        X['check'] = 'check'
    
    cols = [ 'TIME_PER_STRING(s)_mean',
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
    
    X[cols] = X[cols].round(2)
    return X