"""
Interfaz gráfica básica con tkinter para gestionar empleados, departamentos,
proyectos y registros de tiempo.

Nota: la GUI está pensada como un punto de partida funcional para la evaluación.
"""
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import simpledialog
import db
import validaciones
import csv
import os
from typing import Optional


class Aplicacion(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("EcoTech Solutions - Gestión de Empleados")
        self.geometry("800x500")

        # Pestañas
        self.tabs = ttk.Notebook(self)
        self.frame_empleados = ttk.Frame(self.tabs)
        self.frame_departamentos = ttk.Frame(self.tabs)
        self.frame_proyectos = ttk.Frame(self.tabs)
        self.frame_registros = ttk.Frame(self.tabs)

        self.tabs.add(self.frame_empleados, text="Empleados")
        self.tabs.add(self.frame_departamentos, text="Departamentos")
        self.tabs.add(self.frame_proyectos, text="Proyectos")
        self.tabs.add(self.frame_registros, text="Timesheets")
        self.tabs.pack(expand=1, fill="both")

        self._construir_tab_empleados()
        self._construir_tab_departamentos()
        self._construir_tab_proyectos()
        self._construir_tab_registros()

    # ---------------- Empleados ----------------
    def _construir_tab_empleados(self):
        frame = self.frame_empleados

        # Formulario para crear empleado
        formulario = ttk.LabelFrame(frame, text="Crear empleado")
        formulario.pack(fill="x", padx=10, pady=10)

        labels = ["Nombre", "Dirección", "Teléfono", "Email", "Salario", "Contraseña", "Departamento ID"]
        self.entradas = {}
        for i, lbl in enumerate(labels):
            ttk.Label(formulario, text=lbl).grid(row=i, column=0, sticky="w", padx=5, pady=3)
            ent = ttk.Entry(formulario)
            ent.grid(row=i, column=1, sticky="ew", padx=5, pady=3)
            self.entradas[lbl] = ent

        formulario.columnconfigure(1, weight=1)

        ttk.Button(formulario, text="Crear empleado", command=self.crear_empleado).grid(row=len(labels), column=0, columnspan=2, pady=8)

        # Lista de empleados
        lista_frame = ttk.LabelFrame(frame, text="Empleados registrados")
        lista_frame.pack(fill="both", expand=1, padx=10, pady=10)

        self.lista_empleados = tk.Listbox(lista_frame)
        self.lista_empleados.pack(side="left", fill="both", expand=1)
        scrollbar = ttk.Scrollbar(lista_frame, orient="vertical", command=self.lista_empleados.yview)
        scrollbar.pack(side="right", fill="y")
        self.lista_empleados.config(yscrollcommand=scrollbar.set)

        ttk.Button(frame, text="Refrescar lista", command=self.refrescar_lista_empleados).pack(pady=5)
        # Botones para acciones sobre empleado seleccionado
        acciones_frame = ttk.Frame(frame)
        acciones_frame.pack(pady=4)
        ttk.Button(acciones_frame, text="Editar seleccionado", command=self.editar_empleado_seleccionado).pack(side="left", padx=6)
        ttk.Button(acciones_frame, text="Eliminar seleccionado", command=self.eliminar_empleado_seleccionado).pack(side="left", padx=6)

        self.refrescar_lista_empleados()

    def crear_empleado(self):
        nombre = self.entradas["Nombre"].get()
        direccion = self.entradas["Dirección"].get()
        telefono = self.entradas["Teléfono"].get()
        email = self.entradas["Email"].get()
        salario = self.entradas["Salario"].get()
        contrasena = self.entradas["Contraseña"].get()
        departamento_id = self.entradas["Departamento ID"].get() or None

        # Validaciones
        if not validaciones.validar_no_vacio(nombre):
            messagebox.showerror("Error", "El nombre es obligatorio.")
            return
        if not validaciones.validar_email(email):
            messagebox.showerror("Error", "El email no tiene un formato válido.")
            return
        try:
            salario_f = float(salario)
        except Exception:
            messagebox.showerror("Error", "Salario inválido.")
            return

        if not contrasena:
            messagebox.showerror("Error", "La contraseña es obligatoria.")
            return

        # Hash de contraseña
        hash_pw = db.hash_contrasena(contrasena)

        # convertir departamento_id a int o None
        if departamento_id:
            try:
                departamento_id = int(departamento_id)
            except Exception:
                messagebox.showerror("Error", "Departamento ID inválido.")
                return
        else:
            departamento_id = None

        try:
            db.agregar_empleado(nombre, direccion, telefono, email, salario_f, hash_pw, departamento_id)
            messagebox.showinfo("Éxito", "Empleado creado correctamente.")
            self.refrescar_lista_empleados()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear empleado: {e}")

    def _parsear_id_desde_linea(self, linea: str) -> Optional[int]:
        """Parsea una línea de la lista (formato '#id - ...') y devuelve el id como int."""
        try:
            if linea.startswith("#"):
                parte = linea.split("-", 1)[0].strip()
                return int(parte.lstrip("#"))
        except Exception:
            return None
        return None

    def editar_empleado_seleccionado(self):
        sel = self.lista_empleados.curselection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un empleado para editar.")
            return
        linea = self.lista_empleados.get(sel[0])
        emp_id = self._parsear_id_desde_linea(linea)
        if emp_id is None:
            messagebox.showerror("Error", "No se pudo obtener el ID del empleado seleccionado.")
            return

        datos = db.obtener_empleado_por_email(linea.split("|")[1].split("-")[-1].strip())
        # Si no conseguimos por email, obtendremos desde la lista completa
        if not datos:
            # buscar en listar_empleados
            for e in db.listar_empleados():
                if e[0] == emp_id:
                    datos = e
                    break

        if not datos:
            messagebox.showerror("Error", "No se encontraron datos del empleado.")
            return

        # Datos: (id, nombre, direccion, telefono, email, salario, password_hash, departamento_id?) or listar_empleados form
        # Intentar adaptar
        if len(datos) >= 7 and isinstance(datos[0], int):
            # usar obtener_por_email ruta (full)
            try:
                emp_full = db.obtener_empleado_por_email(datos[4])
            except Exception:
                emp_full = None
        else:
            emp_full = None

        # Build editor
        editor = tk.Toplevel(self)
        editor.title("Editar empleado")

        # Obtener valores base
        # Intentar leer desde listar_empleados si emp_full no proporciona todo
        if emp_full:
            _, nombre, direccion, telefono, email, salario, password_hash, departamento_id = emp_full
        else:
            # fallback
            for e in db.listar_empleados():
                if e[0] == emp_id:
                    _, nombre, direccion, telefono, email, salario, departamento_id = e
                    password_hash = None
                    break

        campos = {
            'Nombre': nombre,
            'Dirección': direccion,
            'Teléfono': telefono,
            'Email': email,
            'Salario': str(salario),
            'Departamento ID': str(departamento_id or '')
        }

        entradas = {}
        for i, (k, v) in enumerate(campos.items()):
            ttk.Label(editor, text=k).grid(row=i, column=0, sticky='w', padx=6, pady=3)
            ent = ttk.Entry(editor)
            ent.insert(0, v)
            ent.grid(row=i, column=1, sticky='ew', padx=6, pady=3)
            entradas[k] = ent

        ttk.Label(editor, text="Nueva contraseña (opcional)").grid(row=len(campos), column=0, sticky='w', padx=6, pady=3)
        ent_pw = ttk.Entry(editor)
        ent_pw.grid(row=len(campos), column=1, sticky='ew', padx=6, pady=3)

        def guardar_cambios():
            try:
                nuevo_nombre = entradas['Nombre'].get()
                nueva_dir = entradas['Dirección'].get()
                nuevo_tel = entradas['Teléfono'].get()
                nuevo_email = entradas['Email'].get()
                nuevo_sal = float(entradas['Salario'].get())
                nuevo_dep = entradas['Departamento ID'].get() or None
                if nuevo_dep is not None:
                    nuevo_dep = int(nuevo_dep)

                db.actualizar_empleado(emp_id, nuevo_nombre, nueva_dir, nuevo_tel, nuevo_email, nuevo_sal, nuevo_dep)
                nueva_pw = ent_pw.get()
                if nueva_pw:
                    db.actualizar_contrasena_empleado(emp_id, nueva_pw)
                messagebox.showinfo('Éxito', 'Empleado actualizado')
                editor.destroy()
                self.refrescar_lista_empleados()
            except Exception as err:
                messagebox.showerror('Error', f'No se pudo actualizar: {err}')

        ttk.Button(editor, text='Guardar', command=guardar_cambios).grid(row=len(campos)+1, column=0, columnspan=2, pady=8)

    def eliminar_empleado_seleccionado(self):
        sel = self.lista_empleados.curselection()
        if not sel:
            messagebox.showwarning('Atención', 'Seleccione un empleado para eliminar.')
            return
        linea = self.lista_empleados.get(sel[0])
        emp_id = self._parsear_id_desde_linea(linea)
        if emp_id is None:
            messagebox.showerror('Error', 'No se pudo obtener el ID del empleado seleccionado.')
            return

        if not messagebox.askyesno('Confirmar', f'¿Eliminar empleado #{emp_id}? Esta acción es irreversible.'):
            return
        try:
            db.eliminar_empleado(emp_id)
            messagebox.showinfo('Éxito', 'Empleado eliminado.')
            self.refrescar_lista_empleados()
        except Exception as e:
            messagebox.showerror('Error', f'No se pudo eliminar empleado: {e}')

    def refrescar_lista_empleados(self):
        self.lista_empleados.delete(0, tk.END)
        try:
            empleados = db.listar_empleados()
            for emp in empleados:
                id_e, nombre, direccion, telefono, email, salario, dep = emp
                texto = f"#{id_e} - {nombre} | {email} | Salario: {salario} | Dep: {dep or 'N/A'}"
                self.lista_empleados.insert(tk.END, texto)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo listar empleados: {e}")

    # ---------------- Departamentos ----------------
    def _construir_tab_departamentos(self):
        frame = self.frame_departamentos
        formulario = ttk.Frame(frame)
        formulario.pack(fill="x", padx=10, pady=10)

        ttk.Label(formulario, text="Nombre del departamento").grid(row=0, column=0, sticky="w")
        self.ent_dep_nombre = ttk.Entry(formulario)
        self.ent_dep_nombre.grid(row=0, column=1, sticky="ew")
        formulario.columnconfigure(1, weight=1)
        ttk.Button(formulario, text="Crear departamento", command=self.crear_departamento).grid(row=1, column=0, columnspan=2, pady=6)

        self.lista_departamentos = tk.Listbox(frame)
        self.lista_departamentos.pack(fill="both", expand=1, padx=10, pady=10)
        botones_dep = ttk.Frame(frame)
        botones_dep.pack()
        ttk.Button(botones_dep, text="Refrescar departamentos", command=self.refrescar_departamentos).pack(side="left", padx=4)
        ttk.Button(botones_dep, text="Asignar gerente", command=self.asignar_gerente_seleccionado).pack(side="left", padx=4)
        ttk.Button(botones_dep, text="Eliminar departamento", command=self.eliminar_departamento_seleccionado).pack(side="left", padx=4)
        self.refrescar_departamentos()

    def crear_departamento(self):
        nombre = self.ent_dep_nombre.get()
        if not validaciones.validar_no_vacio(nombre):
            messagebox.showerror("Error", "El nombre del departamento no puede estar vacío.")
            return
        try:
            db.agregar_departamento(nombre)
            messagebox.showinfo("Éxito", "Departamento creado.")
            self.refrescar_departamentos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear departamento: {e}")

    def refrescar_departamentos(self):
        self.lista_departamentos.delete(0, tk.END)
        for dep in db.listar_departamentos():
            id_d, nombre, id_gerente = dep
            self.lista_departamentos.insert(tk.END, f"#{id_d} - {nombre} | Gerente: {id_gerente or 'N/A'}")

    def asignar_gerente_seleccionado(self):
        sel = self.lista_departamentos.curselection()
        if not sel:
            messagebox.showwarning('Atención', 'Seleccione un departamento.')
            return
        linea = self.lista_departamentos.get(sel[0])
        try:
            id_dep = int(linea.split('-')[0].strip().lstrip('#'))
        except Exception:
            messagebox.showerror('Error', 'No se pudo obtener el ID del departamento.')
            return

        gerente_id = simpledialog.askinteger('Gerente', 'Ingrese ID de empleado que será gerente (vacío para eliminar):', parent=self)
        try:
            db.asignar_gerente_departamento(id_dep, gerente_id)
            messagebox.showinfo('Éxito', 'Gerente asignado.')
            self.refrescar_departamentos()
        except Exception as e:
            messagebox.showerror('Error', f'No se pudo asignar gerente: {e}')

    def eliminar_departamento_seleccionado(self):
        sel = self.lista_departamentos.curselection()
        if not sel:
            messagebox.showwarning('Atención', 'Seleccione un departamento para eliminar.')
            return
        linea = self.lista_departamentos.get(sel[0])
        try:
            id_dep = int(linea.split('-')[0].strip().lstrip('#'))
        except Exception:
            messagebox.showerror('Error', 'No se pudo obtener el ID del departamento.')
            return

        if not messagebox.askyesno('Confirmar', f'¿Eliminar departamento #{id_dep}?'):
            return
        try:
            db.eliminar_departamento(id_dep)
            messagebox.showinfo('Éxito', 'Departamento eliminado.')
            self.refrescar_departamentos()
            self.refrescar_lista_empleados()
        except Exception as e:
            messagebox.showerror('Error', f'No se pudo eliminar departamento: {e}')

    # ---------------- Proyectos ----------------
    def _construir_tab_proyectos(self):
        frame = self.frame_proyectos
        formulario = ttk.Frame(frame)
        formulario.pack(fill="x", padx=10, pady=10)

        ttk.Label(formulario, text="Nombre del proyecto").grid(row=0, column=0, sticky="w")
        self.ent_proj_nombre = ttk.Entry(formulario)
        self.ent_proj_nombre.grid(row=0, column=1, sticky="ew")
        ttk.Label(formulario, text="Descripción").grid(row=1, column=0, sticky="w")
        self.ent_proj_desc = ttk.Entry(formulario)
        self.ent_proj_desc.grid(row=1, column=1, sticky="ew")
        formulario.columnconfigure(1, weight=1)
        ttk.Button(formulario, text="Crear proyecto", command=self.crear_proyecto).grid(row=2, column=0, columnspan=2, pady=6)

        self.lista_proyectos = tk.Listbox(frame)
        self.lista_proyectos.pack(fill="both", expand=1, padx=10, pady=10)
        ttk.Button(frame, text="Refrescar proyectos", command=self.refrescar_proyectos).pack()
        self.refrescar_proyectos()

    def crear_proyecto(self):
        nombre = self.ent_proj_nombre.get()
        descripcion = self.ent_proj_desc.get()
        if not validaciones.validar_no_vacio(nombre):
            messagebox.showerror("Error", "Nombre de proyecto obligatorio.")
            return
        try:
            db.agregar_proyecto(nombre, descripcion)
            messagebox.showinfo("Éxito", "Proyecto creado.")
            self.refrescar_proyectos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear proyecto: {e}")

    def refrescar_proyectos(self):
        self.lista_proyectos.delete(0, tk.END)
        for p in db.listar_proyectos():
            id_p, nombre, desc = p
            self.lista_proyectos.insert(tk.END, f"#{id_p} - {nombre} | {desc}")

    # ---------------- Registros de tiempo ----------------
    def _construir_tab_registros(self):
        frame = self.frame_registros
        formulario = ttk.LabelFrame(frame, text="Registrar tiempo")
        formulario.pack(fill="x", padx=10, pady=10)

        ttk.Label(formulario, text="Empleado ID").grid(row=0, column=0, sticky="w")
        self.ent_reg_emp = ttk.Entry(formulario)
        self.ent_reg_emp.grid(row=0, column=1, sticky="ew")
        ttk.Label(formulario, text="Proyecto ID").grid(row=1, column=0, sticky="w")
        self.ent_reg_proj = ttk.Entry(formulario)
        self.ent_reg_proj.grid(row=1, column=1, sticky="ew")
        ttk.Label(formulario, text="Fecha (YYYY-MM-DD)").grid(row=2, column=0, sticky="w")
        self.ent_reg_fecha = ttk.Entry(formulario)
        self.ent_reg_fecha.grid(row=2, column=1, sticky="ew")
        ttk.Label(formulario, text="Horas").grid(row=3, column=0, sticky="w")
        self.ent_reg_horas = ttk.Entry(formulario)
        self.ent_reg_horas.grid(row=3, column=1, sticky="ew")

        formulario.columnconfigure(1, weight=1)
        ttk.Button(formulario, text="Registrar horas", command=self.crear_registro).grid(row=4, column=0, columnspan=2, pady=6)

        self.lista_registros = tk.Listbox(frame)
        self.lista_registros.pack(fill="both", expand=1, padx=10, pady=10)
        botones_reg = ttk.Frame(frame)
        botones_reg.pack()
        ttk.Button(botones_reg, text="Refrescar registros", command=self.refrescar_registros).pack(side="left", padx=4)
        ttk.Button(botones_reg, text="Exportar Reporte", command=self.exportar_reporte).pack(side="left", padx=4)
        self.refrescar_registros()

    def crear_registro(self):
        emp = self.ent_reg_emp.get()
        proj = self.ent_reg_proj.get()
        fecha = self.ent_reg_fecha.get()
        horas = self.ent_reg_horas.get()

        try:
            emp_id = int(emp)
            proj_id = int(proj)
        except Exception:
            messagebox.showerror("Error", "Empleado ID y Proyecto ID deben ser enteros.")
            return

        if not validaciones.validar_fecha_iso(fecha):
            messagebox.showerror("Error", "Fecha inválida. Use formato YYYY-MM-DD.")
            return

        if not validaciones.validar_horas(horas):
            messagebox.showerror("Error", "Horas inválidas. Deben estar entre 0 y 24.")
            return

        try:
            db.agregar_registro_tiempo(emp_id, proj_id, fecha, float(horas))
            messagebox.showinfo("Éxito", "Registro agregado.")
            self.refrescar_registros()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar registro: {e}")

    def refrescar_registros(self):
        self.lista_registros.delete(0, tk.END)
        for r in db.listar_registros():
            idr, emp, proj, fecha, horas = r
            self.lista_registros.insert(tk.END, f"#{idr} - Emp:{emp} | Proj:{proj} | {fecha} | {horas}h")

    def exportar_reporte(self):
        """Exporta todos los registros de tiempo a `reporte_horas.csv` en el directorio del proyecto.

        Usa la librería estándar `csv` para generar un archivo que pueda abrirse en Excel.
        """
        try:
            registros = db.listar_registros()
            ruta = os.path.join(os.path.dirname(__file__), "reporte_horas.csv")
            with open(ruta, mode='w', newline='', encoding='utf-8') as f:
                escritor = csv.writer(f)
                escritor.writerow(["id", "empleado_id", "proyecto_id", "fecha", "horas"])
                for reg in registros:
                    escritor.writerow(reg)
            messagebox.showinfo("Exportado", f"Reporte exportado correctamente a:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar el reporte: {e}")


def iniciar_aplicacion():
    app = Aplicacion()
    app.mainloop()


class Login(tk.Tk):
    """Ventana de login que solicita email y contraseña.

    Al autenticarse correctamente, destruye la ventana de login y abre la
    aplicación principal `Aplicacion`.
    """

    def __init__(self):
        super().__init__()
        self.title("Login - EcoTech Solutions")
        self.geometry("350x180")

        frame = ttk.Frame(self, padding=12)
        frame.pack(expand=1, fill="both")

        ttk.Label(frame, text="Email:").grid(row=0, column=0, sticky="w", pady=6)
        self.ent_email = ttk.Entry(frame)
        self.ent_email.grid(row=0, column=1, sticky="ew", padx=6)

        ttk.Label(frame, text="Contraseña:").grid(row=1, column=0, sticky="w", pady=6)
        self.ent_password = ttk.Entry(frame, show='*')
        self.ent_password.grid(row=1, column=1, sticky="ew", padx=6)

        frame.columnconfigure(1, weight=1)

        botones = ttk.Frame(frame)
        botones.grid(row=2, column=0, columnspan=2, pady=12)
        ttk.Button(botones, text="Ingresar", command=self.intentar_ingresar).pack(side="left", padx=6)
        ttk.Button(botones, text="Salir", command=self.destroy).pack(side="left", padx=6)

        # Bind Enter key to intentar_ingresar
        self.bind('<Return>', lambda event: self.intentar_ingresar())

    def intentar_ingresar(self):
        """Maneja el intento de login: valida email y contraseña contra la BD."""
        email = self.ent_email.get().strip()
        contrasena = self.ent_password.get()

        if not validaciones.validar_no_vacio(email) or not validaciones.validar_no_vacio(contrasena):
            messagebox.showerror("Error", "Email y contraseña son obligatorios.")
            return

        try:
            usuario = db.obtener_empleado_por_email(email)
        except Exception as e:
            messagebox.showerror("Error", f"Error al consultar la base de datos: {e}")
            return

        if not usuario:
            messagebox.showerror("Error", "Usuario no encontrado.")
            return

        # La tupla devuelta por obtener_empleado_por_email incluye password_hash en la posición 6
        try:
            password_hash = usuario[6]
        except Exception:
            messagebox.showerror("Error", "Registro de usuario inválido.")
            return

        if db.verificar_contrasena(contrasena, password_hash):
            # Login correcto: cerrar ventana de login e iniciar la aplicación principal
            self.destroy()
            iniciar_aplicacion()
        else:
            messagebox.showerror("Error", "Contraseña incorrecta.")


if __name__ == "__main__":
    # Si se ejecuta directamente, abrir la ventana de login primero
    login = Login()
    login.mainloop()



if __name__ == "__main__":
    iniciar_aplicacion()
