from core.conecciones.sybase import query_sybase

class EmpleadoServicio:

    @staticmethod
    def buscar_empleado(nombre):
        sql = """ SELECT TOP 20 * FROM vw_maestro_hd WHERE Nombre_Empleado LIKE ? """

        return query_sybase(sql, [f"%{nombre}%"])
    
    def listar_todos():
        sql = """ SELECT * FROM vw_maestro_hd ORDER BY Numero_Empleado """

        return query_sybase(sql)
    
    def buscar_numempleado(empleado):
        sql = """ SELECT * FROM vw_maestro_hd WHERE Numero_Empleado = ? """

        return query_sybase(sql, [int(empleado)])