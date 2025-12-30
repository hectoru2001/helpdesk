import pyodbc

def get_sybase_connection():
    return pyodbc.connect(
        "DRIVER=FreeTDS;"
        "SERVER=10.236.0.3;"
        "PORT=5000;"
        "TDS_Version=5.0;"
        "UID=usr_helpdesk;"
        "PWD=Y53r-H3lDs;"
        "DATABASE=rhumanos;"
        "CHARSET=UTF8;"
    )

def query_sybase(sql, params=None):
    conn = get_sybase_connection()
    cursor = conn.cursor()

    if params:
        cursor.execute(sql, params)
    else:
        cursor.execute(sql)

    columns = [col[0] for col in cursor.description]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]

    conn.close()
    return results
