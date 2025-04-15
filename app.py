import customtkinter as ctk
import mysql.connector
from tkinter import messagebox
import re
from datetime import date
from PIL import Image
import os
import sys



ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Conexión
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  
    database="taller_mecanico"
)
cursor = conn.cursor()

#---------------------------------FUNCIONES----------------------------------------------
def actualizar_cliente(id_cliente, nombre, telefono, vehiculo, placas):
    cliente = buscar_cliente(id_cliente=id_cliente)
    
    if not cliente:
        messagebox.showerror("Error", "Cliente no encontrado.")
        return

    
    nombre = nombre.strip() or cliente[1]
    telefono = telefono.strip() or cliente[2]
    vehiculo = vehiculo.strip() or cliente[3]
    placas = placas.strip().upper() or cliente[4]

    
    if not telefono.isdigit() or not (7 <= len(telefono) <= 15):
        messagebox.showerror("Telefono invalido", "Debe contener solo numeros (7 a 15 dígitos).")
        return

    if not re.match(r'^[A-Z]{3}-\d{4}$', placas):
        messagebox.showerror("Placas invalidas", "Formato incorrecto. Ejemplo: ABC-1234.")
        return

    
    if placas != cliente[4]:
        cursor.execute("SELECT * FROM clientes WHERE placas = %s", (placas,))
        duplicado = cursor.fetchone()
        if duplicado:
            messagebox.showerror("Error", f"Ya existe un cliente con las placas {placas}.")
            return

  
    try:
        cursor.execute("""
            UPDATE clientes
            SET nombre = %s, telefono = %s, vehiculo = %s, placas = %s
            WHERE id = %s
        """, (nombre, telefono, vehiculo, placas, id_cliente))
        conn.commit()
        messagebox.showinfo("✅ Exito", "Cliente actualizado correctamente.")
    except Exception as e:
        messagebox.showerror("Error en la base de datos", str(e))
def eliminar_cliente(id_cliente):
   
    try:
        id_cliente = int(id_cliente)
        if id_cliente <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("ID invalido", "El ID debe ser un numero entero positivo.")
        return

    
    cliente = buscar_cliente(id_cliente=id_cliente)
    if not cliente:
        messagebox.showerror("No encontrado", f"No se encontro un cliente con ID {id_cliente}.")
        return

    
    confirm = messagebox.askyesno("¿Estás seguro?", 
                                  f"¿Deseas eliminar al cliente:\n\n🧾 Nombre: {cliente[1]}\n📞 Teléfono: {cliente[2]}\n🚗 Vehículo: {cliente[3]}\n🔢 Placas: {cliente[4]}\n\nEsta acción no se puede deshacer.")
    if not confirm:
        return

    
    try:
        cursor.execute("DELETE FROM clientes WHERE id = %s", (id_cliente,))
        conn.commit()
        messagebox.showinfo("✅ Eliminado", f"Cliente '{cliente[1]}' eliminado correctamente.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo eliminar el cliente.\n\nDetalle: {e}")

def ver_clientes():
    cursor.execute("SELECT * FROM clientes")
    clientes = cursor.fetchall()

    ventana = ctk.CTkToplevel()
    ventana.title("📋 Lista de Clientes")
    ventana.geometry("800x500")
    ventana.resizable(False, False)

   
    titulo = ctk.CTkLabel(
        ventana,
        text="👥 Clientes Registrados",
        font=("Arial", 28, "bold"),
        text_color="#2c3e50"
    )
    titulo.pack(pady=(20, 10))

   
    frame = ctk.CTkFrame(ventana, width=750, height=400, corner_radius=15)
    frame.pack(pady=10, padx=20)
    frame.pack_propagate(False)

    if clientes:
       
        texto = ctk.CTkTextbox(
            frame,
            width=720,
            height=360,
            corner_radius=10,
            font=("Consolas", 13),
            border_width=2,
            border_color="#2980b9",
            text_color="#2c3e50",
        )
        texto.pack(pady=10)

        texto.insert("end", f"{'🆔':<5} {'Nombre':<22} {'📞 Teléfono':<17} {'🚗 Vehículo':<17} {'🔢 Placas':<10}\n")
        texto.insert("end", "-" * 75 + "\n")
        for cliente in clientes:
            texto.insert(
                "end",
                f"{str(cliente[0]):<5} {cliente[1]:<22} {cliente[2]:<17} {cliente[3]:<17} {cliente[4]:<10}\n"
            )
        texto.configure(state="disabled")
    else:
        sin_clientes = ctk.CTkLabel(
            frame,
            text="❌ No hay clientes registrados.",
            font=("Arial", 16),
            text_color="red"
        )
        sin_clientes.pack(pady=50)


def buscar_cliente(id_cliente=None, placas=None):
    if id_cliente:
        try:
            id_cliente = int(id_cliente)  
        except ValueError:
            messagebox.showerror("Error", "El ID del cliente debe ser un numero.")
            return None
        cursor.execute("SELECT * FROM clientes WHERE id = %s", (id_cliente,))
        return cursor.fetchone()
    
    elif placas:
        placas = placas.strip().upper()
        if not placas:
            messagebox.showerror("Error", "Las placas no pueden estar vacías.")
            return None
        cursor.execute("SELECT * FROM clientes WHERE placas = %s", (placas,))
        return cursor.fetchone()
    
    else:
        messagebox.showwarning("Atención", "Debes ingresar un ID o unas placas para buscar.")
        return None
#-------------------------Ventanas-----------------------------
def ventana_actualizar():
    v = ctk.CTkToplevel()
    v.title("Actualizar Cliente")
    v.geometry("500x620")
    v.resizable(False, False)
    v.configure(fg_color="#f0f0f0")

   
    entry_width = 380
    fuente_titulo = ("Segoe UI", 22, "bold")
    fuente_label = ("Segoe UI", 14)
    fuente_info = ("Segoe UI", 11, "italic")

    
    ctk.CTkLabel(v, text="🛠️ ACTUALIZAR CLIENTE", font=fuente_titulo, text_color="#2b6cb0").pack(pady=15)

    frame = ctk.CTkFrame(v, fg_color="#ffffff", corner_radius=15)
    frame.pack(pady=10, padx=20, fill="both", expand=True)

   
    ctk.CTkLabel(frame, text="🔍 ID del Cliente:", font=fuente_label).pack(anchor="w", padx=20, pady=(15, 0))
    id_cliente = ctk.CTkEntry(frame, placeholder_text="Ej: 101", width=entry_width)
    id_cliente.pack(pady=5)

    
    ctk.CTkButton(frame, text="🔎 Buscar Cliente", width=entry_width, fg_color="#2b6cb0", hover_color="#1a4a80",
                  command=lambda: rellenar_datos()).pack(pady=10)

    
    ctk.CTkLabel(frame, text="👤 Nuevo Nombre:", font=fuente_label).pack(anchor="w", padx=20, pady=(10, 0))
    nombre = ctk.CTkEntry(frame, placeholder_text="Nombre completo", width=entry_width)
    nombre.pack(pady=5)

    ctk.CTkLabel(frame, text="📞 Nuevo Teléfono:", font=fuente_label).pack(anchor="w", padx=20, pady=(10, 0))
    telefono = ctk.CTkEntry(frame, placeholder_text="Solo numeros", width=entry_width)
    telefono.pack(pady=5)

    ctk.CTkLabel(frame, text="🚘 Nuevo Vehiculo:", font=fuente_label).pack(anchor="w", padx=20, pady=(10, 0))
    vehiculo = ctk.CTkEntry(frame, placeholder_text="Marca y modelo", width=entry_width)
    vehiculo.pack(pady=5)

    ctk.CTkLabel(frame, text="🔖 Nuevas Placas:", font=fuente_label).pack(anchor="w", padx=20, pady=(10, 0))
    placas = ctk.CTkEntry(frame, placeholder_text="Formato: ABC-1234", width=entry_width)
    placas.pack(pady=5)

    def limpiar():
        nombre.delete(0, 'end')
        telefono.delete(0, 'end')
        vehiculo.delete(0, 'end')
        placas.delete(0, 'end')

    def rellenar_datos():
        try:
            id_val = int(id_cliente.get())
        except ValueError:
            messagebox.showerror("❌ Error", "El ID debe ser un número entero.")
            return

        cliente = buscar_cliente(id_cliente=id_val)
        if cliente:
            nombre.delete(0, 'end')
            nombre.insert(0, cliente[1])
            telefono.delete(0, 'end')
            telefono.insert(0, cliente[2])
            vehiculo.delete(0, 'end')
            vehiculo.insert(0, cliente[3])
            placas.delete(0, 'end')
            placas.insert(0, cliente[4])
        else:
            messagebox.showerror("🔍 Cliente no encontrado", "No existe un cliente con ese ID.")

    def ejecutar_actualizacion():
        try:
            id_val = int(id_cliente.get())
        except ValueError:
            messagebox.showerror("❌ Error", "El ID debe ser un número.")
            return

        nuevo_nombre = nombre.get().strip()
        nuevo_telefono = telefono.get().strip()
        nuevo_vehiculo = vehiculo.get().strip()
        nuevas_placas = placas.get().strip().upper()

        if not all([nuevo_nombre, nuevo_telefono, nuevo_vehiculo, nuevas_placas]):
            messagebox.showerror("⚠️ Campos Vacíos", "Debes completar todos los campos.")
            return

        if not nuevo_telefono.isdigit() or not (7 <= len(nuevo_telefono) <= 15):
            messagebox.showerror("📞 Teléfono Inválido", "Debe contener solo números (7 a 15 dígitos).")
            return

        if not re.match(r'^[A-Z]{3}-\d{4}$', nuevas_placas):
            messagebox.showerror("🔖 Placas Inválidas", "Formato incorrecto. Ejemplo: ABC-1234.")
            return

        cliente = buscar_cliente(id_cliente=id_val)
        if not cliente:
            messagebox.showerror("❌ Error", "Cliente no encontrado.")
            return

        actualizar_cliente(id_val, nuevo_nombre, nuevo_telefono, nuevo_vehiculo, nuevas_placas)
        messagebox.showinfo("✅ Éxito", "Cliente actualizado correctamente.")
        v.destroy()

   
    ctk.CTkButton(v, text="💾 ACTUALIZAR CLIENTE", width=entry_width, height=40,
                  font=("Segoe UI", 15, "bold"), fg_color="#228B22", hover_color="#196f1d",
                  command=ejecutar_actualizacion).pack(pady=15)

   
    ctk.CTkButton(v, text="🧹 Limpiar Campos", width=entry_width, fg_color="#6c757d", hover_color="#495057",
                  command=limpiar).pack(pady=5)

    
    ctk.CTkLabel(v, text="* Formato placas: ABC-1234", font=fuente_info, text_color="gray").pack(pady=5)


def ventana_agregar():
    v = ctk.CTkToplevel()
    v.title("🧾 Registro de Cliente")
    v.geometry("480x520")
    v.resizable(False, False)

    # Colores y fuente
    font_title = ("Arial", 20, "bold")
    font_label = ("Arial", 14)
    entry_width = 350

    ctk.CTkLabel(v, text="🚗 Nuevo Cliente", font=font_title).pack(pady=15)

  
    frame_form = ctk.CTkFrame(v, fg_color="transparent")
    frame_form.pack(pady=5)

    ctk.CTkLabel(frame_form, text="👤 Nombre completo:", font=font_label).pack(anchor="w", padx=20)
    nombre = ctk.CTkEntry(frame_form, placeholder_text="Ej: Juan Pérez", width=entry_width)
    nombre.pack(pady=5)

    ctk.CTkLabel(frame_form, text="📞 Teléfono:", font=font_label).pack(anchor="w", padx=20)
    telefono = ctk.CTkEntry(frame_form, placeholder_text="Solo números", width=entry_width)
    telefono.pack(pady=5)

    ctk.CTkLabel(frame_form, text="🚘 Vehículo:", font=font_label).pack(anchor="w", padx=20)
    vehiculo = ctk.CTkEntry(frame_form, placeholder_text="Ej: Nissan Versa", width=entry_width)
    vehiculo.pack(pady=5)

    ctk.CTkLabel(frame_form, text="🔖 Placas (ABC-1234):", font=font_label).pack(anchor="w", padx=20)
    placas = ctk.CTkEntry(frame_form, placeholder_text="Ej: ABC-1234", width=entry_width)
    placas.pack(pady=5)

    def limpiar():
        nombre.delete(0, 'end')
        telefono.delete(0, 'end')
        vehiculo.delete(0, 'end')
        placas.delete(0, 'end')

    
    def guardar():
        nombre_val = nombre.get().strip()
        telefono_val = telefono.get().strip()
        vehiculo_val = vehiculo.get().strip()
        placas_val = placas.get().strip().upper()

        
        if not all([nombre_val, telefono_val, vehiculo_val, placas_val]):
            messagebox.showerror("❌ Campos incompletos", "Todos los campos son obligatorios.")
            return

        if not telefono_val.isdigit() or not (7 <= len(telefono_val) <= 15):
            messagebox.showerror("📞 Teléfono inválido", "Debe contener solo números entre 7 y 15 dígitos.")
            return

        if not re.match(r'^[A-Z]{3}-\d{4}$', placas_val):
            messagebox.showerror("🔖 Placas inválidas", "Formato correcto: ABC-1234 (3 letras - 4 números)")
            return

        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="taller_mecanico"
            )
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM clientes WHERE placas = %s", (placas_val,))
            if cursor.fetchone():
                messagebox.showerror("⚠️ Cliente existente", f"Ya existe un cliente con las placas {placas_val}.")
                conn.close()
                return

            cursor.execute(
                "INSERT INTO clientes (nombre, telefono, vehiculo, placas) VALUES (%s, %s, %s, %s)",
                (nombre_val, telefono_val, vehiculo_val, placas_val)
            )
            conn.commit()
            conn.close()

            messagebox.showinfo("✅ Éxito", "Cliente agregado correctamente.")
            v.destroy()

        except Exception as e:
            messagebox.showerror("💥 Error inesperado", f"Ocurrió un error:\n{e}")


    boton_guardar = ctk.CTkButton(v, text="💾 Guardar Cliente", width=entry_width, command=guardar)
    boton_guardar.pack(pady=15)

    boton_limpiar = ctk.CTkButton(v, text="🧹 Limpiar Campos", fg_color="#444", hover_color="#555", width=entry_width, command=limpiar)
    boton_limpiar.pack(pady=5)

    ctk.CTkLabel(v, text="* Las placas deben ser únicas y con formato correcto", font=("Arial", 11, "italic")).pack(pady=10)

def ventana_actualizar():
    v = ctk.CTkToplevel()
    v.title("🔧 Actualizar Cliente")
    v.geometry("480x600")
    v.resizable(False, False)

    font_title = ("Arial", 20, "bold")
    font_label = ("Arial", 14)
    entry_width = 350

    ctk.CTkLabel(v, text="✏️ Modificar Cliente", font=font_title).pack(pady=15)

    frame = ctk.CTkFrame(v, fg_color="transparent")
    frame.pack(pady=5)

    ctk.CTkLabel(frame, text="🔎 ID del Cliente:", font=font_label).pack(anchor="w", padx=20)
    id_cliente = ctk.CTkEntry(frame, placeholder_text="Ej: 3", width=entry_width)
    id_cliente.pack(pady=5)

    ctk.CTkButton(frame, text="🔍 Buscar Cliente", command=lambda: rellenar_datos()).pack(pady=10)

    ctk.CTkLabel(frame, text="👤 Nuevo Nombre:", font=font_label).pack(anchor="w", padx=20)
    nombre = ctk.CTkEntry(frame, placeholder_text="Nombre completo", width=entry_width)
    nombre.pack(pady=5)

    ctk.CTkLabel(frame, text="📞 Nuevo Teléfono:", font=font_label).pack(anchor="w", padx=20)
    telefono = ctk.CTkEntry(frame, placeholder_text="Solo números", width=entry_width)
    telefono.pack(pady=5)

    ctk.CTkLabel(frame, text="🚘 Nuevo Vehículo:", font=font_label).pack(anchor="w", padx=20)
    vehiculo = ctk.CTkEntry(frame, placeholder_text="Marca y modelo", width=entry_width)
    vehiculo.pack(pady=5)

    ctk.CTkLabel(frame, text="🔖 Nuevas Placas:", font=font_label).pack(anchor="w", padx=20)
    placas = ctk.CTkEntry(frame, placeholder_text="Formato: ABC-1234", width=entry_width)
    placas.pack(pady=5)

    def limpiar():
        nombre.delete(0, 'end')
        telefono.delete(0, 'end')
        vehiculo.delete(0, 'end')
        placas.delete(0, 'end')

    def rellenar_datos():
        try:
            id_val = int(id_cliente.get())
        except ValueError:
            messagebox.showerror("❌ Error", "El ID debe ser un número.")
            return

        cliente = buscar_cliente(id_cliente=id_val)
        if cliente:
            nombre.delete(0, 'end')
            nombre.insert(0, cliente[1])
            telefono.delete(0, 'end')
            telefono.insert(0, cliente[2])
            vehiculo.delete(0, 'end')
            vehiculo.insert(0, cliente[3])
            placas.delete(0, 'end')
            placas.insert(0, cliente[4])
        else:
            messagebox.showerror("🔍 Cliente no encontrado", "No existe un cliente con ese ID.")

    def ejecutar_actualizacion():
        try:
            id_val = int(id_cliente.get())
        except ValueError:
            messagebox.showerror("❌ Error", "El ID debe ser un número.")
            return

        nuevo_nombre = nombre.get().strip()
        nuevo_telefono = telefono.get().strip()
        nuevo_vehiculo = vehiculo.get().strip()
        nuevas_placas = placas.get().strip().upper()

        if not all([nuevo_nombre, nuevo_telefono, nuevo_vehiculo, nuevas_placas]):
            messagebox.showerror("⚠️ Campos incompletos", "Debes completar todos los campos.")
            return

        if not nuevo_telefono.isdigit() or not (7 <= len(nuevo_telefono) <= 15):
            messagebox.showerror("📞 Teléfono inválido", "Debe contener solo números entre 7 y 15 dígitos.")
            return

        if not re.match(r'^[A-Z]{3}-\d{4}$', nuevas_placas):
            messagebox.showerror("🔖 Placas inválidas", "Formato correcto: ABC-1234 (3 letras - 4 números)")
            return

        cliente = buscar_cliente(id_cliente=id_val)
        if not cliente:
            messagebox.showerror("❌ Error", "Cliente no encontrado.")
            return

        actualizar_cliente(id_val, nuevo_nombre, nuevo_telefono, nuevo_vehiculo, nuevas_placas)
        messagebox.showinfo("✅ Éxito", "Cliente actualizado correctamente.")
        v.destroy()

    ctk.CTkButton(v, text="💾 Actualizar Cliente", width=entry_width, command=ejecutar_actualizacion).pack(pady=15)
    ctk.CTkButton(v, text="🧹 Limpiar Campos", width=entry_width, fg_color="#444", hover_color="#555", command=limpiar).pack(pady=5)

    ctk.CTkLabel(v, text="* Recuerda que las placas deben tener el formato ABC-1234", font=("Arial", 11, "italic")).pack(pady=10)

#-------------------------------ELIMINAR CLIENTES-------------------------------------
def ventana_eliminar():
    v = ctk.CTkToplevel()
    v.title("🗑️ Eliminar Cliente")
    v.geometry("400x250")
    v.resizable(False, False)

    
    titulo = ctk.CTkLabel(v, text="⚠️ Eliminar Cliente", font=("Arial", 22, "bold"), text_color="#ff5555")
    titulo.pack(pady=15)

   
    subtitulo = ctk.CTkLabel(v, text="Introduce el ID del cliente que deseas eliminar:", font=("Arial", 14))
    subtitulo.pack(pady=5)

   
    id_cliente = ctk.CTkEntry(v, placeholder_text="ID Cliente", width=250)
    id_cliente.pack(pady=10)

    
    boton = ctk.CTkButton(
        v, 
        text="Eliminar Cliente 🗑️", 
        command=lambda: eliminar_cliente(id_cliente.get()),
        fg_color="#d9534f",
        hover_color="#c9302c"
    )
    boton.pack(pady=20)

#---------------------------------SHOW MECANICOS-------------------------------------------
def ver_mecanicos():
    cursor.execute("SELECT * FROM mecanicos")
    mecanicos = cursor.fetchall()

    ventana = ctk.CTkToplevel()
    ventana.title("📋 Lista de Mecánicos")
    ventana.geometry("600x500")
    ventana.resizable(False, False)

    ctk.CTkLabel(ventana, text="🧑‍🔧 Mecánicos Registrados", font=("Arial", 22, "bold")).pack(pady=15)

    # Frame scrollable
    scroll_frame = ctk.CTkScrollableFrame(ventana, width=560, height=380)
    scroll_frame.pack(padx=10, pady=10, fill="both", expand=True)

    if mecanicos:
        for mec in mecanicos:
            frame_item = ctk.CTkFrame(scroll_frame)
            frame_item.pack(pady=8, fill="x", padx=10)

            texto = (
                f"🆔 ID: {mec[0]}\n"
                f"👨‍🔧 Nombre: {mec[1]}\n"
                f"🔧 Especialidad: {mec[2]}\n"
                f"📞 Teléfono: {mec[3]}"
            )

            ctk.CTkLabel(frame_item, text=texto, anchor="w", justify="left").pack(padx=10, pady=5, anchor="w")
    else:
        ctk.CTkLabel(scroll_frame, text="🚫 No hay mecánicos registrados.", font=("Arial", 14)).pack(pady=20)

    # Footer
    ctk.CTkLabel(ventana, text="© 2025 Mecánica Exprés", font=("Arial", 10), text_color="gray").pack(pady=10)

def agregar_mecanico(nombre, especialidad, telefono):
    # Validación de campos vacíos
    if not nombre.strip() or not especialidad.strip() or not telefono.strip():
        messagebox.showerror("Error", "Todos los campos son obligatorios.")
        return

    # Validación del teléfono
    if not telefono.isdigit() or len(telefono) < 7 or len(telefono) > 15:
        messagebox.showerror("Error", "El teléfono debe contener solo números y tener entre 7 y 15 dígitos.")
        return

    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  
            database="taller_mecanico"
        )
        cursor = conexion.cursor()

        
        cursor.execute("SELECT * FROM mecanicos WHERE nombre = %s OR telefono = %s", (nombre.strip(), telefono.strip()))
        existente = cursor.fetchone()

        if existente:
            messagebox.showwarning("Duplicado", "Ya existe un mecánico registrado con ese nombre o teléfono.")
            conexion.close()
            return

        # Insertar nuevo mecánico
        cursor.execute(
            "INSERT INTO mecanicos (nombre, especialidad, telefono) VALUES (%s, %s, %s)",
            (nombre.strip(), especialidad.strip(), telefono.strip())
        )

        conexion.commit()
        conexion.close()

        messagebox.showinfo("Éxito", "Mecánico agregado exitosamente.")
        print("Mecánico agregado exitosamente.")

    except mysql.connector.Error as err:
        messagebox.showerror("Error de Base de Datos", f"Ocurrió un error: {err}")
    

#------------------------ACTUALIZAR MECANICO------------------------------
def actualizar_mecanico(id_mecanico, nuevo_nombre, nueva_especialidad, nuevo_telefono):
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  
        database="taller_mecanico"
    )
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM mecanicos WHERE id = %s", (id_mecanico,))
    resultado = cursor.fetchone()

    if resultado:
        cursor.execute("UPDATE mecanicos SET nombre = %s, especialidad = %s, telefono = %s WHERE id = %s",
                       (nuevo_nombre, nueva_especialidad, nuevo_telefono, id_mecanico))
        conexion.commit()
        print("Mecánico actualizado exitosamente.")
    else:
        print("Mecánico no encontrado.")

    conexion.close()

#------------------------ELIMINAR MECANICOS-------------------------
def eliminar_mecanico(id_mecanico):
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  
        database="taller_mecanico"
    )
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM mecanicos WHERE id = %s", (id_mecanico,))
    resultado = cursor.fetchone()

    if resultado:
        cursor.execute("DELETE FROM mecanicos WHERE id = %s", (id_mecanico,))
        conexion.commit()
        print("Mecánico eliminado exitosamente.")
    else:
        print("Mecánico no encontrado.")

    conexion.close()

#---------------------------VENTANA DE GESTION--------------------------------------------

def ventana_gestion_mecanicos():
    v = ctk.CTkToplevel()
    v.title("🧑‍🔧 Gestión de Mecánicos")
    v.geometry("500x700")
    v.resizable(False, False)

    # -------- Contenedor Principal --------
    frame = ctk.CTkFrame(v)
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    # -------- Título --------
    ctk.CTkLabel(frame, text="🧰 Registro y Edición de Mecánicos", font=("Arial", 20, "bold")).pack(pady=15)

    # -------- Datos Nuevos --------
    ctk.CTkLabel(frame, text="➕ Agregar Nuevo Mecánico", font=("Arial", 14, "bold")).pack(pady=(10, 5))

    nombre = ctk.CTkEntry(frame, placeholder_text="🔤 Nombre completo")
    nombre.pack(pady=5)

    especialidad = ctk.CTkEntry(frame, placeholder_text="🛠️ Especialidad")
    especialidad.pack(pady=5)

    telefono = ctk.CTkEntry(frame, placeholder_text="📞 Teléfono")
    telefono.pack(pady=5)

    boton_agregar = ctk.CTkButton(
        frame, 
        text="💾 Agregar Mecánico", 
        fg_color="#2ecc71", 
        hover_color="#27ae60",
        command=lambda: agregar_mecanico(nombre.get(), especialidad.get(), telefono.get())
    )
    boton_agregar.pack(pady=10)

    # -------- Ver Mecánicos --------
    boton_ver = ctk.CTkButton(
        frame, 
        text="📋 Ver Todos los Mecánicos", 
        command=ver_mecanicos,
        fg_color="#3498db", 
        hover_color="#2980b9"
    )
    boton_ver.pack(pady=15)

    # -------- Editar o Eliminar --------
    ctk.CTkLabel(frame, text="✏️ Actualizar / ❌ Eliminar", font=("Arial", 14, "bold")).pack(pady=(20, 10))

    id_mecanico = ctk.CTkEntry(frame, placeholder_text="🆔 ID del Mecánico")
    id_mecanico.pack(pady=5)

    nuevo_nombre = ctk.CTkEntry(frame, placeholder_text="🔤 Nuevo Nombre (opcional)")
    nuevo_nombre.pack(pady=5)

    nueva_especialidad = ctk.CTkEntry(frame, placeholder_text="🛠️ Nueva Especialidad (opcional)")
    nueva_especialidad.pack(pady=5)

    nuevo_telefono = ctk.CTkEntry(frame, placeholder_text="📞 Nuevo Teléfono (opcional)")
    nuevo_telefono.pack(pady=5)

    boton_actualizar = ctk.CTkButton(
        frame,
        text="🔄 Actualizar Mecánico",
        fg_color="#f1c40f",
        hover_color="#f39c12",
        command=lambda: actualizar_mecanico(id_mecanico.get(), nuevo_nombre.get(), nueva_especialidad.get(), nuevo_telefono.get())
    )
    boton_actualizar.pack(pady=10)

    boton_eliminar = ctk.CTkButton(
        frame, 
        text="🗑️ Eliminar Mecánico", 
        fg_color="#e74c3c", 
        hover_color="#c0392b",
        command=lambda: eliminar_mecanico(id_mecanico.get())
    )
    boton_eliminar.pack(pady=10)

    # Footer
    ctk.CTkLabel(v, text="© 2025 Mecánica Exprés", font=("Arial", 10), text_color="gray").pack(pady=10)



def asignar_mecanico():
    ventana = ctk.CTkToplevel()
    ventana.title("🚗 Asignar Vehículo a Mecánico")
    ventana.geometry("500x620")
    ventana.resizable(False, False)
    frame = ctk.CTkFrame(ventana)
    frame.pack(pady=20, padx=20, fill="both", expand=True)
    ctk.CTkLabel(frame, text="📋 Nueva Orden de Trabajo", font=("Arial", 20, "bold")).pack(pady=10)

    cursor.execute("SELECT id, nombre FROM clientes")
    clientes = cursor.fetchall()

    cursor.execute("SELECT id, nombre FROM mecanicos")
    mecanicos = cursor.fetchall()
    cliente_var = ctk.StringVar()
    mecanico_var = ctk.StringVar()
    descripcion_var = ctk.StringVar()
    tiempo_estimado_var = ctk.StringVar()
    ctk.CTkLabel(frame, text="👤 Cliente:", anchor="w").pack(pady=(15, 5), fill="x")
    cliente_menu = ctk.CTkComboBox(
        frame,
        values=[f"{c[0]} - {c[1]}" for c in clientes],
        variable=cliente_var,
        width=400
    )
    cliente_menu.pack()

    ctk.CTkLabel(frame, text="🧰 Mecánico:", anchor="w").pack(pady=(15, 5), fill="x")
    mecanico_menu = ctk.CTkComboBox(
        frame,
        values=[f"{m[0]} - {m[1]}" for m in mecanicos],
        variable=mecanico_var,
        width=400
    )
    mecanico_menu.pack()

    ctk.CTkLabel(frame, text="🛠️ Descripción del daño:", anchor="w").pack(pady=(15, 5), fill="x")
    descripcion_entry = ctk.CTkEntry(frame, textvariable=descripcion_var, placeholder_text="Ej: Falla en frenos", width=400)
    descripcion_entry.pack()

    ctk.CTkLabel(frame, text="⏱️ Tiempo estimado (horas):", anchor="w").pack(pady=(15, 5), fill="x")
    tiempo_estimado_entry = ctk.CTkEntry(frame, textvariable=tiempo_estimado_var, placeholder_text="Ej: 2.5", width=400)
    tiempo_estimado_entry.pack()

    def guardar_asignacion():
        if not (cliente_var.get() and mecanico_var.get() and descripcion_var.get() and tiempo_estimado_var.get()):
            messagebox.showerror("❗ Error", "Todos los campos son obligatorios.")
            return

        try:
            id_cliente = cliente_var.get().split(" - ")[0]
            id_mecanico = mecanico_var.get().split(" - ")[0]
            descripcion = descripcion_var.get()
            tiempo = float(tiempo_estimado_var.get())
            fecha = date.today()

            sql = """INSERT INTO ordenes_trabajo 
                     (id_cliente, id_mecanico, descripcion_dano, tiempo_estimado, fecha_entrada) 
                     VALUES (%s, %s, %s, %s, %s)"""
            valores = (id_cliente, id_mecanico, descripcion, tiempo, fecha)

            cursor.execute(sql, valores)
            conn.commit()
            messagebox.showinfo("✅ Éxito", "Orden de trabajo asignada correctamente.")
            ventana.destroy()
        except ValueError:
            messagebox.showerror("❗ Error", "El tiempo estimado debe ser un número.")
        except Exception as e:
            messagebox.showerror("❗ Error", f"Ocurrió un error inesperado:\n{e}")
    ctk.CTkButton(
        frame,
        text="💾 Asignar Orden",
        command=guardar_asignacion,
        fg_color="#2ecc71",
        hover_color="#27ae60",
        font=("Arial", 14, "bold"),
        width=200
    ).pack(pady=30)

    # Footer
    ctk.CTkLabel(ventana, text="© 2025 Mecánica Exprés", font=("Arial", 11), text_color="gray").pack(pady=10)



app = ctk.CTk()
app.title("🚗 Mecánica Exprés")
app.geometry("600x750")
app.resizable(False, False)

ctk.set_default_color_theme("blue")  
modo_actual = ctk.StringVar(value="light")

# -----------------------FONDO ANIMADO-----------------------------------
bg_image = ctk.CTkImage(
    light_image=Image.open("fondo_suave.png"),
    dark_image=Image.open("fondo_suave_dark.png"),
    size=(600, 750)
)
background_label = ctk.CTkLabel(app, image=bg_image, text="")
background_label.place(x=0, y=0, relwidth=1, relheight=1)

# -----------------------MENSAJE TEMPORAL-----------------------------------
def mostrar_mensaje_temporal(texto, color="green"):
    toast = ctk.CTkLabel(app, text=texto, text_color="white", fg_color=color,
                         font=("Arial", 14, "bold"), corner_radius=12, padx=20, pady=10)
    toast.place(relx=0.5, rely=0.92, anchor="center")
    app.after(2500, toast.destroy)

# -----------------------REINICIAR LA APP-----------------------------------
def reiniciar_app():
    mostrar_mensaje_temporal("🔄 Reiniciando aplicación...", "#6c757d")
    app.after(1000, lambda: os.execl(sys.executable, sys.executable, *sys.argv))

# -----------------------CAMBIO DE MODO CLARO/OSCURO-----------------------------------
def toggle_modo():
    if modo_actual.get() == "light":
        ctk.set_appearance_mode("dark")
        modo_actual.set("dark")
        boton_modo.configure(text="🌞 Modo Claro")
        mostrar_mensaje_temporal("🌙 Modo oscuro activado", "#444")
    else:
        ctk.set_appearance_mode("light")
        modo_actual.set("light")
        boton_modo.configure(text="🌙 Modo Oscuro")
        mostrar_mensaje_temporal("☀️ Modo claro activado", "#007acc")

# -----------------------EFECTO HOVER EN BOTONES-----------------------------------
def animar_hover(widget, normal_color, hover_color):
    def on_enter(_):
        widget.configure(fg_color=hover_color)
    def on_leave(_):
        widget.configure(fg_color=normal_color)
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)

# -----------------------HEADER------------------------------------------------------
frame_header = ctk.CTkFrame(app, fg_color="transparent")
frame_header.pack(fill="x", pady=(10, 0), padx=20)

logo_img = ctk.CTkImage(Image.open("logo_mecanica.png"), size=(40, 40))  
logo_label = ctk.CTkLabel(frame_header, image=logo_img, text="")
logo_label.pack(side="left", padx=(0, 10))

titulo = ctk.CTkLabel(
    frame_header,
    text="🛠️ Mecánica Exprés",
    font=("Arial Rounded MT Bold", 32),
    text_color="#007acc"
)
titulo.pack(side="left")

boton_modo = ctk.CTkButton(
    frame_header,
    text="🌙 Modo Oscuro",
    command=toggle_modo,
    width=140,
    corner_radius=15,
)
boton_modo.pack(side="right", padx=10)
animar_hover(boton_modo, boton_modo.cget("fg_color"), "#005f99")

# -----------------------TABS PERSONALIZADOS------------------------------------------
tabs = ctk.CTkTabview(app, width=550, height=500, segmented_button_selected_color="#007acc", segmented_button_fg_color="#e9ecef")
tabs.pack(pady=20)

tab_clientes = tabs.add("👤 Clientes")
tab_mecanicos = tabs.add("🔧 Mecánicos")

# -----------------------PESTAÑA CLIENTES--------------------------------------------
ctk.CTkLabel(tab_clientes, text="👥 Gestión de Clientes", font=("Arial", 18, "bold")).pack(pady=15)

botones_clientes = [
    ("➕ Agregar Cliente", lambda: [ventana_agregar(), mostrar_mensaje_temporal("✅ Abriendo ventana para agregar cliente")]),
    ("📋 Ver Clientes", lambda: [ver_clientes(), mostrar_mensaje_temporal("📄 Mostrando lista de clientes")]),
    ("✏️ Actualizar Cliente", lambda: [ventana_actualizar(), mostrar_mensaje_temporal("✏️ Actualizando cliente")]),
    ("❌ Eliminar Cliente", lambda: [ventana_eliminar(), mostrar_mensaje_temporal("❌ Eliminando cliente", "#c9302c")], "#d9534f", "#c9302c")
]

for texto, comando, *colores in botones_clientes:
    fg = colores[0] if colores else "#007acc"
    hover = colores[1] if len(colores) > 1 else "#005f99"
    btn = ctk.CTkButton(tab_clientes, text=texto, width=250, command=comando, fg_color=fg, hover_color=hover)
    btn.pack(pady=8)
    animar_hover(btn, fg, hover)

# -----------------------PESTAÑA MECÁNICOS--------------------------------------------
ctk.CTkLabel(tab_mecanicos, text="🔧 Gestión de Mecánicos", font=("Arial", 18, "bold")).pack(pady=15)

btn_mecanicos = [
    ("🧰 Gestionar Mecánicos", lambda: [ventana_gestion_mecanicos(), mostrar_mensaje_temporal("🧰 Gestión de mecánicos abierta")]),
    ("🚗 Asignar Vehículo", lambda: [asignar_mecanico(), mostrar_mensaje_temporal("🚗 Asignando vehículo a mecánico")])
]

for texto, comando in btn_mecanicos:
    btn = ctk.CTkButton(tab_mecanicos, text=texto, width=250, command=comando)
    btn.pack(pady=8)
    animar_hover(btn, btn.cget("fg_color"), "#005f99")

# -----------------------BOTONES INFERIORES-------------------------------------------
frame_botones = ctk.CTkFrame(app, fg_color="transparent")
frame_botones.pack(pady=10)

btn_salir = ctk.CTkButton(frame_botones, text="🔙 Salir", command=app.destroy,
                          fg_color="#d9534f", hover_color="#c9302c", width=130, corner_radius=15)
btn_salir.pack(side="left", padx=10)
animar_hover(btn_salir, "#d9534f", "#c9302c")

btn_reiniciar = ctk.CTkButton(frame_botones, text="🔄 Reiniciar App", command=reiniciar_app,
                              fg_color="#6c757d", hover_color="#5a6268", width=180, corner_radius=15)
btn_reiniciar.pack(side="left", padx=10)
animar_hover(btn_reiniciar, "#6c757d", "#5a6268")

# --------------------------------PIE DE PÁGINA-------------------------------------------------
ctk.CTkLabel(app, text="© 2025 Mecánica Exprés 🚀", font=("Arial", 12), text_color="gray").pack(side="bottom", pady=10)

app.mainloop()
# Cierra conexión 
cursor.close()
conn.close()
