# Conexion a MySQL con credenciales del .env
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

class ConexionDB:
    # Clase para manejar la conexion a MySQL
    def __init__(self):
        # Cargar datos de conexion desde .env
        self.host = os.getenv('DB_HOST', 'localhost')
        self.database = os.getenv('DB_NAME', 'pepe123')
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', '')
        self.port = os.getenv('DB_PORT', '3306')
        self.conn = None
    
    # Conectar a la base de datos
    def conectar(self):
        try:
            if self.conn is None or not self.conn.is_connected():
                self.conn = mysql.connector.connect(
                    host=self.host,
                    database=self.database,
                    user=self.user,
                    password=self.password,
                    port=self.port
                )
                if self.conn.is_connected():
                    print("Conectado a MySQL")
                    return self.conn
            else:
                return self.conn
        except Error as e:
            print(f"Error conectando: {e}")
            raise
    
    # Cerrar conexion
    def desconectar(self):
        try:
            if self.conn is not None and self.conn.is_connected():
                self.conn.close()
                print("Conexion cerrada")
        except Error as e:
            print(f"Error cerrando: {e}")
    
    # Obtener cursor para ejecutar queries
    def get_cursor(self):
        try:
            connection = self.conectar()
            return connection.cursor(dictionary=True)
        except Error as e:
            print(f"Error obteniendo cursor: {e}")
            raise
    
    # Ejecutar query en la BD
    def ejecutar_query(self, query, params=None, commit=False):
        cursor = None
        try:
            cursor = self.get_cursor()
            cursor.execute(query, params or ())
            
            if commit:
                self.conn.commit()
                if query.strip().upper().startswith('INSERT'):
                    return cursor.lastrowid
                return cursor.rowcount
            else:
                return cursor.fetchall()
        except Error as e:
            if commit and self.conn:
                self.conn.rollback()
            print(f"Error en query: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

# Instancia global de la conexion (para usarla en todos lados)
db_connection = None

def get_db():
    # Obtener la conexion (crea una sola vez)
    global db_connection
    if db_connection is None:
        db_connection = ConexionDB()
    return db_connection

# Verificar si la conexion funciona
def verificar_conexion():
    try:
        db = get_db()
        db.conectar()
        return True
    except Exception as e:
        print(f"Error verificando conexion: {e}")
        return False
