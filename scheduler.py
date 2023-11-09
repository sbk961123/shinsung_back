import pandas as pd
import uvicorn
import json
from tabber import pipeline
import os
import machbase
from postgreeDB import postgresProcess,insert
import psycopg2
import time
from config.config import db, DEBUG
import schedule

def timescaleDB():
    conn = psycopg2.connect(host = db['host'], port = db['port'], dbname = db['database'], user = db['id'], password = db['pw'])
    return conn

def scheduler():
   TABBER('TABBER01A')
   TABBER('TABBER01B')
   TABBER('TABBER02A')
   TABBER('TABBER02B')
   TABBER('TABBER03A')
   TABBER('TABBER03B')
   TABBER('TABBER04A')
   TABBER('TABBER04B')

def aiLearing(data):
     df = pd.DataFrame(data)
     #데이터 컬럼명 변경
     df = df.rename(columns={'OK_NG':'OK/NG'})
     df = df.rename(columns={'TIME_PER_STRING(S)':'TIME_PER_STRING(s)'})
     df['TIME_PER_STRING(s)'] = pd.to_numeric(df['TIME_PER_STRING(s)'], errors='coerce')
   
     #float 형태 변환
     for i in df.columns:
      if i.find('TEMP') == -1 :
         continue
      if df[i].dtypes == object:
         df[i] = pd.to_numeric(df[i], errors='coerce')
 
     try:
      pred = pipeline.quality_predict(df)
      for i in pred.columns:
           # 필요없는 데이터 삭제 
         if i.find('TABBER') != -1 :
            pred = pred.drop(columns=[i])
            #시간 자르기
         if i.find('_TIME') != -1 :
            pred[i] = pred[i].str.slice(0,19)+"."+pred[i].str.slice(20,23)
 
      db_insert_data = pred.to_dict('records')
      sql = ''
      #insert 구문 생성 
      for d in db_insert_data:
         sql = insert.InsertQuery('rtn_judge_data',d)
      #db insert
      result = postgresProcess.postExecuteQuery(sql)
      return result
     except Exception as e:
      print(e,'err')
      return e

def TABBER(id):
     #마크베이스 가장 최신 판정 데이터 가져오기
     data = machbase.selectNowData(id) 
     sql = f'''select jd."EQUIPNUM" ,jd."TO_TIME"  from "ss_ai".rtn_judge_data jd 
               where "EQUIPNUM" ='{id}'
               order by "TO_TIME" desc 
               limit 1'''
     #postgreeDB 저장된 마지막 데이터 가져오기
     pstData = postgresProcess.postQueryDataSet(sql)

     #postgreeDB 저장된 시간 
     if pstData["result"] == "ok":
         pstTime = pstData["data"][0]['TO_TIME'][0:19] #yyyy-mm-dd hh:mm:ss 자르기
     else:
         pstTime = ''
     #저장된 데이터와 실데이터 다를 때 분석
     if data[0]['TO_TIME'][0:19]==pstTime:
        return
     else :
        result = aiLearing(data)
        return result


   
scheduler()

#실행주기 1초
schedule.every(1).seconds.do(scheduler)

#스케쥴 시작
while True:
    schedule.run_pending()
    time.sleep(1)