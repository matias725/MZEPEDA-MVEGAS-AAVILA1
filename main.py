# App principal - EcoTech Solutions
# Sistema con login seguro y consulta de API de calidad del aire

import sys
from modelos import GestorUsuarios, UsuarioError, Usuario
from api import ServicioAPI, APIError
from db import verificar_conexion

# Clase principal de la aplicacion
class AppEcoTech:
    def __init__(self):
        self.gestor = GestorUsuarios()
        self.api = ServicioAPI()
        self.user_actual = None
        self.intentos = 0
        self.max_intentos = 3
    
    # Mostrar banner inicial
    def mostrar_banner(self):
        print("\n" + "=" * 70)
        print("   ECOTECH SOLUTIONS - Sistema de Gestion Ambiental")
        print("=" * 70)
        print("   Programacion Orientada a Objeto Seguro")
        print("=" * 70 + "\n")
    
    # Login con maximo 3 intentos
    def login(self):
        print("LOGIN\n")
        
        while self.intentos < self.max_intentos:
            print(f"Intento {self.intentos + 1} de {self.max_intentos}")
            print("-" * 40)
            
            usuario = input("Usuario: ").strip()
            password = input("Password: ").strip()
            
            if not usuario or not password:
                print("Usuario y password son obligatorios\n")
                continue
            
            try:
                # print(f"Intentando login con {usuario}...")  # debug
                self.user_actual = self.gestor.login(usuario, password)
                
                print(f"\nBienvenido {self.user_actual.nombre_usuario}!")
                print(f"Rol: {self.user_actual.rol}\n")
                return True
                
            except UsuarioError as e:
                self.intentos += 1
                restantes = self.max_intentos - self.intentos
                
                print(f"\nError: {e}")
                
                if restantes > 0:
                    print(f"Te quedan {restantes} intentos\n")
                else:
                    print("\nACCESO DENEGADO: Maximo de intentos alcanzado")
                    print("Cerrando programa...\n")
                    return False
            except Exception as e:
                print(f"\nError inesperado: {e}\n")
                self.intentos += 1
        
        return False
    
    # Menu principal
    def menu_principal(self):
        print("\n" + "=" * 70)
        print("   MENU PRINCIPAL")
        print("=" * 70)
        print("   1. Gestionar Usuarios (CRUD)")
        print("   2. Ver Datos Ambientales (API)")
        print("   3. Salir")
        print("=" * 70)
    
    # Menu de usuarios
    def menu_usuarios(self):
        print("\n" + "-" * 70)
        print("   GESTION DE USUARIOS")
        print("-" * 70)
        print("   1. Crear nuevo usuario")
        print("   2. Buscar usuario")
        print("   3. Listar todos")
        print("   4. Modificar usuario")
        print("   5. Eliminar usuario")
        print("   6. Volver")
        print("-" * 70)
    
    # Loop del menu principal
    def run_menu(self):
        while True:
            self.menu_principal()
            op = input("\nOpcion: ").strip()
            
            if op == '1':
                self.menu_usuarios_loop()
            elif op == '2':
                self.ver_datos_api()
            elif op == '3':
                self.salir()
                break
            else:
                print("Opcion no valida")
    
    # Loop del menu usuarios
    def menu_usuarios_loop(self):
        while True:
            self.menu_usuarios()
            op = input("\nOpcion: ").strip()
            
            if op == '1':
                self.crear_user()
            elif op == '2':
                self.buscar_user()
            elif op == '3':
                self.listar_users()
            elif op == '4':
                self.modificar_user()
            elif op == '5':
                self.eliminar_user()
            elif op == '6':
                break
            else:
                print("Opcion no valida")
    
    # Crear usuario nuevo
    def crear_user(self):
        print("\n--- CREAR USUARIO ---\n")
        
        try:
            nombre = input("Nombre de usuario: ").strip()
            correo = input("Correo: ").strip()
            pw = input("Password: ").strip()
            pw2 = input("Confirmar password: ").strip()
            rol = input("Rol (usuario/administrador) [usuario]: ").strip() or "usuario"
            
            if not all([nombre, correo, pw]):
                print("Todos los campos son obligatorios")
                return
            
            if pw != pw2:
                print("Las passwords no coinciden")
                return
            
            if len(pw) < 6:
                print("Password debe tener al menos 6 caracteres")
                return
            
            # print(f"Creando usuario {nombre}...")  # debug
            nuevo = Usuario(
                nombre_usuario=nombre,
                correo=correo,
                rol=rol,
                password=pw
            )
            
            self.gestor.agregar_usuario(nuevo)
            
        except UsuarioError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Error inesperado: {e}")
    
    # Buscar usuario
    def buscar_user(self):
        print("\n--- BUSCAR USUARIO ---\n")
        
        try:
            nombre = input("Nombre de usuario: ").strip()
            
            if not nombre:
                print("Debes ingresar un nombre")
                return
            
            usr = self.gestor.buscar_por_nombre(nombre)
            
            print("\nUsuario encontrado:")
            print("-" * 50)
            print(f"  ID: {usr.id}")
            print(f"  Usuario: {usr.nombre_usuario}")
            print(f"  Correo: {usr.correo}")
            print(f"  Rol: {usr.rol}")
            print("-" * 50)
            
        except UsuarioError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Error: {e}")
    
    # Listar todos los usuarios
    def listar_users(self):
        print("\n--- LISTADO DE USUARIOS ---\n")
        
        try:
            usuarios = self.gestor.listar_todos()
            
            if not usuarios:
                print("No hay usuarios")
                return
            
            print(f"Total: {len(usuarios)}")
            print("-" * 70)
            print(f"{'ID':<5} {'Usuario':<20} {'Correo':<30} {'Rol':<15}")
            print("-" * 70)
            
            for u in usuarios:
                print(f"{u.id:<5} {u.nombre_usuario:<20} {u.correo:<30} {u.rol:<15}")
            
            print("-" * 70)
            
        except Exception as e:
            print(f"Error: {e}")
    
    def modificar_user(self):
        # Modificar datos de usuario
        print("\n--- MODIFICAR USUARIO ---\n")
        
        try:
            id_usuario = input("ID del usuario: ").strip()
            
            if not id_usuario.isdigit():
                print("El ID debe ser numero")
                return
            
            id_usuario = int(id_usuario)
            
            # buscar el usuario
            usuario = self.gestor.buscar_por_id(id_usuario)
            
            print(f"\nUsuario: {usuario.nombre_usuario}")
            print("deja en blanco si no quieres cambiar\n")
            
            nuevo_correo = input(f"correo [{usuario.correo}]: ").strip()
            nuevo_rol = input(f"rol [{usuario.rol}]: ").strip()
            nueva_pass = input("password [dejar vacio]: ").strip()
            
            # modificar solo si hay algo
            if nuevo_correo or nuevo_rol or nueva_pass:
                self.gestor.modificar(
                    id_usr=id_usuario,
                    nuevo_correo=nuevo_correo if nuevo_correo else None,
                    nuevo_rol=nuevo_rol if nuevo_rol else None,
                    nuevo_pass=nueva_pass if nueva_pass else None
                )
            else:
                print("no se cambio nada")
                
        except UsuarioError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Error: {e}")
    
    def eliminar_user(self):
        # Eliminar usuario
        print("\n--- ELIMINAR USUARIO ---\n")
        
        try:
            id_usuario = input("ID del usuario a eliminar: ").strip()
            
            if not id_usuario.isdigit():
                print("El ID debe ser numero")
                return
            
            id_usuario = int(id_usuario)
            
            # ver si existe
            usuario = self.gestor.buscar_por_id(id_usuario)
            
            # no te puedes eliminar a ti mismo
            if self.user_actual and usuario.id == self.user_actual.id:
                print("No puedes eliminarte a ti mismo")
                return
            
            # confirmar
            confirmacion = input(f"Seguro que quieres borrar a '{usuario.nombre_usuario}'? (s/n): ").strip().lower()
            
            if confirmacion == 's':
                self.gestor.eliminar(id_usuario)
            else:
                print("Cancelado")
                
        except UsuarioError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Error: {e}")
    
    # ========== API ==========
    
    def ver_datos_api(self):
        # Consultar API de calidad del aire
        print("\n--- DATOS AMBIENTALES (API) ---\n")
        
        try:
            ciudad = input("ciudad [Santiago]: ").strip() or "Santiago"
            
            print("\nconsultando...\n")
            self.api.mostrar_datos(ciudad)
            
        except APIError as e:
            print(f"\nError API: {e}")
        except Exception as e:
            print(f"\nError: {e}")
        
        input("\n\nEnter para continuar...")
    
    # ========== SALIDA ==========
    
    def salir(self):
        # salir del programa
        print("\n" + "=" * 70)
        print("   Gracias por usar EcoTech Solutions")
        print("   Juntos construimos un futuro mas verde")
        print("=" * 70 + "\n")
    
    def iniciar(self):
        # inicio del programa
        self.mostrar_banner()
        
        # ver si hay conexion a la base de datos
        print("verificando conexion a BD...")
        if not verificar_conexion():
            print("\nNo se pudo conectar a la BD")
            print("verifica que MySQL este corriendo y el .env")
            sys.exit(1)
        
        print()
        
        # login
        if not self.login():
            sys.exit(1)
        
        # mostrar menu si el login fue ok
        try:
            self.run_menu()
        except KeyboardInterrupt:
            print("\n\nPrograma interrumpido")
            self.salir()
        except Exception as e:
            print(f"\nError: {e}")
            sys.exit(1)


# ============================================
# MAIN
# ============================================

def main():
    # crear app e iniciar
    app = AppEcoTech()
    app.iniciar()


if __name__ == "__main__":
    main()
