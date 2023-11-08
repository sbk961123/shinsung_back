# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter
import pandas as pd
import uvicorn
import json
from tabber import pipeline2,pipeline_box
from postgreeDB import postgresProcess
import json
app = FastAPI()
origins = ["*"]

# MiddleWare 설정. CORS Error 방지.

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#실시간 품질 예측 조회
@app.post("/QualityPredictionSearch")
async def QualityPredictionSearch(data:dict):
    try:
     sql = f'''
      select  *
      from ss_ai.rtn_judge_data trd 
      where "EQUIPNUM" = '{data['facility']}'
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

#공정 최적값 조회 화면 조회시
@app.post("/processOptimal")
async def processOptimal(data:dict):
    try:
     pred,pred2 = pipeline2.target_optimization({data['facility']},'./tabber/pkl/model/model_xgb_tps.pkl',  './tabber/pkl/ohe/ohe_tps.gz', './tabber/pkl/scaler/scaler_tps.gz', 
                                 './tabber/Shinsung_Tabber_minmax table.xlsx')
     return pred
    except Exception as e:
     print("err...")
     return e
    
#실시간 품질 이력 조회
@app.post("/QualityHistoryList")
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
    
#trend chart
@app.post("/TrendChart")
async def TrendChart(data:dict):
    try:
     sql = f'''
           select *
           from ss_ai.tmp_relearning_data trd 
           where "EQUIPNUM" ='{data['facility']}'
           and learning_to 
           between date_trunc('week', '{data['date']}'::timestamp)- interval '8 day' 
           and date_trunc('week', '{data['date']}'::timestamp)- interval '1 day'  - interval '1 seconds';
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

#박스 플롯
@app.post("/listBoxPlot")
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
     print(df)
     result = pipeline_box.box_plot_params(df)
     return result
    except Exception as e:
     print("err...")
     return e

#data 조회
@app.post("/DataSet")
async def DataSet(data:dict):
    try:
     sql = f'''
           select "EQUIPNUM" as "설비", to_char("learning_to",'yyyy-mm-dd') as "일자" ,count(*) as "총 데이터 수",count(case when "OK/NG" ='OK' then 1 end) as "OK", count(case when "OK/NG" ='NG' then 1 end) as "NG" from "ss_ai".tmp_relearning_data rjd  
           where to_char("learning_to",'yyyy-mm-dd')
           between '{data['startDate']}' and '{data['endDate']}'
           group by to_char("learning_to",'yyyy-mm-dd'),"EQUIPNUM" 
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
    
#data 하단 그리드 조회
@app.post("/SubDataSet")
async def SubDataSet(data:dict):
    try:
     sql = f'''
           select *
           from "ss_ai".tmp_relearning_data
           where to_char("learning_to",'yyyy-mm-dd') = '{data['date']}'
           and "EQUIPNUM" = '{data['facility']}'
           limit 100
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
    

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
