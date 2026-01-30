import pyodbc

def get_sybase_connection(database="rhumanos"):
    return pyodbc.connect(
        "DRIVER=FreeTDS;"
        "SERVER=10.236.0.3;"
        "PORT=5000;"
        "TDS_Version=5.0;"
        "UID=usr_helpdesk;"
        "PWD=Y53r-H3lDs;"
        f"DATABASE={database};"
        "CHARSET=UTF8;"
    )

def get_sybase_connection_extra(database="activos"):
    return pyodbc.connect(
        "DRIVER=FreeTDS;"
        "SERVER=10.236.0.8;"
        "PORT=5000;"
        "TDS_Version=5.0;"
        "UID=helpDesk_usr;"
        "PWD=helpDesk_DBv1!2026;"
        "DATABASE=activos;"
        "CHARSET=UTF8;"
    )

def query_sybase(sql, params=None, database="rhumanos"):
    if database == "activos":
        conn = get_sybase_connection_extra(database)
    else:
        conn = get_sybase_connection(database)
    cursor = conn.cursor()

    if params:
        cursor.execute(sql, params)
    else:
        cursor.execute(sql)

    columns = [col[0] for col in cursor.description]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]

    conn.close()
    return results
