from core.conecciones.sybase import query_sybase

class EmpleadoServicio:

    @staticmethod
    def buscar_empleado(nombre):
        sql = """
            SELECT TOP 20 *
            FROM vw_maestro_hd
            WHERE Nombre_Empleado LIKE ?
        """
        return query_sybase(sql, [f"%{nombre}%"])

    @staticmethod
    def buscar_funcionario(nombre):
        sql = """
            SELECT TOP 20 *
            FROM vw_maestro_hd
            WHERE Nombre_Empleado LIKE ?
        """
        return query_sybase(sql, [f"%{nombre}%"], database="funcionarios")

    @staticmethod
    def buscar_numempleado(empleado, database="rhumanos"):
        sql = """
            SELECT *
            FROM vw_maestro_hd
            WHERE Numero_Empleado = ?
        """
        return query_sybase(sql, [int(empleado)], database=database)


    def listar_todos():
        sql = """ SELECT * FROM vw_maestro_hd ORDER BY Numero_Empleado """

        return query_sybase(sql)
    
    def buscar_numempleado(empleado):
        sql = """ SELECT * FROM vw_maestro_hd WHERE Numero_Empleado = ? """

        return query_sybase(sql, [int(empleado)])
    
    def buscar_numpatrimonio(empleado):
        sql = """ SELECT codigo, serie, descripcion, marca, color FROM patr_mob_articulos WHERE codigo = ? """

        return query_sybase(sql, [empleado], database="activos")
    
