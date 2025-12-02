"""
Modelos POO para el sistema de gestión de empleados (EcoTech Solutions).
Contiene las clases: Persona, Empleado, Departamento, Proyecto, RegistroTiempo.
Todos los comentarios y nombres están en español para la evaluación.
"""
from datetime import date


class Persona:
    """Clase base Persona.

    Atributos:
        nombre (str)
        direccion (str)
        telefono (str)
        email (str)
    """

    def __init__(self, nombre: str, direccion: str, telefono: str, email: str):
        self.nombre = nombre
        self.direccion = direccion
        self.telefono = telefono
        self.email = email

    def obtener_descripcion(self) -> str:
        """Método polimórfico: devuelve una descripción básica de la persona.
        Las subclases pueden sobreescribir este método.
        """
        return f"Persona: {self.nombre} - {self.email}"

    def __str__(self):
        return self.obtener_descripcion()


class Empleado(Persona):
    """Clase Empleado que hereda de Persona.

    Atributos adicionales:
        id_empleado (int) - puede ser None hasta guardarlo en la BD
        salario (float)
        password_hash (str) - el hash SHA-256 de la contraseña
        departamento_id (int | None)
    """

    def __init__(self, nombre: str, direccion: str, telefono: str, email: str,
                 salario: float, password_hash: str, id_empleado: int = None,
                 departamento_id: int = None):
        super().__init__(nombre, direccion, telefono, email)
        self.id_empleado = id_empleado
        self.salario = salario
        self.password_hash = password_hash
        self.departamento_id = departamento_id

    def obtener_descripcion(self) -> str:
        """Sobrescribe el método de Persona para incluir datos de empleado.
        Esto demuestra polimorfismo: un objeto Empleado responde de forma distinta.
        """
        return f"Empleado #{self.id_empleado or 'N/A'}: {self.nombre} - {self.email}"


class Departamento:
    """Representa un departamento de la empresa.

    Atributos:
        id (int | None)
        nombre (str)
        id_gerente (int | None) - referencia a `Empleado.id_empleado`
    """

    def __init__(self, nombre: str, id: int = None, id_gerente: int = None):
        self.id = id
        self.nombre = nombre
        self.id_gerente = id_gerente

    def __str__(self):
        return f"Departamento #{self.id or 'N/A'}: {self.nombre}"


class Proyecto:
    """Representa un proyecto.

    Atributos:
        id (int | None)
        nombre (str)
        descripcion (str)
    """

    def __init__(self, nombre: str, descripcion: str = "", id: int = None):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion

    def __str__(self):
        return f"Proyecto #{self.id or 'N/A'}: {self.nombre}"


class RegistroTiempo:
    """Registro de horas trabajadas por un empleado en un proyecto una fecha.

    Atributos:
        empleado_id (int)
        proyecto_id (int)
        fecha (str) - formato ISO YYYY-MM-DD
        horas (float)
    """

    def __init__(self, empleado_id: int, proyecto_id: int, fecha: str, horas: float, id: int = None):
        self.id = id
        self.empleado_id = empleado_id
        self.proyecto_id = proyecto_id
        self.fecha = fecha
        self.horas = horas

    def __str__(self):
        return f"Registro: Empleado={self.empleado_id}, Proyecto={self.proyecto_id}, Fecha={self.fecha}, Horas={self.horas}"
