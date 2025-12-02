import unittest
import tempfile
import os
import db


class TestDB(unittest.TestCase):
    def setUp(self):
        # Crear base de datos temporal para pruebas
        self.tmp = tempfile.NamedTemporaryFile(delete=False)
        self.db_path = self.tmp.name
        self.tmp.close()
        db.inicializar_bd(ruta_db=self.db_path)

    def tearDown(self):
        try:
            os.unlink(self.db_path)
        except Exception:
            pass

    def test_crud_basico(self):
        # Departamentos
        id_dep = db.agregar_departamento('Pruebas', ruta_db=self.db_path)
        deps = db.listar_departamentos(ruta_db=self.db_path)
        self.assertTrue(any(d[0] == id_dep for d in deps))

        # Proyectos
        id_proj = db.agregar_proyecto('Proyecto Test', 'Desc', ruta_db=self.db_path)
        projs = db.listar_proyectos(ruta_db=self.db_path)
        self.assertTrue(any(p[0] == id_proj for p in projs))

        # Empleado
        hash_pw = db.hash_contrasena('abc123')
        id_emp = db.agregar_empleado('Test', 'Dir', '000', 't@test.com', 1000.0, hash_pw, id_dep, ruta_db=self.db_path)
        emp = db.obtener_empleado_por_email('t@test.com', ruta_db=self.db_path)
        self.assertIsNotNone(emp)

        # Asignar proyecto y agregar registro
        db.asignar_empleado_a_proyecto(id_emp, id_proj, ruta_db=self.db_path)
        db.agregar_registro_tiempo(id_emp, id_proj, '2025-12-02', 4.0, ruta_db=self.db_path)
        regs = db.listar_registros(ruta_db=self.db_path)
        self.assertTrue(len(regs) >= 1)

        # Actualizar empleado
        db.actualizar_empleado(id_emp, 'Test2', 'Dir2', '111', 't2@test.com', 1100.0, None, ruta_db=self.db_path)
        emp2 = db.obtener_empleado_por_email('t2@test.com', ruta_db=self.db_path)
        self.assertIsNotNone(emp2)

        # Eliminar empleado
        db.eliminar_empleado(id_emp, ruta_db=self.db_path)
        emp3 = db.obtener_empleado_por_email('t2@test.com', ruta_db=self.db_path)
        self.assertIsNone(emp3)


if __name__ == '__main__':
    unittest.main()
