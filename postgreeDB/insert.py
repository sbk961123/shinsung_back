# FLOAT 처리
def is_number(n):
    if n != 'NULL':
        try:
            float(n)
        except ValueError:
            return False

    return True

def InsertQuery(tableName:str, data:dict):
    sql = 'INSERT into "ss_ai".{} ("{}")values({})'
    key = '", "'.join(list(data.keys()))
    value=','.join(str(e) if is_number(str(e)) else "'"+str(e)+"'" for e in data.values())
    return sql.format(tableName, key, value)