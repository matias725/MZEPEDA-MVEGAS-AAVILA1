"""
Script para poblar datos de ejemplo en la base de datos.
Usar para pruebas rápidas de la aplicación.
"""
import db


def poblar_ejemplo():
    db.inicializar_bd()
    
    # Verificar si ya existen datos
    departamentos_existentes = db.listar_departamentos()
    if departamentos_existentes:
        print("⚠️  La base de datos ya contiene datos.")
        print(f"  - {len(departamentos_existentes)} departamentos")
        print(f"  - {len(db.listar_proyectos())} proyectos")
        print(f"  - {len(db.listar_empleados())} empleados")
        print(f"  - {len(db.listar_registros())} registros")
        
        # Agregar solo un empleado adicional si no existe
        try:
            print("\n➕ Agregando nuevo empleado de prueba...")
            dep_rrhh = [d for d in departamentos_existentes if "Recursos" in d[1]]
            dep_id = dep_rrhh[0][0] if dep_rrhh else departamentos_existentes[0][0]
            
            hash_admin = db.hash_contrasena("admin2025")
            emp_admin = db.agregar_empleado(
                "Juan Administrador", 
                "Av. Principal 456", 
                "+56987654321", 
                "admin@ecotech.com", 
                2500.0, 
                hash_admin, 
                dep_id
            )
            
            # Asignar a primer proyecto disponible
            proyectos = db.listar_proyectos()
            if proyectos:
                db.asignar_empleado_a_proyecto(emp_admin, proyectos[0][0])
                db.agregar_registro_tiempo(emp_admin, proyectos[0][0], "2025-12-02", 8.0)
            
            print("\n✅ Nueva credencial creada exitosamente:")
            print("   📧 Email: admin@ecotech.com")
            print("   🔑 Contraseña: admin2025")
            print("   👤 Usuario: Juan Administrador")
            
        except Exception as e:
            print(f"\n⚠️  El usuario ya existe o hubo un error: {e}")
        
        return
    
    # Crear departamentos
    dep1 = db.agregar_departamento("Desarrollo")
    dep2 = db.agregar_departamento("Recursos Humanos")

    # Crear proyectos
    proj1 = db.agregar_proyecto("Portal Web", "Desarrollo del portal cliente")
    proj2 = db.agregar_proyecto("Infraestructura", "Migración a la nube")

    # Crear empleado 1 con contraseña 'password123'
    hash_pw = db.hash_contrasena("password123")
    emp1 = db.agregar_empleado("Matías Zepeda", "Calle Falsa 123", "+56912345678", "matias.zepeda@ecotech.com", 1200.0, hash_pw, dep1)

    # Crear empleado 2 con contraseña 'admin2025'
    hash_admin = db.hash_contrasena("admin2025")
    emp2 = db.agregar_empleado("Juan Administrador", "Av. Principal 456", "+56987654321", "admin@ecotech.com", 2500.0, hash_admin, dep2)

    # Asignar a proyectos y registrar horas
    db.asignar_empleado_a_proyecto(emp1, proj1)
    db.agregar_registro_tiempo(emp1, proj1, "2025-12-01", 6.5)
    
    db.asignar_empleado_a_proyecto(emp2, proj2)
    db.agregar_registro_tiempo(emp2, proj2, "2025-12-02", 8.0)

    print("✅ Datos de ejemplo creados exitosamente:")
    print(f"  - Departamentos: {len(db.listar_departamentos())}")
    print(f"  - Proyectos: {len(db.listar_proyectos())}")
    print(f"  - Empleados: {len(db.listar_empleados())}")
    print(f"  - Registros: {len(db.listar_registros())}")
    
    print("\n🔑 Credenciales de prueba:")
    print("  1️⃣  Email: matias.zepeda@ecotech.com  |  Contraseña: password123")
    print("  2️⃣  Email: admin@ecotech.com          |  Contraseña: admin2025")


if __name__ == "__main__":
    poblar_ejemplo()
