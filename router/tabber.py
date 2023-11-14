# -*- coding: utf-8 -*-
from fastapi import FastAPI,APIRouter
import pandas as pd
from tabber import pipeline2,pipeline_box,pipeline_heat
from postgreeDB import postgresProcess,insert
import json
from datetime import datetime
router = APIRouter()

@router.post("/QualityPredictionSearch",tags=['TABBER'],summary='실시간 품질 예측 조회')
async def QualityPredictionSearch(data:dict):
    try:
     sql = f'''
      select  *
      from ss_ai.rtn_judge_data trd 
      where "EQUIPNUM" = '{data['facility']}'
      and to_char("TO_TIME" ,'yyyy-mm-dd') = to_char(now(),'yyyy-mm-dd')
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

@router.post("/processOptimal", tags=['TABBER'], summary='공정 최적값 조회 화면 조회')
async def processOptimal(data:dict):
    try:
     pred,pred2 = pipeline2.target_optimization({data['facility']},'./tabber/pkl/model/model_xgb_tps.pkl',  './tabber/pkl/ohe/ohe_tps.gz', './tabber/pkl/scaler/scaler_tps.gz', 
                                 './tabber/Shinsung_Tabber_minmax table.xlsx')
     pred_data = pred.to_dict('records') #딕셔너리 변환 
     db_insert_data = {
        'model_version': 'model_xgb_tps.pkl',
        'ohe_version': 'ohe_tps.gz',
        'scaler_version': 'scaler_tps.gz',
        'setting_file': 'Shinsung_Tabber_minmax table.xlsx',
        'learning_to': datetime.today().strftime("%Y-%m-%d %H:%M:%S")
                  }
     db_insert_data.update(pred_data[0]) #데이터 합치기
     for d in [db_insert_data]:
        sql = insert.InsertQuery('rtn_opti_data',d)      
     result = postgresProcess.postExecuteQuery(sql)
     #insert 성공 
     if result['result']=='ok':
        return pred
     else :
        return result
    except Exception as e:
     print("err...")
     return e
    
@router.post("/QualityHistoryList", tags=['TABBER'],summary='실시간 품질 이력 조회')
async def QualityHistoryList(data:dict):
    try:
     sql = f'''
      select to_char("TO_TIME",'yyyy-mm-dd') as "일자" ,count(*) as "전체예측건수",count(case when "OK/NG" ='NG' then 1 end) as "PLC NG" ,count(case when "OK/NG_pred" ='NG' then 1 end) as "NG 예측" 
      from ss_ai.rtn_judge_data rjd  
      where to_char("TO_TIME",'yyyy-mm-dd')
      between '{data['startDate']}' and '{data['endDate']}'
      and "EQUIPNUM" = '{data['facility']}'
      group by to_char("TO_TIME",'yyyy-mm-dd')
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
    
@router.post("/TrendChart", tags=['TABBER'], summary='trend chart')
async def TrendChart(data:dict):
    try:
     sql = f'''
           select *
           from ss_ai.tmp_relearning_data trd 
           where "EQUIPNUM" ='{data['facility']}'
           and learning_to 
           between date_trunc('week', '{data['date']}'::timestamp)- interval '8 day' 
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

@router.post("/listBoxPlot",  tags=['TABBER'],summary='박스 플롯')
async def listBoxPlot():
    try:
    #  임시로 모든 데이터 가져오기
     sql = f'''select * from ss_ai.tmp_relearning_data trd 
               '''
     #postgreeDB 저장된 마지막 데이터 가져오기
     rs = postgresProcess.postQueryDataSet(sql)
    # postgreeDB 저장된 시간 
     if rs["result"] == "ok":
         data = rs["data"] 
     else:
         data = ''
     df = pd.DataFrame(data)
     result = pipeline_box.box_plot_params(df)
     return result
    except Exception as e:
     print("err...")
     return e

@router.post("/listHeatMap", tags=['TABBER'],summary='HeatMap')
async def listHeatMap():
    try:
    #  임시로 모든 데이터 가져오기
     sql = f'''select * from ss_ai.tmp_relearning_data trd 
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


@router.post("/DataSet", tags=['TABBER'], summary='data 조회')
async def DataSet(data:dict):
    try:
     sql = f'''
           select to_char("learning_to",'yyyy-mm-dd') as "일자" ,count(*) as "총 데이터 수",count(case when "OK/NG" ='OK' then 1 end) as "OK", count(case when "OK/NG" ='NG' then 1 end) as "NG" 
           from "ss_ai".tmp_relearning_data rjd  
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
    
@router.post("/SubDataSet", tags=['TABBER'],summary='data 하단 그리드 조회')
async def SubDataSet(data:dict):
    try:
     sql = f'''
           select *
           from "ss_ai".tmp_relearning_data
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
    
