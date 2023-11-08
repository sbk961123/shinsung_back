import json
from fastapi.responses import JSONResponse
import psycopg2
from config.config import db, DEBUG
from postgreeDB.convertTools import NoneToEmptyJSON, convert_null_to_blank

#커넥션 타임 일단 7초
CONNECTION_TIMEOUT = 7
#디버그1이면 출력(오류제외), 개별설정을 위해변수처리
debugM = DEBUG["MODE"]

#options = '-c timezone=Asia/Seoul', 
def timescaleDB():
    conn = psycopg2.connect(host = db['host'], port = db['port'], dbname = db['database'], user = db['id'], password = db['pw'], options = f"-c timezone=Asia/Seoul", connect_timeout=CONNECTION_TIMEOUT)
    return conn

def timescaleDB2(ip, port, id, pw, database):
    conn = psycopg2.connect(host = ip, port = port, dbname = database, user = id, password = pw, options = f"-c timezone=Asia/Seoul", connect_timeout=CONNECTION_TIMEOUT)
    return conn

# 연결할 DB 상태확인
def postDBCheckEvent(dbinfo):
    
    try:
        sql = f"SELECT 'ONLINE' as status FROM pg_catalog.pg_database WHERE datname='{dbinfo['database']}'"
        
        
        conn = timescaleDB2(dbinfo["ip"], dbinfo["port"], dbinfo["id"], dbinfo["pw"], dbinfo["database"])

        rst = postQueryDataOne(sql, conn)

        if debugM == 1:
            print(f"{sql}\n\nSuccess")  

        result = rst["data"]

    except Exception as e:
        result = "데이터베이스 연결 상태 오류 : " + e
        print("데이터베이스 연결상태 오류 : ", e)
        print("=" * 150)
    finally:
        conn.close()
        return result
    
# 연결할 DB 모든테이블 조회 - 보류
def postgresqlDBAllTable(dbinfo, conn = None, autoCommit = True):
    
    rstData = { "result" : "ok", "msg" : f"정상" , "data" : ""}

    sql = f'''SELECT table_schema ||'.'|| table_name as id, table_schema ||'.' ||table_name as text 
                from INFORMATION_SCHEMA.TABLES 
                where table_catalog = '{dbinfo["database"]}'
                order by table_catalog, table_schema, table_name;'''
    try:

        rst = exPostQueryDataSet(dbinfo, sql)

        if rst["result"]=="ok":
            result=rst["data"]
            
        else:
            result = []
    except Exception as e:
        result = []
    finally:
        return result


## postgresql 쿼리 실행
def exPostExecuteQuery( dbinfo, qry, postConn = None , autoCommit = True ):
    if postConn is None:
        postConn = timescaleDB2(dbinfo["ip"], dbinfo["port"], dbinfo["id"], dbinfo["pw"], dbinfo["database"])
    return postExecuteQuery( qry, postConn, autoCommit )

## postgresql 쿼리 실행
def postExecuteQuery( qry, postConn = None , autoCommit = True ):
    rstData = { "result" : "ok", "msg" : f"정상" , "data" : []}

    try:
        if postConn is None:
            postConn = timescaleDB()
        
        postCur = postConn.cursor()
        
        if debugM == 1:
            print("* SQL : ", qry)
            print("*"*30)

        postCur.execute(qry)
                
        if (autoCommit):
            postConn.commit()

        rstData = {"result" : "ok", "msg" : "처리 완료"}
        if debugM == 1:
            print(rstData)
            print("=" * 150)
    except Exception as e:
        print(f'PostSQL Execute Query Failed: {e}')
        print("* Execute : ", qry)
        print("=" * 150)
        rstData = { "result" : "error", "msg" : f"오류 : {e}"}
        if (autoCommit):
            postConn.rollback()
    finally:
        if (autoCommit): 
            postConn.close()
        
        postCur.close()
        return rstData
    
## 프로시저 실행    
def exPostCallProc( dbinfo, qry, parameters= None, postConn = None , autoCommit = True ):
    if postConn is None:
        postConn = timescaleDB2(dbinfo["ip"], dbinfo["port"], dbinfo["id"], dbinfo["pw"], dbinfo["database"])
    return postCallProc( qry, parameters, postConn , autoCommit)    

## 프로시저 실행
def postCallProc( qry, parameters= None, postConn = None , autoCommit = True ):
    rstData = { "result" : "ok", "msg" : f"정상" , "data" : []}

    try:
        if postConn is None:
            postConn = timescaleDB()
        
        postCur = postConn.cursor()
        
        if (parameters is None):
            if debugM == 1:
                print("* Sql Proc : ", qry )
                print("*"*30)
            postCur.callproc(qry )
        else:
            if debugM == 1:
                print(qry, parameters )
            postCur.callproc(qry, parameters )
        
        result = postCur.fetchone()[0]

        #서버성능때문에 출력 최소
        if debugM == 1:
            print(result)#json.dumps(result, indent=4))
                
        if (autoCommit):
            postConn.commit()

        rstData = {"result" : "ok", "msg" : "DB 작업 완료", "data" : result}
    
    except Exception as e:
        print(f'PostSQL CallProc Query Failed: {e}')
        print("* Sql Proc : ", qry )
        print("=" * 150)
        rstData = { "result" : "error", "msg" : f"오류 : {e}" , "data" : ""}
        if (autoCommit):
            postConn.rollback()
    finally:
        if (autoCommit): 
            postConn.close()
        
        postCur.close()
        return rstData

## postgresql 다중 여러행
def exPostQueryDataSet( dbinfo, qry, postConn = None , autoCommit = True ):
    if postConn is None:
        postConn = timescaleDB2(dbinfo["ip"], dbinfo["port"], dbinfo["id"], dbinfo["pw"], dbinfo["database"])
    return postQueryDataSet( qry, postConn , autoCommit)   
  
## postgresql 다중 여러행
def postQueryDataSet( qry , postConn = None, autoCommit = True ):
    rstData = { "result" : "ok", "msg" : f"정상"}
    data = []

    try:
        if postConn is None:
            postConn = timescaleDB()
        postCur = postConn.cursor()
        
        if debugM == 1:
            print("* Qry : ", qry)
            print("=" * 150)

        postCur.execute(qry)
        rows = postCur.fetchall()
        
        columns = [column[0] for column in postCur.description]
        for row in rows:
            data.append(dict(zip(columns,row)))

        if not data:
            rstData = {"result" : "nodata", "msg" : f"조회 데이터가 존재하지 않습니다." , "data" : [] } 
            return rstData

        if debugM == 1:
            print ("* Data size : ", len(data))
                        
        if (not (data is None)):
            datas = json.dumps(data, default=str, indent=4, ensure_ascii=False)
            
            if debugM == 1:
                #print("* Dataset : ", datas)
                print("=" * 150)
            jsonDatas = json.loads(datas)
            jsonDatas = convert_null_to_blank(jsonDatas)
            # print("jsonDatas : ", jsonDatas)
            # datas = json.dumps(data, default=str, ensure_ascii=False)
        # print (jsonDatas)
        if (autoCommit):
            postConn.commit()

        rstData = {"result" : "ok", "msg" : "처리 완료", "data" : jsonDatas}
    
    except Exception as e:
        print(f'PostSQL DataSet Query Failed: {e}')
        print("* Qry : ", qry)
        print("=" * 150)
        rstData = { "result" : "error", "msg" : f"오류 : {e}" , "data" : []}
        if (autoCommit):
            postConn.rollback()
    finally:
        if (autoCommit): 
            postConn.close()

        postCur.close()
        return rstData
    
## postgresql 단일값
def exPostQueryDataOne( dbinfo, qry, postConn = None , autoCommit = True ):
    if postConn is None:
        postConn = timescaleDB2(dbinfo["ip"], dbinfo["port"], dbinfo["id"], dbinfo["pw"], dbinfo["database"])
    return postQueryDataOne( qry, postConn , autoCommit)    

## postgresql 단일값
def postQueryDataOne( qry , postConn = None , autoCommit = True):
    rstData = { "result" : "ok", "msg" : f"정상" , "data" : ""}

    try:
        if postConn is None:
            postConn = timescaleDB()
        postCur = postConn.cursor()

        print(qry,'qry')
        postCur.execute(qry)
        print(postCur,'postCur')
        data = postCur.fetchone()
        print(data,'data')
        
        if debugM == 1:
            print("* Qry :", qry)
            print("* One Data : ",json.dumps(data, default=str, indent=4, ensure_ascii=False) )
            print("=" * 150)
        # datas = json.dumps(data, default=str, indent=4, ensure_ascii=False)
        #datas = json.dumps(data, default=str, ensure_ascii=False)
        #print(datas)
        # jsonDatas = json.loads(datas)
        if (autoCommit):
            postConn.commit()

        if (data is None):
            oData = ""
        else:
            oData = data[0]

        rstData = {"result" : "ok", "msg" : "처리 완료", "data" : oData}

            
    except Exception as e:
        print(f'PostSQL DataOne Query Failed: {e}')
        print("* Qry :", qry)
        print("=" * 150)
        rstData = { "result" : "error", "msg" : f"오류 : {e}" , "data" : ""}
        if (autoCommit):
            postConn.rollback()
    finally:
        if (autoCommit): 
            postConn.close()
        
        postCur.close()
        return rstData
    
def exPostQueryPageData( dbinfo, qryTable, whereOption:str = "",  pageNumber:int=1, pageSize:int = 10, postConn = None, autoCommit = True):    
    if postConn is None:
        postConn = timescaleDB2(dbinfo["ip"], dbinfo["port"], dbinfo["id"], dbinfo["pw"], dbinfo["database"])
    return postQueryPageData( qryTable, whereOption,  pageNumber, pageSize, postConn, autoCommit)    

## 테이블 페이징 조회
## where 옵션은 where 로 시작해야한다.
## 포스트그리 함수제약 조건으로 속도개선을 위해 변경(핸저 이건 미사용)
def postQueryPageDataFunc(qryTable, whereOption:str = "",  pageNumber:int=1, pageSize:int = 10, postConn = None, autoCommit = True ):
    
    rstData = { "result" : "ok", "msg" : f"정상" , "data" : ""}

    if debugM == 1:
        print("con", postConn)

    if postConn is None:
            postConn = timescaleDB()
    postCur = postConn.cursor()

    data = []
    try:
        qry = f"""
            select * from public.fn_paingloaddata( '{qryTable}', '{whereOption}', {pageNumber}, {pageSize});
            
        """
        if debugM == 1:
            print("* Qry : ",qry)
            print("=" * 150)

        postCur.execute(qry)
        data = postCur.fetchone()
        # jsonDatas = json.loads(datas)
        jsonDatas = data[0] #json.loads(data[0]) # 바로 가져옴
        jsonDatas = convert_null_to_blank(jsonDatas)
        #서버성능때문에 출력 최소
        #if debugM == 1:
            #print("* Json Datas :", json.dumps(data[0], default=str, indent=4, ensure_ascii=False))
            #print("=" * 150)
    
        if (autoCommit):
            postConn.commit()

        rstData = { "result" : "ok", "msg" : f"테이블 조회 완료" , "data" : jsonDatas}
    except Exception as e:
        print(f'PostSQL PageData Query Failed: {e}')
        print("* Qry : ",qry)
        print("=" * 150)
        rstData = { "result" : "error", "msg" : f"테이블 조회 오류 : {e}" , "data" : ""}
        if (autoCommit):
            postConn.rollback()
    finally:
        if (autoCommit): 
            postConn.close()

        postCur.close()
        return rstData


## where 옵션은 where 로 시작해야한다.
def postQueryPageData(qryTable, whereOption:str = "",  pageNumber:int=1, pageSize:int = 10, postConn = None, autoCommit = True ):
    
    rstData = { "result" : "ok", "msg" : f"정상" , "data" : ""}

    if debugM == 1:
        print("con", postConn)

    if postConn is None:
        postConn = timescaleDB()
    
    postCur = postConn.cursor()

    data = []
    qry = ""

    try:

        ##서브쿼리시 페이징 처리 속도 개선이 필요(8.14)
        ##서브쿼리 안에 오프셋 넣는걸로
        ##서브쿼리 () 제거후 오프셋 넣고 다시 () 걸로 변경
        newQryTable = qryTable.strip()

        if (newQryTable[0] == '(' and newQryTable[-1] == ')'):
            qry = f"""

with baseTBL as (
    select ROW_NUMBER() OVER(ORDER BY (SELECT 1)) 
        {
                f'''+  ( ( {pageNumber } -1 ) * {pageSize} )  '''   if pageNumber != 0 else ''
        } as "No"
        , *
    from (
        select 
            dkfdldktm_a.*
        from ( 
            {newQryTable[1:-1]} 
            {
            f'''OFFSET  ( ( {pageNumber } -1 ) * {pageSize} ) ROWS FETCH NEXT {pageSize}  ROWS ONLY '''  if pageNumber != 0 else ''
            }
        ) as dkfdldktm_a 

        {whereOption if whereOption != '' else ''}
    ) r
            """
        else:
            qry = f"""
                        
            with baseTBL as (
                select ROW_NUMBER() OVER(ORDER BY (SELECT 1)) 
                {
                        f'''+  ( ( {pageNumber } -1 ) * {pageSize} )  '''   if pageNumber != 0 else ''
                }  as "No"
                    , *
                from (
                    select 
                        dkfdldktm_a.*
                    from {qryTable} 
                    as dkfdldktm_a 
                    {whereOption if whereOption != '' else ''}
                    {
                    f''' OFFSET  ( ( {pageNumber } -1 ) * {pageSize} ) ROWS FETCH NEXT {pageSize}  ROWS ONLY '''  if pageNumber != 0 else ''
                    } 
                ) r
            """


        qry += f"""

), totTBL as (
    select count(*) as recordsTotal
    from  {qryTable} 
    as dkfdldktm_a
)

{ f'''
, filterTBL as (
    select count(*) as recordsFiltered
    from {qryTable} 
    as dkfdldktm_a 
    {whereOption}
)

''' if whereOption != '' 
    else f'''
, filterTBL as (
    select recordsTotal as recordsFiltered
    from totTBL
)
'''
}

select row_to_json(r) as results
from (
    select 
        { pageNumber } as draw
        ,b_aliasname.recordsTotal as "recordsTotal"
        ,c_aliasname.recordsFiltered as "recordsFiltered"
        , a_aliasname.data
    from (
        select array_to_json( 
            array (
                select row_to_json(a_aliasname1)
                from baseTBL  a_aliasname1
            )         
        ) as data
    ) as a_aliasname
    , totTBL as b_aliasname
    , filterTBL as c_aliasname
) r  
    
        """

        if debugM == 1:
            print("* Qry : ",qry)
            print("=" * 150)

        postCur.execute(qry)
        data = postCur.fetchone()
        # jsonDatas = json.loads(datas)
        jsonDatas = data[0] #json.loads(data[0]) # 바로 가져옴
        jsonDatas = convert_null_to_blank(jsonDatas)
        #if debugM == 1:
            #print("* Json Datas :", json.dumps(data[0], default=str, indent=4, ensure_ascii=False))
            #print("=" * 150)
    
        if (autoCommit):
            postConn.commit()

        rstData = { "result" : "ok", "msg" : f"테이블 조회 완료" , "data" : jsonDatas}
    except Exception as e:
        print(f'PostSQL PageData Query Failed: {e}')
        print("* Qry : ",qry)
        print("=" * 150)
        rstData = { "result" : "error", "msg" : f"테이블 조회 오류 : {e}" , "data" : ""}
        if (autoCommit):
            postConn.rollback()
    finally:
        if (autoCommit): 
            postConn.close()

        postCur.close()
        return rstData
