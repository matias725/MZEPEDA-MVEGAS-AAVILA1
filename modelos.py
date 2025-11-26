# Modelos para manejar usuarios y la BD
import bcrypt
from db import get_db
from mysql.connector import Error

# Excepciones para errores de usuarios
class UsuarioError(Exception):
    # Error base para todo lo relacionado con usuarios
    pass


# Clase Usuario
class Usuario:
    def __init__(self, nombre_usuario, correo, rol='usuario', password=None, id=None):
        self.id = id
        self.nombre_usuario = nombre_usuario
        self.correo = correo
        self.rol = rol
        self._pass_hash = None
        
        # Hashear password si se proporciona
        if password:
            self.set_password(password)
    
    # Hashear password con bcrypt
    def set_password(self, password):
        pw_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=12)
        self._pass_hash = bcrypt.hashpw(pw_bytes, salt).decode('utf-8')
    
    # Verificar si el password es correcto
    def check_password(self, password):
        if not self._pass_hash:
            return False
        pw_bytes = password.encode('utf-8')
        hash_bytes = self._pass_hash.encode('utf-8')
        return bcrypt.checkpw(pw_bytes, hash_bytes)
    
    # Obtener el hash para guardarlo en BD
    def get_hash(self):
        return self._pass_hash
    
    # Setear un hash que ya existe (cuando cargo de BD)
    def set_hash(self, hash_str):
        self._pass_hash = hash_str
    
    def __str__(self):
        return f"Usuario({self.nombre_usuario}, {self.correo}, {self.rol})"

# Clase para manejar todo el CRUD de usuarios
class GestorUsuarios:
    def __init__(self):
        self.db = get_db()
    
    # Agregar usuario nuevo
    def agregar_usuario(self, usuario):
        try:
            # Verificar que no exista
            if self._existe_usuario(usuario.nombre_usuario, usuario.correo):
                raise UsuarioError(f"El usuario '{usuario.nombre_usuario}' o correo ya existe")
            
            query = "INSERT INTO usuarios (nombre_usuario, password, correo, rol) VALUES (%s, %s, %s, %s)"
            params = (
                usuario.nombre_usuario,
                usuario.get_hash(),
                usuario.correo,
                usuario.rol
            )
            
            id_nuevo = self.db.ejecutar_query(query, params, commit=True)
            usuario.id = id_nuevo
            print(f"Usuario '{usuario.nombre_usuario}' creado (ID: {id_nuevo})")
            return id_nuevo
        except UsuarioError:
            raise
        except Error as e:
            raise UsuarioError(f"Error agregando usuario: {e}")
    
    # Ver si un usuario ya existe
    def _existe_usuario(self, nombre, correo):
        query = "SELECT id FROM usuarios WHERE nombre_usuario = %s OR correo = %s"
        result = self.db.ejecutar_query(query, (nombre, correo))
        return len(result) > 0
    
    # Buscar usuario por nombre
    def buscar_por_nombre(self, nombre):
        try:
            query = "SELECT * FROM usuarios WHERE nombre_usuario = %s"
            result = self.db.ejecutar_query(query, (nombre,))
            
            if not result:
                raise UsuarioError(f"Usuario '{nombre}' no encontrado")
            
            datos = result[0]
            usr = Usuario(
                nombre_usuario=datos['nombre_usuario'],
                correo=datos['correo'],
                rol=datos['rol'],
                id=datos['id']
            )
            usr.set_hash(datos['password'])
            return usr
        except UsuarioError:
            raise
        except Error as e:
            raise UsuarioError(f"Error buscando: {e}")
    
    # Buscar por ID
    def buscar_por_id(self, id_usr):
        try:
            query = "SELECT * FROM usuarios WHERE id = %s"
            result = self.db.ejecutar_query(query, (id_usr,))
            
            if not result:
                raise UsuarioError(f"Usuario ID {id_usr} no encontrado")
            
            datos = result[0]
            usr = Usuario(
                nombre_usuario=datos['nombre_usuario'],
                correo=datos['correo'],
                rol=datos['rol'],
                id=datos['id']
            )
            usr.set_hash(datos['password'])
            return usr
        except UsuarioError:
            raise
        except Error as e:
            raise UsuarioError(f"Error: {e}")
    
    # Listar todos
    def listar_todos(self):
        try:
            query = "SELECT * FROM usuarios ORDER BY id"
            result = self.db.ejecutar_query(query)
            
            usuarios = []
            for datos in result:
                usr = Usuario(
                    nombre_usuario=datos['nombre_usuario'],
                    correo=datos['correo'],
                    rol=datos['rol'],
                    id=datos['id']
                )
                usr.set_hash(datos['password'])
                usuarios.append(usr)
            return usuarios
        except Error as e:
            raise UsuarioError(f"Error listando: {e}")
    
    # Modificar datos de un usuario
    def modificar(self, id_usr, nuevo_correo=None, nuevo_rol=None, nuevo_pass=None):
        try:
            usuario = self.buscar_por_id(id_usr)
            
            campos = []
            params = []
            
            if nuevo_correo:
                campos.append("correo = %s")
                params.append(nuevo_correo)
            
            if nuevo_rol:
                campos.append("rol = %s")
                params.append(nuevo_rol)
            
            if nuevo_pass:
                usr_temp = Usuario('temp', 'temp@t.com', password=nuevo_pass)
                campos.append("password = %s")
                params.append(usr_temp.get_hash())
            
            if not campos:
                print("No hay nada que modificar")
                return False
            
            params.append(id_usr)
            
            query = f"UPDATE usuarios SET {', '.join(campos)} WHERE id = %s"
            filas = self.db.ejecutar_query(query, tuple(params), commit=True)
            
            if filas > 0:
                print(f"Usuario ID {id_usr} modificado")
                return True
            return False
        except UsuarioError:
            raise
        except Error as e:
            raise UsuarioError(f"Error modificando: {e}")
    
    # Eliminar usuario
    def eliminar(self, id_usr):
        try:
            usuario = self.buscar_por_id(id_usr)
            
            query = "DELETE FROM usuarios WHERE id = %s"
            filas = self.db.ejecutar_query(query, (id_usr,), commit=True)
            
            if filas > 0:
                print(f"Usuario '{usuario.nombre_usuario}' eliminado")
                return True
            return False
        except UsuarioError:
            raise
        except Error as e:
            raise UsuarioError(f"Error eliminando: {e}")
    
    # Login - verificar usuario y password
    def login(self, nombre, password):
        try:
            # print(f"Intentando login con: {nombre}")  # debug
            usuario = self.buscar_por_nombre(nombre)
            
            if usuario.check_password(password):
                print(f"Login OK: {nombre}")
                return usuario
            else:
                raise UsuarioError("Password incorrecto")
        except UsuarioError as e:
            if "no encontrado" in str(e):
                raise UsuarioError(f"Usuario '{nombre}' no existe")
            raise
        except Exception as e:
            raise UsuarioError(f"Error en login: {e}")

# Codigo viejo que no funciono bien
# def verificar_pass_manual(hash_bd, pass_texto):
#     # esto no servia, mejor usar bcrypt directo
#     return hash_bd == pass_texto
