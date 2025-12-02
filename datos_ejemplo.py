"""
Script para poblar datos de ejemplo en la base de datos.
Usar para pruebas rápidas de la aplicación.
"""
import db


def poblar_ejemplo():
    db.inicializar_bd()
    # Crear departamentos
    dep1 = db.agregar_departamento("Desarrollo")
    dep2 = db.agregar_departamento("Recursos Humanos")

    # Crear proyectos
    proj1 = db.agregar_proyecto("Portal Web", "Desarrollo del portal cliente")
    proj2 = db.agregar_proyecto("Infraestructura", "Migración a la nube")

    # Crear empleado con contraseña 'password123'
    hash_pw = db.hash_contrasena("password123")
    emp1 = db.agregar_empleado("María Pérez", "Calle Falsa 123", "+56912345678", "maria.perez@example.com", 1200.0, hash_pw, dep1)

    # Asignar a proyecto y registrar horas
    db.asignar_empleado_a_proyecto(emp1, proj1)
    db.agregar_registro_tiempo(emp1, proj1, "2025-12-01", 6.5)

    print("Datos de ejemplo creados:")
    print("Departamentos:", db.listar_departamentos())
    print("Proyectos:", db.listar_proyectos())
    print("Empleados:", db.listar_empleados())
    print("Registros:", db.listar_registros())


if __name__ == "__main__":
    poblar_ejemplo()
