"""
python version = 3.8.17
xgboost version = 2.0.0
geneticalgorithm version = 1.0.2
"""


import pandas as pd
import numpy as np
import math
import pickle
import joblib
from geneticalgorithm import geneticalgorithm
import warnings


"""
신성이엔지 태버공정 공정최적화 파이프라인 함수

신성이엔지 시스템의 [공정최적값 조회 > 공정최적값 조회] 화면에서 태버공정의 양품생산을 위한 공정 변수 최적값을 도출함
(arg)    target_equip: 목표 설비명; string
         model_file: 품질판정 예측모델 파일명; str
         ohe_file: 인코더 파일명; str
         scaler_file: 스케일러 파일명; str
         stat_df: 변수별 최소최대값 표 파일명; str
         ok_prob: 양품을 에측할 확률 목표. default=0.99; float
(return) final_solution: 양품생산을 위한 공정 최적값; Dataframe
         target_repredicted: 도출된 최적값을 활용하여 재예측한 '양품(OK)' 예측 확률; float
"""


def target_optimization(target_equip, model_file, ohe_file, scaler_file, stat_df, ok_prob=0.99):
    # 품질판정 예측모델 불러오기
    model = pd.read_pickle(model_file)

    # 범주형 변수 인코더 불러오기
    ohe = joblib.load(ohe_file)

    # 데이터 표준화 스케일러 불러오기
    scaler = joblib.load(scaler_file)

    # 변수별 최소최대값 표 불러오기 - 최적값 서칭범위 설정에 필요
    df_stat = pd.read_excel(stat_df, index_col=0)

    # 공정최적화 분석변수 정의
    Xcols = ['TIME_PER_STRING(s)_mean', 
             'BOTTOMPLATE01_TEMP_mean', 'BOTTOMPLATE01_TEMP_std',
             'BOTTOMPLATE02_TEMP_mean', 'BOTTOMPLATE02_TEMP_std',
             'BOTTOMPLATE03_TEMP_mean', 'BOTTOMPLATE03_TEMP_std',
             'BOTTOMPLATE04_TEMP_mean', 'BOTTOMPLATE04_TEMP_std',
             'BOTTOMPLATE05_TEMP_mean', 'BOTTOMPLATE05_TEMP_std',
             'BOTTOMPLATE06_TEMP_mean', 'BOTTOMPLATE06_TEMP_std',
             'BOTTOMPLATE07_TEMP_mean', 'BOTTOMPLATE07_TEMP_std',
             'BOTTOMPLATE08_TEMP_mean', 'BOTTOMPLATE08_TEMP_std',
             'BOTTOMPLATE09_TEMP_mean', 'BOTTOMPLATE09_TEMP_std',
             'BOTTOMPLATE10_TEMP_mean', 'BOTTOMPLATE10_TEMP_std',
             'EQUIPNUM_TABBER01A', 'EQUIPNUM_TABBER01B', 'EQUIPNUM_TABBER02A',
             'EQUIPNUM_TABBER02B', 'EQUIPNUM_TABBER03A', 'EQUIPNUM_TABBER03B',
             'EQUIPNUM_TABBER04A', 'EQUIPNUM_TABBER04B']
    # 변수 개수
    dim = len(Xcols)

    # 유전 알고리즘을 사용하기 위해 독립변수를 변환하는 함수 정의
    # 0: 'TIME_PER_STRING(s)_mean',
    # 1: 'BOTTOMPLATE01_TEMP_mean',
    # 2: 'BOTTOMPLATE01_TEMP_std',
    # 3: 'BOTTOMPLATE02_TEMP_mean',
    # 4: 'BOTTOMPLATE02_TEMP_std',
    # 5: 'BOTTOMPLATE03_TEMP_mean',
    # 6: 'BOTTOMPLATE03_TEMP_std',
    # 7: 'BOTTOMPLATE04_TEMP_mean',
    # 8: 'BOTTOMPLATE04_TEMP_std',
    # 9: 'BOTTOMPLATE05_TEMP_mean',
    # 10: 'BOTTOMPLATE05_TEMP_std',
    # 11: 'BOTTOMPLATE06_TEMP_mean',
    # 12: 'BOTTOMPLATE06_TEMP_std',
    # 13: 'BOTTOMPLATE07_TEMP_mean',
    # 14: 'BOTTOMPLATE07_TEMP_std',
    # 15: 'BOTTOMPLATE08_TEMP_mean',
    # 16: 'BOTTOMPLATE08_TEMP_std',
    # 17: 'BOTTOMPLATE09_TEMP_mean',
    # 18: 'BOTTOMPLATE09_TEMP_std',
    # 19: 'BOTTOMPLATE10_TEMP_mean',
    # 20: 'BOTTOMPLATE10_TEMP_std',
    # 21: 'EQUIPNUM_TABBER01A',
    # 22: 'EQUIPNUM_TABBER01B',
    # 23: 'EQUIPNUM_TABBER02A',
    # 24: 'EQUIPNUM_TABBER02B',
    # 25: 'EQUIPNUM_TABBER03A',
    # 26: 'EQUIPNUM_TABBER03B',
    # 27: 'EQUIPNUM_TABBER04A',
    # 28 'EQUIPNUM_TABBER04B'    
    def input_conversion(x_input):
        conversion = [float(x_input[0]), float(x_input[1]),
                      float(x_input[2]), float(x_input[3]),
                      float(x_input[4]), float(x_input[5]),
                      float(x_input[6]), float(x_input[7]),
                      float(x_input[8]), float(x_input[9]),
                      float(x_input[10]), float(x_input[11]),
                      float(x_input[12]), float(x_input[13]),
                      float(x_input[14]), float(x_input[15]),
                      float(x_input[16]), float(x_input[17]),
                      float(x_input[18]), float(x_input[19]),
                      float(x_input[20]), 
                      int(x_input[21]),
                      int(x_input[22]), int(x_input[23]),
                      int(x_input[24]), int(x_input[25]),
                      int(x_input[26]), int(x_input[27]),
                      int(x_input[28])]
        return conversion

    # 원핫인코더를 통해 설비명 변환
    a,b,c,d,m,n,o,p = map(int, ohe.transform(pd.DataFrame(data=[target_equip], columns=['EQUIPNUM'])).flatten())

    # 최적값을 찾고자 하는 변수의 서칭범위 설정
    varbound = np.array([#[df_stat.loc['min', 'TIME_PER_STRING(s)_mean'], df_stat.loc['max', 'TIME_PER_STRING(s)_mean']],
                         [df_stat.loc['min', 'TIME_PER_STRING(s)_mean'], 60],   # 최대 1분으로 제한
                         [df_stat.loc['min', 'BOTTOMPLATE01_TEMP_mean'], df_stat.loc['max', 'BOTTOMPLATE01_TEMP_mean']], 
                         [df_stat.loc['min', 'BOTTOMPLATE01_TEMP_std']+1, df_stat.loc['max', 'BOTTOMPLATE01_TEMP_std']], 
                         [df_stat.loc['min', 'BOTTOMPLATE02_TEMP_mean'], df_stat.loc['max', 'BOTTOMPLATE02_TEMP_mean']],
                         [df_stat.loc['min', 'BOTTOMPLATE02_TEMP_std']+1, df_stat.loc['max', 'BOTTOMPLATE02_TEMP_std']],
                         [df_stat.loc['min', 'BOTTOMPLATE03_TEMP_mean'], df_stat.loc['max', 'BOTTOMPLATE03_TEMP_mean']], 
                         [df_stat.loc['min', 'BOTTOMPLATE03_TEMP_std']+1, df_stat.loc['max', 'BOTTOMPLATE03_TEMP_std']], 
                         [df_stat.loc['min', 'BOTTOMPLATE04_TEMP_mean'], df_stat.loc['max', 'BOTTOMPLATE04_TEMP_mean']],
                         [df_stat.loc['min', 'BOTTOMPLATE04_TEMP_std']+1, df_stat.loc['max', 'BOTTOMPLATE04_TEMP_std']],
                         [df_stat.loc['min', 'BOTTOMPLATE05_TEMP_mean'], df_stat.loc['max', 'BOTTOMPLATE05_TEMP_mean']],
                         [df_stat.loc['min', 'BOTTOMPLATE05_TEMP_std']+1, df_stat.loc['max', 'BOTTOMPLATE05_TEMP_std']],
                         [df_stat.loc['min', 'BOTTOMPLATE06_TEMP_mean'], df_stat.loc['max', 'BOTTOMPLATE06_TEMP_mean']], 
                         [df_stat.loc['min', 'BOTTOMPLATE06_TEMP_std']+1, df_stat.loc['max', 'BOTTOMPLATE06_TEMP_std']], 
                         [df_stat.loc['min', 'BOTTOMPLATE07_TEMP_mean'], df_stat.loc['max', 'BOTTOMPLATE07_TEMP_mean']],
                         [df_stat.loc['min', 'BOTTOMPLATE07_TEMP_std']+1, df_stat.loc['max', 'BOTTOMPLATE07_TEMP_std']],
                         [df_stat.loc['min', 'BOTTOMPLATE08_TEMP_mean'], df_stat.loc['max', 'BOTTOMPLATE08_TEMP_mean']], 
                         [df_stat.loc['min', 'BOTTOMPLATE08_TEMP_std']+1, df_stat.loc['max', 'BOTTOMPLATE08_TEMP_std']], 
                         [df_stat.loc['min', 'BOTTOMPLATE09_TEMP_mean'], df_stat.loc['max', 'BOTTOMPLATE09_TEMP_mean']],
                         [df_stat.loc['min', 'BOTTOMPLATE09_TEMP_std']+1, df_stat.loc['max', 'BOTTOMPLATE09_TEMP_std']],
                         [df_stat.loc['min', 'BOTTOMPLATE10_TEMP_mean'], df_stat.loc['max', 'BOTTOMPLATE10_TEMP_mean']],
                         [df_stat.loc['min', 'BOTTOMPLATE10_TEMP_std']+1, df_stat.loc['max', 'BOTTOMPLATE10_TEMP_std']],
                         [a,a],    # 제한조건. 설비명은 0,1로 받음    
                         [b,b],
                         [c,c],
                         [d,d],
                         [m,m],
                         [n,n],
                         [o,o],
                         [p,p]
                        ]) 

    # 목표 판정값(OK)을 얻기 위한 최적 공정조건 도출
    def object_function_target(x_input, target_model=model):
        input_converted = input_conversion(x_input)
        input_converted = np.array(input_converted).reshape(1, -1)
        input_scaled = scaler.transform(input_converted)  
        prediction = target_model.predict_proba(input_scaled)          
        target = ok_prob          # 품질판정 'OK'를 예측할 확률 목표
        return math.log(abs(target - prediction[:,1]))    #ok는 두번째에 있는 값

    # 유전 알고리즘 파라미터 정의
    algorithm_param = {'max_num_iteration': 500,     # 진화(연산) 횟수
                       'population_size': 200,       # 초기 세대(generation)의 개체수(population)
                       'mutation_probability': 0.2,  # 다음 세대의 몇 %를 변이로 채울 것인지 결정
                       'elit_ratio': 0.01,           # 이전 세대의 가장 뛰어난 해의 몇 %를 가져올 것인지 결정
                       'crossover_probability': 0.5, # 이전 세대와 현 세대를 몇 % 교차할 것인지 결정
                       'parents_portion': 0.3,       # 자식 세대가 부모 세대로부터 얼마나 가져오는지 결정
                       'crossover_type': 'uniform',
                       'max_iteration_without_improv': None}   # 지정한 횟수만큼 연산이 없으면 정지. None: 정지시키지 않음

    # 유전 알고리즘 정의
    model_ga_target = geneticalgorithm(function=object_function_target,
                                       dimension=dim,            # 변수 개수
                                       variable_type='real',     # 타깃 변수(ok_prob)가 실수
                                       variable_boundaries=varbound,
                                       algorithm_parameters=algorithm_param)

    # 유전 알고리즘 실행
    warnings.filterwarnings(action='ignore')     # 경고문구 제거 설정 
    model_ga_target.run()

    # 최종 솔루션
    # convergence_target = model_ga_target.report      # iteration 동안 converge 되는 과정
    solution_target = model_ga_target.output_dict 
    
    # 최종 솔루션을 보기 쉽게 표 형태로
    ga_solution = input_conversion(solution_target['variable'])
    ga_solution = np.array(ga_solution).reshape(1, -1)
    ga_solution_df = pd.DataFrame(ga_solution, columns=Xcols)   #Xcols has 'encoded' names

    # one-hot-encoded 설비명 역변환
    final_solution = ga_solution_df.copy()
    equipnum_in_ohe = final_solution[ohe.get_feature_names_out()]                    #[0,0,0,0,0,0,0,0] 형태의 설비명  
    final_solution['EQUIPNUM'] = ohe.inverse_transform(equipnum_in_ohe).flatten()    #TABBER00X 형태의 설비명
    final_solution.drop(ohe.get_feature_names_out(), axis=1, inplace=True)           #원핫인코더 변환명으로 된 컬럼들 모두 삭제
   
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
    
    final_solution[cols] = final_solution[cols].round(2)    
    
    # 위 최적의 해를 사용하여 'OK' 판정 확률 재예측
    # prediction = model.predict_proba(ga_solution_df)
    prediction = model.predict_proba(scaler.transform(ga_solution_df))
    target_repredicted = prediction[:,1]

    return final_solution, target_repredicted