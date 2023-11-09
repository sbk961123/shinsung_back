from machbaseAPI.machbaseAPI import machbase
import json

# # 사용자에게 받아온 정보로 접속
def machbaseDB():
    # machConn = machbaseDB('150.4.5.164','sys','manager',5656)
    
    conn = machbase()
    conn.open('150.4.5.164','sys','manager',5656)
    return conn

def selectNowData(EQUIPNUM):
    qry = f''' SELECT a.SID AS EQUIPNUM
        , b.TIMESTAMP
        , a.FR_TIME, a.TO_TIME
        , CASE WHEN b.TID LIKE '%TIME_PER_STRING' THEN value END AS 'TIME_PER_STRING(s)'
        , CASE WHEN b.TID LIKE '%BOTTOMPLATE01_TEMP' THEN value END AS 'BOTTOMPLATE01_TEMP'
        , CASE WHEN b.TID LIKE '%BOTTOMPLATE02_TEMP' THEN value END AS 'BOTTOMPLATE02_TEMP'
        , CASE WHEN b.TID LIKE '%BOTTOMPLATE03_TEMP' THEN value END AS 'BOTTOMPLATE03_TEMP'
        , CASE WHEN b.TID LIKE '%BOTTOMPLATE04_TEMP' THEN value END AS 'BOTTOMPLATE04_TEMP'
        , CASE WHEN b.TID LIKE '%BOTTOMPLATE05_TEMP' THEN value END AS 'BOTTOMPLATE05_TEMP'
        , CASE WHEN b.TID LIKE '%BOTTOMPLATE06_TEMP' THEN value END AS 'BOTTOMPLATE06_TEMP'
        , CASE WHEN b.TID LIKE '%BOTTOMPLATE07_TEMP' THEN value END AS 'BOTTOMPLATE07_TEMP'
        , CASE WHEN b.TID LIKE '%BOTTOMPLATE08_TEMP' THEN value END AS 'BOTTOMPLATE08_TEMP'
        , CASE WHEN b.TID LIKE '%BOTTOMPLATE09_TEMP' THEN value END AS 'BOTTOMPLATE09_TEMP'
        , CASE WHEN b.TID LIKE '%BOTTOMPLATE10_TEMP' THEN value END AS 'BOTTOMPLATE10_TEMP'
        , a.OK_NG
    FROM (

        SELECT E_SQ, SID
             , MIN(R_TIME) AS fr_time
             , MAX(R_TIME) AS to_time
             , MAX(CASE WHEN SQ = 1 THEN OK_NG ELSE '' END) AS OK_NG
        FROM (
            SELECT a.E_SQ
                , b.SQ
                , a.SID
                , b.R_TIME
                , b.OK_NG
            FROM (

                -- 테버리스트
                SELECT ROWNUM() AS E_SQ
                    , SID
                FROM (
                    SELECT   SUBSTR(TID,1,9) AS SID
                    FROM _TAG_META
                    WHERE SUBSTR(TID,1, 6) = 'TABBER'
                    GROUP BY SUBSTR(TID,1, 9)
                    ORDER BY SUBSTR(TID,1, 9)
                ) a
                ORDER BY SID
            ) a
            JOIN (
                SELECT ROWNUM() AS SQ
                    , SID
                    , TID
                    , TIMESTAMP AS R_TIME
                    , CASE WHEN TID LIKE '%STRING_NUMBER_OK'  THEN 'OK' ELSE 'NG' END AS OK_NG
                FROM tag
                where tid like '{EQUIPNUM}.STRING_NUMBER_%'
                ORDER BY SID, TIMESTAMP DESC
                LIMIT 2
        ) b ON a.SID = b.SID
        ) aa
        GROUP BY E_SQ, SID
    ) a
    LEFT JOIN TAG b ON a.SID = b.SID
        AND b.TIMESTAMP BETWEEN a.FR_TIME AND a.TO_TIME
        AND ( TID LIKE '%.BOTTOMPLATE%' OR TID LIKE '%.TIME_PER_STRING' )
    ORDER BY a.E_SQ, b.TID, b.TIMESTAMP

    '''
    try:
      machConn = machbaseDB()
      machConn.execute(qry)
      mdata = machConn.result()
      jdata = '[' + mdata + ']'
      rstData = json.loads(jdata)
    except Exception as e:
        print(f'SQL DataSet Query Failed: {e}')
        print("* mach Qry : ", qry)
        print("=" * 150)
        rstData = { "result" : "error", "msg" : f"오류 : {e}" , "data" : []}
    finally: 
        # machConn.close()
        return rstData