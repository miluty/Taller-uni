import customtkinter as ctk
import mysql.connector
from tkinter import messagebox
import re

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
#-----------------------FUNCIONES-------------------------------------
def agregar_cliente(nombre, telefono, vehiculo, placas):
    if not (nombre and telefono and vehiculo and placas):
        messagebox.showerror("Error", "Todos los campos son obligatorios.")
        return
    
   
    if not telefono.isdigit():
        messagebox.showerror("Error", "El teléfono debe contener solo números.")
        return
    
   
    placa_pattern = r'^[A-Za-z]{3}-\d{4}$'
    if not re.match(placa_pattern, placas):
        messagebox.showerror("Error", "El formato de las placas es incorrecto. Ejemplo: ABC-1234")
        return
    
    try:
        cursor.execute("INSERT INTO clientes (nombre, telefono, vehiculo, placas) VALUES (%s, %s, %s, %s)",
                       (nombre, telefono, vehiculo, placas))
        conn.commit()
        messagebox.showinfo("Éxito", "Cliente agregado correctamente.")
    except mysql.connector.IntegrityError:
        messagebox.showerror("Error", "Placas duplicadas. El cliente ya existe.")

def ver_clientes():
    cursor.execute("SELECT * FROM clientes")
    clientes = cursor.fetchall()
    ventana = ctk.CTkToplevel()
    ventana.title("Lista de Clientes")
    ventana.geometry("700x400")

    text = ctk.CTkTextbox(ventana, width=680, height=380)
    text.pack(pady=10)

    if clientes:
        for cliente in clientes:
            text.insert("end", f"ID: {cliente[0]} | Nombre: {cliente[1]} | Teléfono: {cliente[2]} | Vehículo: {cliente[3]} | Placas: {cliente[4]}\n")
    else:
        text.insert("end", "No hay clientes registrados.")

    text.configure(state="disabled")

def buscar_cliente(id_cliente=None, placas=None):
    if id_cliente:
        cursor.execute("SELECT * FROM clientes WHERE id = %s", (id_cliente,))
    elif placas:
        cursor.execute("SELECT * FROM clientes WHERE placas = %s", (placas,))
    else:
        return None
    return cursor.fetchone()

def actualizar_cliente(id_cliente, nombre, telefono, vehiculo, placas):
    cliente = buscar_cliente(id_cliente=id_cliente)
    if cliente:
        cursor.execute("""
        UPDATE clientes SET nombre = %s, telefono = %s, vehiculo = %s, placas = %s WHERE id = %s
        """, (nombre or cliente[1], telefono or cliente[2], vehiculo or cliente[3], placas or cliente[4], id_cliente))
        conn.commit()
        messagebox.showinfo("Éxito", "Cliente actualizado correctamente.")
    else:
        messagebox.showerror("Error", "Cliente no encontrado.")

def eliminar_cliente(id_cliente):
    cliente = buscar_cliente(id_cliente=id_cliente)
    if cliente:
        confirm = messagebox.askyesno("Confirmar", f"¿Eliminar a {cliente[1]}?")
        if confirm:
            cursor.execute("DELETE FROM clientes WHERE id = %s", (id_cliente,))
            conn.commit()
            messagebox.showinfo("Éxito", "Cliente eliminado correctamente.")
    else:
        messagebox.showerror("Error", "Cliente no encontrado.")

#-------------------------Ventanas auxiliares------------------------------

def ventana_agregar():
    v = ctk.CTkToplevel()
    v.title("Agregar Cliente")
    v.geometry("400x400")

    nombre = ctk.CTkEntry(v, placeholder_text="Nombre")
    nombre.pack(pady=10)
    telefono = ctk.CTkEntry(v, placeholder_text="Teléfono")
    telefono.pack(pady=10)
    vehiculo = ctk.CTkEntry(v, placeholder_text="Vehículo")
    vehiculo.pack(pady=10)
    placas = ctk.CTkEntry(v, placeholder_text="Placas")
    placas.pack(pady=10)

    boton = ctk.CTkButton(v, text="Guardar", command=lambda: agregar_cliente(nombre.get(), telefono.get(), vehiculo.get(), placas.get()))
    boton.pack(pady=20)
#----------------------------actualizar clientes----------------------------------
def ventana_actualizar():
    v = ctk.CTkToplevel()
    v.title("Actualizar Cliente")
    v.geometry("400x550")

    id_cliente = ctk.CTkEntry(v, placeholder_text="ID Cliente")
    id_cliente.pack(pady=10)

    nombre = ctk.CTkEntry(v, placeholder_text="Nuevo Nombre")
    nombre.pack(pady=10)
    telefono = ctk.CTkEntry(v, placeholder_text="Nuevo Teléfono")
    telefono.pack(pady=10)
    vehiculo = ctk.CTkEntry(v, placeholder_text="Nuevo Vehículo")
    vehiculo.pack(pady=10)
    placas = ctk.CTkEntry(v, placeholder_text="Nuevas Placas")
    placas.pack(pady=10)

    def rellenar_datos():
        cliente = buscar_cliente(id_cliente=id_cliente.get())
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
            messagebox.showerror("Error", "Cliente no encontrado.")

    rellenar = ctk.CTkButton(v, text="Buscar Cliente", command=rellenar_datos)
    rellenar.pack(pady=10)

    boton = ctk.CTkButton(v, text="Actualizar", command=lambda: actualizar_cliente(id_cliente.get(), nombre.get(), telefono.get(), vehiculo.get(), placas.get()))
    boton.pack(pady=20)
#-------------------------------ELIMINAR CLIENTES-------------------------------------
def ventana_eliminar():
    v = ctk.CTkToplevel()
    v.title("Eliminar Cliente")
    v.geometry("300x200")

    id_cliente = ctk.CTkEntry(v, placeholder_text="ID Cliente")
    id_cliente.pack(pady=20)

    boton = ctk.CTkButton(v, text="Eliminar", command=lambda: eliminar_cliente(id_cliente.get()))
    boton.pack(pady=20)
#       -------------mecanicos---------------
def agregar_mecanico(nombre, especialidad, telefono):
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # tu password si tienes, si no está vacío
        database="taller_mecanico"
    )
    cursor = conexion.cursor()

    cursor.execute("INSERT INTO mecanicos (nombre, especialidad, telefono) VALUES (%s, %s, %s)",
                   (nombre, especialidad, telefono))

    conexion.commit()
    conexion.close()
    print("Mecánico agregado exitosamente.")

#---------------------------------SHOW MECANICOS-------------------------------------------
def ver_mecanicos():
    cursor.execute("SELECT * FROM mecanicos")
    mecanicos = cursor.fetchall()
    ventana = ctk.CTkToplevel()
    ventana.title("Lista de Mecánicos")
    ventana.geometry("600x400")
    
    text = ctk.CTkTextbox(ventana, width=580, height=380)
    text.pack(pady=10)

    if mecanicos:
        for mecanico in mecanicos:
            text.insert("end", f"ID: {mecanico[0]} | Nombre: {mecanico[1]} | Especialidad: {mecanico[2]} | Teléfono: {mecanico[3]}\n")
    else:
        text.insert("end", "No hay mecánicos registrados.")

    text.configure(state="disabled")
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
    v.title("Gestión de Mecánicos")
    v.geometry("400x600")

    nombre = ctk.CTkEntry(v, placeholder_text="Nombre")
    nombre.pack(pady=5)
    especialidad = ctk.CTkEntry(v, placeholder_text="Especialidad")
    especialidad.pack(pady=5)
    telefono = ctk.CTkEntry(v, placeholder_text="Teléfono")
    telefono.pack(pady=5)

    boton_agregar = ctk.CTkButton(v, text="Agregar Mecánico", command=lambda: agregar_mecanico(nombre.get(), especialidad.get(), telefono.get()))
    boton_agregar.pack(pady=10)

    boton_ver = ctk.CTkButton(v, text="Ver Mecánicos", command=ver_mecanicos)
    boton_ver.pack(pady=10)

    id_mecanico = ctk.CTkEntry(v, placeholder_text="ID Mecánico para actualizar/eliminar")
    id_mecanico.pack(pady=10)

    nuevo_nombre = ctk.CTkEntry(v, placeholder_text="Nuevo Nombre (opcional)")
    nuevo_nombre.pack(pady=5)
    nueva_especialidad = ctk.CTkEntry(v, placeholder_text="Nueva Especialidad (opcional)")
    nueva_especialidad.pack(pady=5)
    nuevo_telefono = ctk.CTkEntry(v, placeholder_text="Nuevo Teléfono (opcional)")
    nuevo_telefono.pack(pady=5)

    boton_actualizar = ctk.CTkButton(v, text="Actualizar Mecánico", command=lambda: actualizar_mecanico(id_mecanico.get(), nuevo_nombre.get(), nueva_especialidad.get(), nuevo_telefono.get()))
    boton_actualizar.pack(pady=10)

    boton_eliminar = ctk.CTkButton(v, text="Eliminar Mecánico", command=lambda: eliminar_mecanico(id_mecanico.get()))
    boton_eliminar.pack(pady=10)
import customtkinter as ctk
from tkinter import messagebox
from datetime import date

def asignar_mecanico():
    ventana = ctk.CTkToplevel()
    ventana.title("Asignar Vehículo a Mecánico")
    ventana.geometry("500x600")

    # Obtener lista de clientes
    cursor.execute("SELECT id, nombre FROM clientes")
    clientes = cursor.fetchall()

    # Obtener lista de mecánicos
    cursor.execute("SELECT id, nombre FROM mecanicos")
    mecanicos = cursor.fetchall()

    # Variables para los ComboBox
    cliente_var = ctk.StringVar()
    mecanico_var = ctk.StringVar()

    # ComboBox de Cliente
    ctk.CTkLabel(ventana, text="Selecciona Cliente:").pack(pady=5)
    cliente_menu = ctk.CTkComboBox(
        ventana, 
        values=[f"{c[0]} - {c[1]}" for c in clientes], 
        variable=cliente_var
    )
    cliente_menu.pack(pady=10)

    # ComboBox Mecánico
    ctk.CTkLabel(ventana, text="Selecciona Mecánico:").pack(pady=5)
    mecanico_menu = ctk.CTkComboBox(
        ventana, 
        values=[f"{m[0]} - {m[1]}" for m in mecanicos], 
        variable=mecanico_var
    )
    mecanico_menu.pack(pady=10)

    #-----------Otros Campos-------------------
    ctk.CTkLabel(ventana, text="Descripción del daño:").pack(pady=5)
    descripcion_var = ctk.StringVar()
    descripcion_entry = ctk.CTkEntry(ventana, textvariable=descripcion_var, placeholder_text="Descripción del daño")
    descripcion_entry.pack(pady=10)

    ctk.CTkLabel(ventana, text="Tiempo estimado de reparación (horas):").pack(pady=5)
    tiempo_estimado_var = ctk.StringVar()
    tiempo_estimado_entry = ctk.CTkEntry(ventana, textvariable=tiempo_estimado_var, placeholder_text="Tiempo estimado")
    tiempo_estimado_entry.pack(pady=10)

    def guardar_asignacion():
        if not (cliente_var.get() and mecanico_var.get() and descripcion_var.get() and tiempo_estimado_var.get()):
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        try:
            id_cliente = cliente_var.get().split(" - ")[0]
            id_mecanico = mecanico_var.get().split(" - ")[0]
            descripcion_daño = descripcion_var.get()
            tiempo = float(tiempo_estimado_var.get())  #   numérico
            fecha = date.today()

            sql = """INSERT INTO ordenes_trabajo 
                     (id_cliente, id_mecanico, descripcion_dano, tiempo_estimado, fecha_entrada) 
                     VALUES (%s, %s, %s, %s, %s)"""
            valores = (id_cliente, id_mecanico, descripcion_daño, tiempo, fecha)

            cursor.execute(sql, valores)
            conn.commit()
            messagebox.showinfo("Éxito", "Orden de trabajo creada exitosamente.")
            ventana.destroy()
        
        except ValueError:
            messagebox.showerror("Error", "Tiempo estimado debe ser un número.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {e}")

    #guardar la asignación
    boton_guardar = ctk.CTkButton(ventana, text="Asignar", command=guardar_asignacion)
    boton_guardar.pack(pady=20)

# Inicializar la app
app = ctk.CTk()
app.title("🛠️ Mecánica Exprés")
app.geometry("600x750")
app.resizable(False, False)

# ---------- Encabezado ----------
label = ctk.CTkLabel(
    app,
    text="🛠️ Mecánica Exprés",
    font=("Helvetica", 32, "bold"),
    text_color="#00bfff"
)
label.pack(pady=25)

# ---------- Tabs ----------
tabs = ctk.CTkTabview(app, width=550, height=500, corner_radius=15, segmented_button_fg_color="#1f1f1f")
tabs.pack(pady=10)

# Tabs
tab_clientes = tabs.add("👥 Clientes")
tab_mecanicos = tabs.add("🔧 Mecánicos")

# ---------- CLIENTES ----------
btn_agregar_cliente = ctk.CTkButton(tab_clientes, text="➕ Agregar Cliente", command=ventana_agregar, width=250)
btn_agregar_cliente.pack(pady=15)

btn_ver_clientes = ctk.CTkButton(tab_clientes, text="📋 Ver Clientes", command=ver_clientes, width=250)
btn_ver_clientes.pack(pady=15)

btn_actualizar_cliente = ctk.CTkButton(tab_clientes, text="✏️ Actualizar Cliente", command=ventana_actualizar, width=250)
btn_actualizar_cliente.pack(pady=15)

btn_eliminar_cliente = ctk.CTkButton(tab_clientes, text="🗑️ Eliminar Cliente", command=ventana_eliminar, width=250)
btn_eliminar_cliente.pack(pady=15)

# ---------- MECÁNICOS ----------
btn_gestion_mecanicos = ctk.CTkButton(tab_mecanicos, text="👨‍🔧 Gestión de Mecánicos", command=ventana_gestion_mecanicos, width=250)
btn_gestion_mecanicos.pack(pady=15)

btn_asignar_vehiculo = ctk.CTkButton(tab_mecanicos, text="🚗 Asignar Vehículo a Mecánico", command=asignar_mecanico, width=250)
btn_asignar_vehiculo.pack(pady=15)

# ---------- BOTÓN SALIR ----------
btn_salir = ctk.CTkButton(
    app,
    text="❌ Salir",
    command=app.destroy,
    fg_color="#d9534f",
    hover_color="#c9302c",
    text_color="white",
    width=200
)
btn_salir.pack(pady=30)

app.mainloop()

# Cierra conexión 
cursor.close()
conn.close()
