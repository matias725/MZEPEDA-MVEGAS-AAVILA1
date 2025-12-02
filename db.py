"""
Módulo de acceso a datos (SQLite) y funciones de seguridad.

Implementa:
- Inicialización de la base de datos y creación de tablas
- CRUD básico para empleados, departamentos, proyectos y registros de tiempo
- Hash y verificación de contraseñas con SHA-256
"""
import sqlite3
from typing import Optional, List, Tuple
import hashlib
import os

DB_RUTA_DEFAULT = os.path.join(os.path.dirname(__file__), "ecotech.db")


def obtener_conexion(ruta_db: str = DB_RUTA_DEFAULT):
    """Devuelve una conexión a la base de datos SQLite."""
    return sqlite3.connect(ruta_db)


def inicializar_bd(ruta_db: str = DB_RUTA_DEFAULT):
    """Crea las tablas necesarias si no existen."""
    with obtener_conexion(ruta_db) as conn:
        cursor = conn.cursor()
        # Tabla de departamentos
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS departamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            id_gerente INTEGER
        )
        """)

        # Tabla de proyectos
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS proyectos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT
        )
        """)

        # Tabla de empleados
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS empleados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            direccion TEXT,
            telefono TEXT,
            email TEXT NOT NULL UNIQUE,
            salario REAL,
            password_hash TEXT NOT NULL,
            departamento_id INTEGER,
            FOREIGN KEY(departamento_id) REFERENCES departamentos(id)
        )
        """)

        # Relación muchos-a-muchos empleados <-> proyectos
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS proyectos_empleados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empleado_id INTEGER NOT NULL,
            proyecto_id INTEGER NOT NULL,
            UNIQUE(empleado_id, proyecto_id),
            FOREIGN KEY(empleado_id) REFERENCES empleados(id),
            FOREIGN KEY(proyecto_id) REFERENCES proyectos(id)
        )
        """)

        # Registros de tiempo
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS registros_tiempo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empleado_id INTEGER NOT NULL,
            proyecto_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            horas REAL NOT NULL,
            FOREIGN KEY(empleado_id) REFERENCES empleados(id),
            FOREIGN KEY(proyecto_id) REFERENCES proyectos(id)
        )
        """)

        conn.commit()


# ------------------ Seguridad de contraseñas ------------------
def hash_contrasena(contrasena: str) -> str:
    """Devuelve el hash SHA-256 hexadecimal de la contraseña.

    Usar este método antes de almacenar la contraseña en la BD.
    """
    if contrasena is None:
        raise ValueError("La contraseña no puede ser None")
    h = hashlib.sha256()
    h.update(contrasena.encode("utf-8"))
    return h.hexdigest()


def verificar_contrasena(contrasena_plana: str, hash_almacenado: str) -> bool:
    """Verifica si la contraseña en texto plano coincide con el hash almacenado."""
    return hash_contrasena(contrasena_plana) == hash_almacenado


# ------------------ Operaciones CRUD básicas ------------------
def agregar_departamento(nombre: str, ruta_db: str = DB_RUTA_DEFAULT) -> int:
    with obtener_conexion(ruta_db) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO departamentos (nombre) VALUES (?)", (nombre,))
        conn.commit()
        return cursor.lastrowid


def listar_departamentos(ruta_db: str = DB_RUTA_DEFAULT) -> List[Tuple]:
    with obtener_conexion(ruta_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, id_gerente FROM departamentos")
        return cursor.fetchall()


def agregar_proyecto(nombre: str, descripcion: str = "", ruta_db: str = DB_RUTA_DEFAULT) -> int:
    with obtener_conexion(ruta_db) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO proyectos (nombre, descripcion) VALUES (?, ?)", (nombre, descripcion))
        conn.commit()
        return cursor.lastrowid


def listar_proyectos(ruta_db: str = DB_RUTA_DEFAULT) -> List[Tuple]:
    with obtener_conexion(ruta_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, descripcion FROM proyectos")
        return cursor.fetchall()


def agregar_empleado(nombre: str, direccion: str, telefono: str, email: str,
                     salario: float, password_hash: str, departamento_id: Optional[int] = None,
                     ruta_db: str = DB_RUTA_DEFAULT) -> int:
    with obtener_conexion(ruta_db) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO empleados (nombre, direccion, telefono, email, salario, password_hash, departamento_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (nombre, direccion, telefono, email, salario, password_hash, departamento_id)
        )
        conn.commit()
        return cursor.lastrowid


def obtener_empleado_por_email(email: str, ruta_db: str = DB_RUTA_DEFAULT) -> Optional[Tuple]:
    with obtener_conexion(ruta_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, direccion, telefono, email, salario, password_hash, departamento_id FROM empleados WHERE email = ?", (email,))
        return cursor.fetchone()


def listar_empleados(ruta_db: str = DB_RUTA_DEFAULT) -> List[Tuple]:
    with obtener_conexion(ruta_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, direccion, telefono, email, salario, departamento_id FROM empleados")
        return cursor.fetchall()


def asignar_empleado_a_proyecto(empleado_id: int, proyecto_id: int, ruta_db: str = DB_RUTA_DEFAULT) -> int:
    with obtener_conexion(ruta_db) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO proyectos_empleados (empleado_id, proyecto_id) VALUES (?, ?)", (empleado_id, proyecto_id))
        conn.commit()
        return cursor.lastrowid


def agregar_registro_tiempo(empleado_id: int, proyecto_id: int, fecha: str, horas: float, ruta_db: str = DB_RUTA_DEFAULT) -> int:
    with obtener_conexion(ruta_db) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO registros_tiempo (empleado_id, proyecto_id, fecha, horas) VALUES (?, ?, ?, ?)",
            (empleado_id, proyecto_id, fecha, horas)
        )
        conn.commit()
        return cursor.lastrowid


def listar_registros(ruta_db: str = DB_RUTA_DEFAULT) -> List[Tuple]:
    with obtener_conexion(ruta_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, empleado_id, proyecto_id, fecha, horas FROM registros_tiempo")
        return cursor.fetchall()


# ------------------ Funciones adicionales (actualizar / eliminar / consultas) ------------------
def actualizar_empleado(id_empleado: int, nombre: str, direccion: str, telefono: str,
                        email: str, salario: float, departamento_id: Optional[int],
                        ruta_db: str = DB_RUTA_DEFAULT) -> None:
    """Actualiza los datos de un empleado (sin cambiar contraseña)."""
    with obtener_conexion(ruta_db) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE empleados
            SET nombre = ?, direccion = ?, telefono = ?, email = ?, salario = ?, departamento_id = ?
            WHERE id = ?
            """,
            (nombre, direccion, telefono, email, salario, departamento_id, id_empleado)
        )
        conn.commit()


def actualizar_contrasena_empleado(id_empleado: int, nueva_contrasena: str, ruta_db: str = DB_RUTA_DEFAULT) -> None:
    """Actualiza la contraseña (almacenando su hash)."""
    hash_pw = hash_contrasena(nueva_contrasena)
    with obtener_conexion(ruta_db) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE empleados SET password_hash = ? WHERE id = ?", (hash_pw, id_empleado))
        conn.commit()


def eliminar_empleado(id_empleado: int, ruta_db: str = DB_RUTA_DEFAULT) -> None:
    """Elimina un empleado y sus asignaciones y registros relacionados."""
    with obtener_conexion(ruta_db) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM proyectos_empleados WHERE empleado_id = ?", (id_empleado,))
        cursor.execute("DELETE FROM registros_tiempo WHERE empleado_id = ?", (id_empleado,))
        cursor.execute("DELETE FROM empleados WHERE id = ?", (id_empleado,))
        conn.commit()


def desasignar_empleado_de_proyecto(empleado_id: int, proyecto_id: int, ruta_db: str = DB_RUTA_DEFAULT) -> None:
    with obtener_conexion(ruta_db) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM proyectos_empleados WHERE empleado_id = ? AND proyecto_id = ?", (empleado_id, proyecto_id))
        conn.commit()


def obtener_proyectos_de_empleado(empleado_id: int, ruta_db: str = DB_RUTA_DEFAULT) -> List[Tuple]:
    with obtener_conexion(ruta_db) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT p.id, p.nombre, p.descripcion FROM proyectos p"
            " JOIN proyectos_empleados pe ON p.id = pe.proyecto_id"
            " WHERE pe.empleado_id = ?",
            (empleado_id,)
        )
        return cursor.fetchall()


def asignar_gerente_departamento(departamento_id: int, gerente_id: Optional[int], ruta_db: str = DB_RUTA_DEFAULT) -> None:
    """Asigna (o elimina si gerente_id es None) el gerente de un departamento."""
    with obtener_conexion(ruta_db) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE departamentos SET id_gerente = ? WHERE id = ?", (gerente_id, departamento_id))
        conn.commit()


def eliminar_departamento(departamento_id: int, ruta_db: str = DB_RUTA_DEFAULT) -> None:
    """Elimina un departamento; deja los empleados con departamento_id = NULL."""
    with obtener_conexion(ruta_db) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE empleados SET departamento_id = NULL WHERE departamento_id = ?", (departamento_id,))
        cursor.execute("DELETE FROM departamentos WHERE id = ?", (departamento_id,))
        conn.commit()


def actualizar_departamento(departamento_id: int, nombre: str, ruta_db: str = DB_RUTA_DEFAULT) -> None:
    with obtener_conexion(ruta_db) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE departamentos SET nombre = ? WHERE id = ?", (nombre, departamento_id))
        conn.commit()


def eliminar_proyecto(proyecto_id: int, ruta_db: str = DB_RUTA_DEFAULT) -> None:
    """Elimina un proyecto y sus asignaciones y registros relacionados."""
    with obtener_conexion(ruta_db) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM proyectos_empleados WHERE proyecto_id = ?", (proyecto_id,))
        cursor.execute("DELETE FROM registros_tiempo WHERE proyecto_id = ?", (proyecto_id,))
        cursor.execute("DELETE FROM proyectos WHERE id = ?", (proyecto_id,))
        conn.commit()


def actualizar_proyecto(proyecto_id: int, nombre: str, descripcion: str, ruta_db: str = DB_RUTA_DEFAULT) -> None:
    with obtener_conexion(ruta_db) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE proyectos SET nombre = ?, descripcion = ? WHERE id = ?", (nombre, descripcion, proyecto_id))
        conn.commit()
