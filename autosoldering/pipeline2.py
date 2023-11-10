"""
python version = 3.8.17
xgboost version = 2.0.0
geneticalgorithm version = 1.0.2
"""


from aifc import Aifc_read
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


def target_optimization(model_file, scaler_file, stat_df, ok_prob=0.99):
    # 품질판정 예측모델 불러오기
    model = pd.read_pickle(model_file)

    # 데이터 표준화 스케일러 불러오기
    scaler = joblib.load(scaler_file)

    # 변수별 최소최대값 표 불러오기 - 최적값 서칭범위 설정에 필요
    df_stat = pd.read_excel(stat_df, index_col=0)

    # 공정최적화 분석변수 정의
    Xcols = ['MAIN_Z-LEFT_mean', 'MAIN_Z-LEFT_std', 'MAIN_Z-MIDDLE_mean',
            'MAIN_Z-MIDDLE_std', 'MAIN_Z-RIGHT_mean', 'MAIN_Z-RIGHT_std',
            'SUB1_CYCLE_TIME_mean', 'SUB1_CYCLE_TIME_std', 'SUB1_MAX_TEMP_mean',
            'SUB1_MAX_TEMP_std', 'SUB1_PV_TEMP_mean', 'SUB1_PV_TEMP_std',
            'SUB2_CYCLE_TIME_mean', 'SUB2_MAX_TEMP_mean', 'SUB2_MAX_TEMP_std',
            'SUB2_PV_TEMP_mean', 'SUB2_PV_TEMP_std', 'SUB3_CYCLE_TIME_mean',
            'SUB3_MAX_TEMP_mean', 'SUB3_MAX_TEMP_std', 'SUB3_PV_TEMP_mean',
            'SUB3_PV_TEMP_std', 'SUB4_CYCLE_TIME_mean', 'SUB4_MAX_TEMP_mean',
            'SUB4_MAX_TEMP_std', 'SUB4_PV_TEMP_std', 'SUB5_CYCLE_TIME_mean',
            'SUB5_MAX_TEMP_mean', 'SUB5_MAX_TEMP_std', 'SUB6_CYCLE_TIME_mean',
            'SUB6_MAX_TEMP_mean', 'SUB6_MAX_TEMP_std']
    # 변수 개수
    dim = len(Xcols)
    # 유전 알고리즘을 사용하기 위해 독립변수를 변환하는 함수 정의
    
    # 0 : 'MAIN_Z-LEFT_mean',
    # 1 : 'MAIN_Z-LEFT_std', 
    # 2 : 'MAIN_Z-MIDDLE_mean',
    # 3 : 'MAIN_Z-MIDDLE_std',
    # 4 : 'MAIN_Z-RIGHT_mean', 
    # 5 : 'MAIN_Z-RIGHT_std',
    # 6 : 'SUB1_CYCLE_TIME_mean', 
    # 7 : 'SUB1_CYCLE_TIME_std', 
    # 8 : 'SUB1_MAX_TEMP_mean',
    # 9 : 'SUB1_MAX_TEMP_std', 
    # 10 : 'SUB1_PV_TEMP_mean', 
    # 11 : 'SUB1_PV_TEMP_std',
    # 12 : 'SUB2_CYCLE_TIME_mean', 
    # 13 : 'SUB2_MAX_TEMP_mean', 
    # 14 : 'SUB2_MAX_TEMP_std',
    # 15 : 'SUB2_PV_TEMP_mean', 
    # 16 : 'SUB2_PV_TEMP_std', 
    # 17 : 'SUB3_CYCLE_TIME_mean',
    # 18 : 'SUB3_MAX_TEMP_mean', 
    # 19 : 'SUB3_MAX_TEMP_std', 
    # 20 : 'SUB3_PV_TEMP_mean',
    # 21 : 'SUB3_PV_TEMP_std', 
    # 22 : 'SUB4_CYCLE_TIME_mean', 
    # 23 : 'SUB4_MAX_TEMP_mean',
    # 24 : 'SUB4_MAX_TEMP_std', 
    # 25 : 'SUB4_PV_TEMP_std', 
    # 26 : 'SUB5_CYCLE_TIME_mean',
    # 27 : 'SUB5_MAX_TEMP_mean', 
    # 28 : 'SUB5_MAX_TEMP_std',
    # 29 : 'SUB6_CYCLE_TIME_mean',
    # 30 : 'SUB6_MAX_TEMP_mean', 
    # 31 : 'SUB6_MAX_TEMP_std'   
       
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
                      float(x_input[20]), float(x_input[21]),
                      float(x_input[22]), float(x_input[23]),
                      float(x_input[24]), float(x_input[25]),
                      float(x_input[26]), float(x_input[27]),
                      float(x_input[28]), float(x_input[29]),
                      float(x_input[30]), float(x_input[31])
                      ]
        return conversion

  # 최적값을 찾고자 하는 변수의 서칭범위 설정
    varbound = np.array([
    
                         [df_stat.loc['min', 'MAIN_Z-LEFT_mean'], df_stat.loc['max', 'MAIN_Z-LEFT_mean']], 
                         [df_stat.loc['min', 'MAIN_Z-LEFT_std'], df_stat.loc['max', 'MAIN_Z-LEFT_std']],
                         [df_stat.loc['min', 'MAIN_Z-MIDDLE_mean'], df_stat.loc['max', 'MAIN_Z-MIDDLE_mean']],
                         [df_stat.loc['min', 'MAIN_Z-MIDDLE_std'], df_stat.loc['max', 'MAIN_Z-MIDDLE_std']],
                         [df_stat.loc['min', 'MAIN_Z-RIGHT_mean'], df_stat.loc['max', 'MAIN_Z-RIGHT_mean']],
                         [df_stat.loc['min', 'MAIN_Z-RIGHT_std'], df_stat.loc['max', 'MAIN_Z-RIGHT_std']],
                         [df_stat.loc['min', 'SUB1_CYCLE_TIME_mean'], df_stat.loc['max', 'SUB1_CYCLE_TIME_mean']],
                         [df_stat.loc['min', 'SUB1_CYCLE_TIME_std'], df_stat.loc['max', 'SUB1_CYCLE_TIME_std']],
                         [df_stat.loc['min', 'SUB1_MAX_TEMP_mean'], df_stat.loc['max', 'SUB1_MAX_TEMP_mean']],
                         [df_stat.loc['min', 'SUB1_MAX_TEMP_std'], df_stat.loc['max', 'SUB1_MAX_TEMP_std']],
                         [df_stat.loc['min', 'SUB1_PV_TEMP_mean'], df_stat.loc['max', 'SUB1_PV_TEMP_mean']],
                         [df_stat.loc['min', 'SUB1_PV_TEMP_std'], df_stat.loc['max', 'SUB1_PV_TEMP_std']],
                         [df_stat.loc['min', 'SUB2_CYCLE_TIME_mean'], df_stat.loc['max', 'SUB2_CYCLE_TIME_mean']],
                         [df_stat.loc['min', 'SUB2_MAX_TEMP_mean'], df_stat.loc['max', 'SUB2_MAX_TEMP_mean']],
                         [df_stat.loc['min', 'SUB2_MAX_TEMP_std'], df_stat.loc['max', 'SUB2_MAX_TEMP_std']],
                         [df_stat.loc['min', 'SUB2_PV_TEMP_mean'], df_stat.loc['max', 'SUB2_PV_TEMP_mean']],
                         [df_stat.loc['min', 'SUB2_PV_TEMP_std'], df_stat.loc['max', 'SUB2_PV_TEMP_std']],
                         [df_stat.loc['min', 'SUB3_CYCLE_TIME_mean'], df_stat.loc['max', 'SUB3_CYCLE_TIME_mean']],
                         [df_stat.loc['min', 'SUB3_MAX_TEMP_mean'], df_stat.loc['max', 'SUB3_MAX_TEMP_mean']],
                         [df_stat.loc['min', 'SUB3_MAX_TEMP_std'], df_stat.loc['max', 'SUB3_MAX_TEMP_std']],
                         [df_stat.loc['min', 'SUB3_PV_TEMP_mean'], df_stat.loc['max', 'SUB3_PV_TEMP_mean']],
                         [df_stat.loc['min', 'SUB3_PV_TEMP_std'], df_stat.loc['max', 'SUB3_PV_TEMP_std']],
                         [df_stat.loc['min', 'SUB4_CYCLE_TIME_mean'], df_stat.loc['max', 'SUB4_CYCLE_TIME_mean']],
                         [df_stat.loc['min', 'SUB4_MAX_TEMP_mean'], df_stat.loc['max', 'SUB4_MAX_TEMP_mean']],
                         [df_stat.loc['min', 'SUB4_MAX_TEMP_std'], df_stat.loc['max', 'SUB4_MAX_TEMP_std']],
                         [df_stat.loc['min', 'SUB4_PV_TEMP_std'], df_stat.loc['max', 'SUB4_PV_TEMP_std']],
                         [df_stat.loc['min', 'SUB5_CYCLE_TIME_mean'], df_stat.loc['max', 'SUB5_CYCLE_TIME_mean']],
                         [df_stat.loc['min', 'SUB5_MAX_TEMP_mean'], df_stat.loc['max', 'SUB5_MAX_TEMP_mean']],
                         [df_stat.loc['min', 'SUB5_MAX_TEMP_std'], df_stat.loc['max', 'SUB5_MAX_TEMP_std']],
                         [df_stat.loc['min', 'SUB6_CYCLE_TIME_mean'], df_stat.loc['max', 'SUB6_CYCLE_TIME_mean']],
                         [df_stat.loc['min', 'SUB6_MAX_TEMP_mean'], df_stat.loc['max', 'SUB6_MAX_TEMP_mean']],
                         [df_stat.loc['min', 'SUB6_MAX_TEMP_std'], df_stat.loc['max', 'SUB6_MAX_TEMP_std']],
                
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


    final_solution[Xcols] = final_solution[Xcols].round(2)    




    # 위 최적의 해를 사용하여 'OK' 판정 확률 재예측
    # prediction = model.predict_proba(ga_solution_df)
    prediction = model.predict_proba(scaler.transform(ga_solution_df))
    target_repredicted = prediction[:,1]

    return final_solution, target_repredicted