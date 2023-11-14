# -*- coding: utf-8 -*-
from fastapi import FastAPI,APIRouter
import pandas as pd
from autosoldering import pipeline2,pipeline_box2,pipeline_heat,accyracy
from postgreeDB import postgresProcess,insert
import json
from datetime import datetime
router = APIRouter()

@router.get("/AutoQualityPredictionSearch",tags=['AutoSoldering'],summary='AUTO 실시간 품질 예측 조회')
async def AutoQualityPredictionSearch():
    try:
     sql = f'''
      select  *
      from ss_ai.rtn_autosoldering_data trd 
      where to_char("TO_TIME" ,'yyyy-mm-dd') = to_char(now(),'yyyy-mm-dd')
      order by "TO_TIME"
            '''
     rs = postgresProcess.postQueryDataSet(sql)
     if rs["result"] == "ok":
         data = rs["data"] 
     else:
         data = ''
     return data

    except Exception as e:
     print("err...")
     return e

@router.post("/AutoprocessOptimal", tags=['AutoSoldering'], summary='AUTO 공정 최적값 조회 화면 조회')
async def AutoprocessOptimal(data:dict):
    try:
     pred,pred2 = pipeline2.target_optimization('./autosoldering/pkl/model/model_xgb_tps.pkl', './autosoldering/pkl/scaler/scaler_tps.gz', 
                                 './autosoldering/Shinsung_AutoSoldering_minmax table.xlsx')

     pred_data = pred.to_dict('records') #딕셔너리 변환 
     db_insert_data = {
        'model_version': 'model_xgb_tps.pkl',
        'scaler_version': 'scaler_tps.gz',
        'setting_file': 'Shinsung_AutoSoldering_minmax table.xlsx',
        '조회된 시점': datetime.today().strftime("%Y-%m-%d %H:%M:%S")
                  }
     db_insert_data.update(pred_data[0]) #데이터 합치기
     for d in [db_insert_data]:
        sql = insert.InsertQuery('rtn_opti_autosolder_data',d)    
     result = postgresProcess.postExecuteQuery(sql)
    #  insert 성공 
     if result['result']=='ok':
        return pred
     else :
        return []
    except Exception as e:
     print("err...")
     return e
    
@router.post("/AutoQualityHistoryList", tags=['AutoSoldering'],summary='AUTO 실시간 품질 이력 조회')
async def AutoQualityHistoryList(data:dict):
    try:
     sql = f'''
      select "OK/NG" ,"OK/NG_pred" ,to_char("TO_TIME",'YYYY-MM-DD') as "TIME"
      from ss_ai.rtn_autosoldering_data rjd  
      where to_char("TO_TIME",'yyyy-mm-dd')
      between '{data['startDate']}' and '{data['endDate']}'
      order by "TO_TIME"
            '''
     rs = postgresProcess.postQueryDataSet(sql)
     #데이터 조회
     if rs["result"] == "ok":
        df = pd.DataFrame(rs["data"])
        acc = accyracy.accuracy_tabber(df)
        data = acc.to_dict('records')
     else:
         data = ''
     return data
    except Exception as e:
     print("err...")
     return e
    
@router.post("/AutoTrendChart", tags=['AutoSoldering'], summary='AUTO trend chart')
async def AutoTrendChart(data:dict):
    try:
     sql = f'''
           select 
             "MAIN_Z-LEFT_mean",
             "MAIN_Z-MIDDLE_mean",
             "MAIN_Z-RIGHT_mean",
             "SUB1_CYCLE_TIME_mean",
             "SUB1_MAX_TEMP_mean",
             "SUB1_PV_TEMP_mean",
             "SUB2_CYCLE_TIME_mean",
             "SUB2_MAX_TEMP_mean",
             "SUB2_PV_TEMP_mean",
             "SUB3_CYCLE_TIME_mean",
             "SUB3_MAX_TEMP_mean",
             "SUB3_PV_TEMP_mean",
             "SUB4_CYCLE_TIME_mean",
             "SUB4_MAX_TEMP_mean",
             "SUB5_CYCLE_TIME_mean",
             "SUB5_MAX_TEMP_mean",
             "SUB6_CYCLE_TIME_mean",
             "SUB6_MAX_TEMP_mean"
           from "ss_ai".tmp_autosolder_relearning_data trd 
           where learning_to between date_trunc('week', '{data['date']}'::timestamp)- interval '8 day' 
           and date_trunc('week', '{data['date']}'::timestamp)- interval '1 day'  - interval '1 seconds'
           limit 1000;
            '''
     rs = postgresProcess.postQueryDataSet(sql)
 
     if rs["result"] == "ok":
         data = rs["data"] 
         df =pd.DataFrame(rs["data"])
        #  df = df.transpose() #행열변환
         data =df
     else:
         data = {}
     return data
    except Exception as e:
     print("err...")
     return e

@router.post("/AutolistBoxPlot", tags=['AutoSoldering'],summary='AUTO 박스 플롯')
async def AutolistBoxPlot():
    try:
    #  임시로 모든 데이터 가져오기
     sql = f'''select * from ss_ai.tmp_autosolder_relearning_data trd 
               '''
     #postgreeDB 저장된 마지막 데이터 가져오기
     rs = postgresProcess.postQueryDataSet(sql)
    # postgreeDB 저장된 시간 
     if rs["result"] == "ok":
         data = rs["data"] 
     else:
         data = ''
     df = pd.DataFrame(data)
     result = pipeline_box2.box_plot_params(df)
     return result
    except Exception as e:
     print("err...")
     return e

@router.post("/AutolistHeatMap", tags=['AutoSoldering'],summary='AUTO HeatMap')
async def AutolistHeatMap():
    try:
    #  임시로 모든 데이터 가져오기
     sql = f'''select * from ss_ai.tmp_autosolder_relearning_data trd 
               '''
     #postgreeDB 저장된 마지막 데이터 가져오기
     rs = postgresProcess.postQueryDataSet(sql)
    # postgreeDB 저장된 시간 
     if rs["result"] == "ok":
         data = rs["data"] 
     else:
         data = ''
     df = pd.DataFrame(data)
     result = pipeline_heat.get_heat_corr(df)
     return result
    except Exception as e:
     print("err...")
     return e


@router.post("/AutoDataSet", tags=['AutoSoldering'], summary='AUTO data 조회')
async def AutoDataSet(data:dict):
    try:
     sql = f'''
           select to_char("learning_to",'yyyy-mm-dd') as "일자" ,count(*) as "총 데이터 수",count(case when "OK/NG" ='OK' then 1 end) as "OK", count(case when "OK/NG" ='NG' then 1 end) as "NG" 
           from "ss_ai".tmp_autosolder_relearning_data rjd  
           where to_char("learning_to",'yyyy-mm-dd')
           between '{data['startDate']}' and '{data['endDate']}'
           group by to_char("learning_to",'yyyy-mm-dd')
            '''
     rs = postgresProcess.postQueryDataSet(sql)
 
     if rs["result"] == "ok":
         data = rs["data"] 
     else:
         data = ''
     return data
    except Exception as e:
     print("err...")
     return e
    
@router.post("/AutoSubDataSet", tags=['AutoSoldering'],summary='AUTO data 하단 그리드 조회')
async def AutoSubDataSet(data:dict):
    try:
     sql = f'''
           select *
           from "ss_ai".tmp_autosolder_relearning_data
           where to_char("learning_to",'yyyy-mm-dd') = '{data['date']}'
            '''
     rs = postgresProcess.postQueryDataSet(sql)
 
     if rs["result"] == "ok":
         data = rs["data"] 
     else:
         data = ''
     return data
    except Exception as e:
     print("err...")
     return e
    
