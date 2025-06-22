import tkinter as tk
from tkinter import messagebox
import json

#variables generales para todas las funciones
numero_seleccionado = None
nivel_seleccionado = "FACIL"
nombre_jugador = ""
juego_activo = False
celdas = []
coordenadas_jugables = []
modo_borrador = False
pila_deshacer = []
pila_rehacer = []


def cargar_partida():
    archivo = open("kakuro2025_partidas.json", "r")
    contenido = archivo.read()
    archivo.close()
    datos = json.loads(contenido)
    for partida in datos:
        if partida["nivel_de_dificultad"] == nivel_seleccionado:
            return partida

def pintar_tablero_completo():
    # Recorre todas las celdas del tablero y las deja en color gris claro y sin texto
    for fila in range(9):
        for col in range(9):
            celdas[fila][col].config(bg="lightgray", text="")

    #limpia la lista de coordenadas que son jugables 
    coordenadas_jugables.clear()
    #carga la partida correspondiente al nivel seleccionado
    partida = cargar_partida()
    if not partida:
        # Si no hay partida, sale de la función
        return

    # Obtiene la lista de claves (pistas de suma) de la partida
    claves = partida["claves"]
    for clave in claves:
        tipo = clave["tipo_de_clave"]  # Puede ser 'F' (fila) o 'C' (columna)
        fila = clave["fila"] - 1       # Ajusta a índice base 0
        col = clave["columna"] - 1     # Ajusta a índice base 0
        suma = clave["clave"]          # Valor de la suma a lograr
        cantidad = clave["casillas"]   # Número de casillas que abarca la clave

        # Pone la suma en la celda correspondiente y la pinta de azul claro
        if 0 <= fila < 9 and 0 <= col < 9:
            celdas[fila][col].config(text=str(suma), bg="lightblue")

        # Si la clave es de fila ('F'), marca las casillas jugables a la derecha
        if tipo == "F":
            for i in range(1, cantidad + 1):
                nueva_col = col + i
                if 0 <= nueva_col < 9:
                    celdas[fila][nueva_col].config(bg="white")
                    coordenadas_jugables.append((fila, nueva_col))

        # Si la clave es de columna ('C'), marca las casillas jugables hacia abajo
        if tipo == "C":
            for i in range(1, cantidad + 1):
                nueva_fila = fila + i
                if 0 <= nueva_fila < 9:
                    celdas[nueva_fila][col].config(bg="white")
                    coordenadas_jugables.append((nueva_fila, col))

def iniciar_juego(nombre, boton_iniciar, etiqueta_nivel):
    global nombre_jugador, juego_activo
    if nombre.strip() == "":
        tk.messagebox.showerror("Error", "Debe ingresar un nombre antes de iniciar el juego.")
        return
    nombre_jugador = nombre
    juego_activo = True
    boton_iniciar.config(state="disabled")
    etiqueta_nivel.config(text="NIVEL " + nivel_seleccionado.upper())
    pintar_tablero_completo()

def seleccionar_numero(num):
    global numero_seleccionado
    numero_seleccionado = num

def validar_jugada(fila, columna, numero):
    partida = cargar_partida()
    if not partida:
        return False

    for clave in partida["claves"]:
        tipo = clave["tipo_de_clave"]
        f = clave["fila"] - 1
        c = clave["columna"] - 1
        cantidad = clave["casillas"]
        valor_clave = clave["clave"]

        suma = 0
        usados = []

        if tipo == "F" and f == fila and c < columna <= c + cantidad:
            for i in range(1, cantidad + 1):
                actual_col = c + i
                val = celdas[f][actual_col]["text"]
                if (f, actual_col) == (fila, columna):
                    suma += numero
                elif val.isdigit():
                    usados.append(int(val))
                    suma += int(val)
            if numero in usados:
                messagebox.showerror("Error", "JUGADA NO ES VÁLIDA PORQUE EL NÚMERO YA ESTÁ EN SU GRUPO DE FILA")
                return False
            if suma > valor_clave:
                messagebox.showerror("Error", f"JUGADA NO ES VÁLIDA PORQUE LA SUMA DE LA FILA ES {suma} Y LA CLAVE NUMÉRICA ES {valor_clave}")
                return False

        if tipo == "C" and c == columna and f < fila <= f + cantidad:
            for i in range(1, cantidad + 1):
                actual_fila = f + i
                val = celdas[actual_fila][c]["text"]
                if (actual_fila, c) == (fila, columna):
                    suma += numero
                elif val.isdigit():
                    usados.append(int(val))
                    suma += int(val)
            if numero in usados:
                messagebox.showerror("Error", "JUGADA NO ES VÁLIDA PORQUE EL NÚMERO YA ESTÁ EN SU GRUPO DE COLUMNA")
                return False
            if suma > valor_clave:
                messagebox.showerror("Error", f"JUGADA NO ES VÁLIDA PORQUE LA SUMA DE LA COLUMNA ES {suma} Y LA CLAVE NUMÉRICA ES {valor_clave}")
                return False

    return True

def activar_borrador():
    global modo_borrador
    modo_borrador = True


def colocar_numero_en_casilla(fila, columna):
    global numero_seleccionado, modo_borrador
    if not juego_activo or (fila, columna) not in coordenadas_jugables:
        return

    if modo_borrador:
        valor_anterior = celdas[fila][columna]["text"]
        if valor_anterior != "":
            registrar_jugada(fila, columna, valor_anterior, "")

        celdas[fila][columna].config(text="")
        modo_borrador = False
        return

    if numero_seleccionado is None:
        messagebox.showerror("Error", "FALTA QUE SELECCIONE EL NÚMERO.")
        return

    if validar_jugada(fila, columna, numero_seleccionado):
        valor_anterior = celdas[fila][columna]["text"]
        valor_nuevo = str(numero_seleccionado)
        registrar_jugada(fila, columna, valor_anterior, valor_nuevo)
        celdas[fila][columna].config(text=str(numero_seleccionado))
        # Verificamos si ya se llenó el tablero
        if tablero_completo():
            guardar_record(nombre_jugador, nivel_seleccionado, 0, 0, 0)  # Por ahora ponemos 00:00:00
            messagebox.showinfo("¡Felicidades!", "¡Completaste el tablero!")
        verificar_victoria()

def registrar_jugada(fila, columna, valor_anterior, valor_nuevo):
    movimiento = {
        "fila": fila,
        "columna": columna,
        "antes": valor_anterior,
        "despues": valor_nuevo
    }
    pila_deshacer.append(movimiento)
    pila_rehacer.clear()  # Al hacer una nueva jugada, ya no se pueden rehacer las viejas

def deshacer_jugada():
    if not pila_deshacer:
        messagebox.showinfo("Info", "No hay jugadas que deshacer.")
        return

    jugada = pila_deshacer.pop()  # Sacamos la última jugada
    fila = jugada["fila"]
    columna = jugada["columna"]
    valor_anterior = jugada["antes"]
    valor_nuevo = jugada["despues"]

    # Restauramos la celda con lo que había antes
    celdas[fila][columna].config(text=valor_anterior)

    # Guardamos lo que deshicimos en pila_redo por si se quiere rehacer
    pila_rehacer.append(jugada)

def rehacer_jugada():
    if not pila_rehacer:
        messagebox.showinfo("Info", "No hay jugadas que rehacer.")
        return

    jugada = pila_rehacer.pop()
    fila = jugada["fila"]
    columna = jugada["columna"]
    valor_nuevo = jugada["despues"]
    valor_anterior = jugada["antes"]

    # Aplicamos de nuevo el número que se había quitado
    celdas[fila][columna].config(text=valor_nuevo)

    # Volvemos a guardar en la pila de undo por si el jugador quiere volver a deshacer
    pila_deshacer.append(jugada)



def tablero_completo():
    for fila, columna in coordenadas_jugables:
        texto = celdas[fila][columna]["text"]
        if not texto.isdigit() or texto == "":
            return False
    return True


def guardar_record(nombre, nivel, horas, minutos, segundos):
    archivo = open("kakuro2025_records.txt", "r", encoding="utf-8")
    texto = archivo.read()
    archivo.close()

    datos = json.loads(texto)

    nuevo = {
        "jugador": nombre, 
        "nivel": nivel,
        "tiempo": str(horas).zfill(2) + ":" + str(minutos).zfill(2) + ":" + str(segundos).zfill(2)
    }

    datos.append(nuevo)

    archivo = open("kakuro2025_records.txt", "w", encoding="utf-8")
    texto_nuevo = json.dumps(datos, indent=4)
    archivo.write(texto_nuevo)
    archivo.close()

def mostrar_records():
    archivo = open("kakuro2025_records.txt", "r", encoding="utf-8")
    datos = json.load(archivo)
    archivo.close()

    ventana = tk.Toplevel()
    ventana.title("Récords")
    ventana.geometry("350x300")
    ventana.config(bg="light pink")

    tk.Label(ventana, text="---RÉCORDS KAKURO---", font=("Helvetica", 14), bg="light pink").pack(pady=10)

    if not datos:
        tk.Label(ventana, text="No hay récords registrados todavía.", bg="white").pack(pady=10)
        return

    for record in datos:
        texto = f"Jugador: {record['jugador']} | Nivel: {record['nivel']} | Tiempo: {record['tiempo']}"
        tk.Label(ventana, text=texto, bg="light pink").pack(anchor="w", padx=15, pady=2)


def verificar_victoria():
    for (fila, columna) in coordenadas_jugables:
        texto = celdas[fila][columna]["text"]
        if texto.strip() == "" or not texto.isdigit():
            return 
    messagebox.showinfo("¡Felicidades!", "¡EXCELENTE JUGADOR! TERMINÓ EL JUEGO CON ÉXITO.")
    guardar_record(nombre_jugador, nivel_seleccionado, 0, 0, 30)
    reiniciar_juego()

def borrar_juego(boton_iniciar, etiqueta_nivel, entrada_nombre):
    global juego_activo, numero_seleccionado, pila_deshacer, pila_rehacer

    if not juego_activo:
        messagebox.showerror("Error", "NO SE HA INICIADO EL JUEGO")
        return

    respuesta = messagebox.askyesno("Confirmar", "¿ESTÁ SEGURO DE BORRAR EL JUEGO?")

    if respuesta:
        numero_seleccionado = None
        juego_activo = False
        pila_deshacer.clear()
        pila_rehacer.clear()
        pintar_tablero_completo()
        boton_iniciar.config(state="normal")
        etiqueta_nivel.config(text="NIVEL " + nivel_seleccionado.upper())
        entrada_nombre.delete(0, tk.END)

def reiniciar_juego():
    global numero_seleccionado
    numero_seleccionado = None
    pintar_tablero_completo()


def jugar():
    global celdas
    ventana = tk.Toplevel()
    ventana.title("Kakuro 2025")
    ventana.geometry("780x650")
    ventana.config(bg="light pink")

    fondo = tk.Frame(ventana, bg="light pink")
    fondo.pack()

    titulo = tk.Label(fondo, text="K A K U R O", font=("Helvetica", 18), bg="light pink")
    titulo.pack(pady=5)

    caja_nombre = tk.Frame(fondo, bg="light pink")
    caja_nombre.pack()
    texto_nombre = tk.Label(caja_nombre, text="Jugador:", bg="light pink")
    texto_nombre.pack(side=tk.LEFT)
    entrada = tk.Entry(caja_nombre, width=30)
    entrada.pack(side=tk.LEFT, padx=5)

    centro = tk.Frame(fondo, bg="light pink")
    centro.pack(pady=5)

    tablero = tk.Frame(centro, bg="light pink")
    tablero.pack(side=tk.LEFT, padx=10)
    celdas = []
    for fila in range(9):
        fila_actual = []
        for columna in range(9):
            celda = tk.Label(tablero, width=4, height=2, bg="lightgray", relief="solid", bd=1)
            celda.grid(row=fila, column=columna, padx=1, pady=1)

            def click(evento, f=fila, c=columna):
                colocar_numero_en_casilla(f, c)

            celda.bind("<Button-1>", click)
            fila_actual.append(celda)
        celdas.append(fila_actual)

    numeros = tk.Frame(centro, bg="light pink")
    numeros.pack(side=tk.LEFT, padx=10)
    texto = tk.Label(numeros, text="Seleccionar número", bg="light pink")
    texto.pack(pady=3)

    for num in range(1, 10):
        boton = tk.Button(numeros, text=str(num), width=2, height=1, command=lambda n=num: seleccionar_numero(n))
        boton.pack(pady=1)
        # Botón borrador para activar modo borrar
    boton_borrador = tk.Button(numeros, text="🧽", font=("Arial", 14), width=3, command=activar_borrador)
    boton_borrador.pack(pady=8)


    reloj = tk.Frame(fondo, bg="light pink")
    reloj.pack(pady=3)

    tk.Label(reloj, text="Horas", bg="light pink").grid(row=0, column=0, padx=10)
    tk.Label(reloj, text="Minutos", bg="light pink").grid(row=0, column=1, padx=10)
    tk.Label(reloj, text="Segundos", bg="light pink").grid(row=0, column=2, padx=10)
    tk.Label(reloj, text="00", bg="light pink").grid(row=1, column=0)
    tk.Label(reloj, text="00", bg="light pink").grid(row=1, column=1)
    tk.Label(reloj, text="00", bg="light pink").grid(row=1, column=2)

    etiqueta_nivel = tk.Label(fondo, text="NIVEL FÁCIL", bg="light pink")
    etiqueta_nivel.pack(pady=2)

    def seleccionar_nivel_y_continuar():
        def guardar_y_cargar():
            global nivel_seleccionado
            nivel_seleccionado = variable_nivel.get()
            ventana.destroy()
            iniciar_juego(entrada.get(), boton_iniciar, etiqueta_nivel)

        ventana = tk.Toplevel()
        ventana.title("Seleccionar nivel")
        ventana.geometry("300x250")
        ventana.config(bg="light pink")

        tk.Label(ventana, text="Seleccione el nivel de dificultad:", font=("Arial", 12), bg="light pink").pack(pady=10)
        variable_nivel = tk.StringVar(value="FACIL")
        for nivel in ["FACIL", "MEDIO", "DIFICIL", "EXPERTO"]:
            tk.Radiobutton(ventana, text=nivel, variable=variable_nivel, value=nivel, bg="light pink").pack(anchor="w", padx=20)
        tk.Button(ventana, text="Aceptar", bg="light pink", command=guardar_y_cargar).pack(pady=15)

    botones_abajo = tk.Frame(fondo, bg="light pink")
    botones_abajo.pack(pady=10)
    boton_iniciar = tk.Button(botones_abajo, text="INICIAR JUEGO", bg="PaleVioletRed", width=19, height=2, command=seleccionar_nivel_y_continuar)
    boton_iniciar.grid(row=0, column=0, padx=6, pady=4)

    boton_deshacer = tk.Button(botones_abajo, text="DESHACER JUGADA", bg="plum3", width=19, height=2, command=deshacer_jugada)
    boton_deshacer.grid(row=0, column=1, padx=6, pady=4)

    boton_borrar = tk.Button(botones_abajo, text="BORRAR JUEGO", bg="pink2", width=19, height=2, command=lambda: borrar_juego(boton_iniciar, etiqueta_nivel, entrada))
    boton_borrar.grid(row=0, column=2, padx=6, pady=4)

    boton_guardar = tk.Button(botones_abajo, text="GUARDAR JUEGO", bg="Thistle2", width=19, height=2)
    boton_guardar.grid(row=0, column=3, padx=6, pady=4)

    boton_records = tk.Button(botones_abajo, text="RÉCORDS", bg="antiquewhite1", width=19, height=2, command=mostrar_records)
    boton_records.grid(row=1, column=0, padx=6, pady=4)

    boton_rehacer = tk.Button(botones_abajo, text="REHACER JUGADA", bg="orchid2", width=19, height=2, command=rehacer_jugada)
    boton_rehacer.grid(row=1, column=1, padx=6, pady=4)

    boton_terminar = tk.Button(botones_abajo, text="TERMINAR JUEGO", bg="lightcoral", width=19, height=2)
    boton_terminar.grid(row=1, column=2, padx=6, pady=4)

    boton_cargar = tk.Button(botones_abajo, text="CARGAR JUEGO", bg="rosybrown", width=19, height=2)
    boton_cargar.grid(row=1, column=3, padx=6, pady=4)


def configurar():
    messagebox.showinfo("Configurar")

def ayuda():
    messagebox.showinfo("Ayuda")

def acerca_de():
    messagebox.showinfo("Acerca de")

def salir():
    ventana_principal.destroy()

ventana_principal = tk.Tk()
ventana_principal.title("Kakuro 2025")
ventana_principal.geometry("300x400")
ventana_principal.configure(bg="light pink")

etiqueta_titulo = tk.Label(ventana_principal, text="Kakuro 2025", font=("Verdana", 15), bg="light pink")
etiqueta_titulo.pack(pady=20)

tk.Button(ventana_principal, text="Jugar", width=25, command=jugar).pack(pady=5)
tk.Button(ventana_principal, text="Configurar", width=25, command=configurar).pack(pady=5)
tk.Button(ventana_principal, text="Ayuda", width=25, command=ayuda).pack(pady=5)
tk.Button(ventana_principal, text="Acerca de", width=25, command=acerca_de).pack(pady=5)
tk.Button(ventana_principal, text="Salir", width=25, bg="PaleVioletRed", command=salir).pack(pady=20)

ventana_principal.mainloop()
