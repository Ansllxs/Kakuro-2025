import tkinter as tk
from tkinter import messagebox
import json
import datetime

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
tiempo_inicio = None  #para el cronómetro
tiempo_restante = 0   #para el temporizador
modo_tiempo = "ninguno"  #"cronometro", "temporizador", "ninguno"
reloj_activo = False   #para saber si está corriendo



def cargar_partida():
    archivo = open("kakuro2025_partidas.json", "r")
    contenido = archivo.read()
    archivo.close()
    datos = json.loads(contenido)
    for partida in datos:
        if partida["nivel_de_dificultad"].strip().upper() == nivel_seleccionado.strip().upper():
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

def actualizar_reloj():
    global reloj_activo, tiempo_inicio, tiempo_restante, modo_tiempo

    if not reloj_activo:
        return

    ahora = datetime.datetime.now()

    if modo_tiempo == "cronometro":
        delta = ahora - tiempo_inicio
        total_segundos = int(delta.total_seconds())

    elif modo_tiempo == "temporizador":
        total_segundos = tiempo_restante
        tiempo_restante -= 1
        if tiempo_restante <= 0:
            reloj_activo = False
            respuesta = messagebox.askyesno("Tiempo Expirado", "TIEMPO EXPIRADO. ¿DESEA CONTINUAR EL MISMO JUEGO (SI/NO)?")
            if respuesta:
                # Cambiar a cronómetro y seguir contando desde el tiempo transcurrido
                modo_tiempo = "cronometro"
                # El cronómetro debe empezar desde el tiempo que ya pasó
                tiempo_total_config = horas_config * 3600 + minutos_config * 60 + segundos_config
                tiempo_inicio = ahora - datetime.timedelta(seconds=tiempo_total_config)
                reloj_activo = True
                actualizar_reloj()
            else:
                # Terminar el juego y regresar a la pantalla de jugar
                messagebox.showinfo("Fin del juego", "El juego ha finalizado. Regresando a la pantalla de jugar.")
                reiniciar_juego()
                return
            return
    else:
        return

    horas = total_segundos // 3600
    minutos = (total_segundos % 3600) // 60
    segundos = total_segundos % 60

    hora_label.config(text=str(horas).zfill(2))
    minuto_label.config(text=str(minutos).zfill(2))
    segundo_label.config(text=str(segundos).zfill(2))

    # Repite cada segundo
    hora_label.after(1000, actualizar_reloj)

def cargar_configuracion():
    global modo_tiempo, horas_config, minutos_config, segundos_config, nivel_seleccionado
    archivo = open("kakuro2025_configuracion.json", "r")
    datos = json.load(archivo)
    archivo.close()

    modo_tiempo = datos["modo_tiempo"]
    horas_config = datos["horas"]
    minutos_config = datos["minutos"]
    segundos_config = datos["segundos"]
    nivel_seleccionado = datos["nivel"]


def iniciar_juego(nombre, boton_iniciar, etiqueta_nivel):
    global nombre_jugador, juego_activo
    if nombre.strip() == "":
        tk.messagebox.showerror("Error", "Debe ingresar un nombre antes de iniciar el juego.")
        return
    nombre_jugador = nombre
    juego_activo = True
    boton_iniciar.config(state="disabled")
    cargar_configuracion()
    etiqueta_nivel.config(text="NIVEL " + nivel_seleccionado.upper())
    pintar_tablero_completo()

    global tiempo_inicio, tiempo_restante, reloj_activo

    if modo_tiempo == "cronometro":
        tiempo_inicio = datetime.datetime.now()
        reloj_activo = True
        actualizar_reloj()

    elif modo_tiempo == "temporizador":
        tiempo_restante = horas_config * 3600 + minutos_config * 60 + segundos_config
        reloj_activo = True
        actualizar_reloj()
    else:
        reloj_activo = False



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
    global tiempo_inicio, tiempo_restante

    for (fila, columna) in coordenadas_jugables:
        texto = celdas[fila][columna]["text"]
        if texto.strip() == "" or not texto.isdigit():
            return 

    # Calcular tiempo real
    if modo_tiempo == "cronometro":
        delta = datetime.datetime.now() - tiempo_inicio
        total_segundos = int(delta.total_seconds())
    elif modo_tiempo == "temporizador":
        total_segundos = horas_config * 3600 + minutos_config * 60 + segundos_config - tiempo_restante
    else:
        total_segundos = 0  # Sin reloj

    horas = total_segundos // 3600
    minutos = (total_segundos % 3600) // 60
    segundos = total_segundos % 60

    guardar_record(nombre_jugador, nivel_seleccionado, horas, minutos, segundos)

    messagebox.showinfo("¡Felicidades!", "¡EXCELENTE JUGADOR! TERMINÓ EL JUEGO CON ÉXITO.")
    reiniciar_juego()


def terminarJuego(ventanaJuego):
    global juego_activo
    if not juego_activo:
        messagebox.showerror("Error", "NO SE HA INICIADO EL JUEGO")
        return
            
    respuesta = messagebox.askyesno("Confirmar", "¿ESTÁ SEGURO DE TERMINAR EL JUEGO?")
    
    if respuesta:
        juego_activo = False
        ventanaJuego.destroy()  # Cierra la ventana del juego actual
        jugar() #empieza la pantallaa  de jugar para empezar otro juego
    else:
        pass

def reiniciar_juego():
    global numero_seleccionado
    numero_seleccionado = None
    pintar_tablero_completo()

def borrar_juego(boton_iniciar, etiqueta_nivel, entrada):
    global juego_activo, numero_seleccionado, pila_deshacer, pila_rehacer, coordenadas_jugables, modo_borrador, reloj_activo
    
    if not juego_activo:
        messagebox.showerror("Error", "NO SE HA INICIADO EL JUEGO")
        return
    
    respuesta = messagebox.askyesno("Confirmar", "¿ESTÁ SEGURO DE BORRAR EL JUEGO ACTUAL?")
    
    if respuesta:
        # Reiniciar variables globales
        juego_activo = False
        numero_seleccionado = None
        pila_deshacer.clear()
        pila_rehacer.clear()
        coordenadas_jugables.clear()
        modo_borrador = False
        reloj_activo = False
        
        # Limpiar el tablero
        for fila in range(9):
            for col in range(9):
                celdas[fila][col].config(bg="lightgray", text="")
        
        # Reiniciar la interfaz
        boton_iniciar.config(state="normal")
        etiqueta_nivel.config(text="NIVEL FÁCIL")
        entrada.delete(0, tk.END)
        
        # Reiniciar el reloj
        hora_label.config(text="00")
        minuto_label.config(text="00")
        segundo_label.config(text="00")
        
        messagebox.showinfo("Juego Borrado", "El juego ha sido borrado exitosamente.")

def guardar_juego(nombreJugador, ventana):
    global juego_activo

    if not juego_activo:
        messagebox.showerror("Error", "NO SE HA INICIADO EL JUEGO")
        return

    # Guardar el estado actual del tablero
    tablero = []
    for fila in range(9):
        fila_actual = []
        for col in range(9):
            texto = celdas[fila][col]["text"]
            fila_actual.append(texto)
        tablero.append(fila_actual)

    # Armar datos del juego
    datos = {
        "nivel": nivel_seleccionado,
        "tablero": tablero,
        "jugadas": pila_deshacer
    }

    archivo = open("kakuro2025_juego_actual.json", "r")
    partidas = json.load(archivo)
    archivo.close()

    partidas[nombreJugador] = datos

    archivo = open("kakuro2025_juego_actual.json", "w")
    json.dump(partidas, archivo, indent=4)
    archivo.close()

    messagebox.showinfo("Guardado", "El juego se guardó correctamente.")

    respuesta = messagebox.askyesno("Continuar", "¿VA A CONTINUAR JUGANDO?")
    if not respuesta:
        juego_activo = False
        ventana.destroy()

def cargar_juego(nombreJugador):
    global juego_activo, nivel_seleccionado, pila_deshacer

    if juego_activo:
        messagebox.showerror("Error", "YA HAY UN JUEGO ACTIVO")
        return

    archivo = open("kakuro2025_juego_actual.json", "r")
    partidas = json.load(archivo)
    archivo.close()

    if nombreJugador not in partidas:
        messagebox.showerror("Error", "NO HAY PARTIDA GUARDADA PARA ESTE JUGADOR")
        return

    datos = partidas[nombreJugador]
    tablero = datos["tablero"]
    nivel_seleccionado = datos["nivel"]
    pila_deshacer = datos["jugadas"]

    for fila in range(9):
        for col in range(9):
            texto = tablero[fila][col]
            celdas[fila][col].config(text=texto)

    messagebox.showinfo("Cargado", "La partida fue cargada correctamente.\nPresione INICIAR JUEGO para continuar.")


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

    boton_borrador = tk.Button(numeros, text="🧽", font=("Arial", 14), width=3, command=activar_borrador)
    boton_borrador.pack(pady=8)

    # === Bloque del reloj ===

    global hora_label, minuto_label, segundo_label

    reloj = tk.Frame(fondo, bg="light pink")
    reloj.pack(pady=3)

    tk.Label(reloj, text="Horas", bg="light pink").grid(row=0, column=0, padx=10)
    tk.Label(reloj, text="Minutos", bg="light pink").grid(row=0, column=1, padx=10)
    tk.Label(reloj, text="Segundos", bg="light pink").grid(row=0, column=2, padx=10)

    hora_label = tk.Label(reloj, text="00", bg="light pink")
    hora_label.grid(row=1, column=0)

    minuto_label = tk.Label(reloj, text="00", bg="light pink")
    minuto_label.grid(row=1, column=1)

    segundo_label = tk.Label(reloj, text="00", bg="light pink")
    segundo_label.grid(row=1, column=2)


    etiqueta_nivel = tk.Label(fondo, text="NIVEL " + nivel_seleccionado.upper(), bg="light pink")
    etiqueta_nivel.pack(pady=2)

    botones_abajo = tk.Frame(fondo, bg="light pink")
    botones_abajo.pack(pady=10)
    boton_iniciar = tk.Button(botones_abajo, text="INICIAR JUEGO", bg="PaleVioletRed", width=19, height=2, command=lambda: iniciar_juego(entrada.get(), boton_iniciar, etiqueta_nivel))
    boton_iniciar.grid(row=0, column=0, padx=6, pady=4)

    boton_deshacer = tk.Button(botones_abajo, text="DESHACER JUGADA", bg="plum3", width=19, height=2, command=deshacer_jugada)
    boton_deshacer.grid(row=0, column=1, padx=6, pady=4)

    boton_borrar = tk.Button(botones_abajo, text="BORRAR JUEGO", bg="pink2", width=19, height=2, command=lambda: borrar_juego(boton_iniciar, etiqueta_nivel, entrada))
    boton_borrar.grid(row=0, column=2, padx=6, pady=4)

    boton_guardar = tk.Button(botones_abajo, text="GUARDAR JUEGO", bg="Thistle2", width=19, height=2, command=lambda: guardar_juego(nombre_jugador, ventana))
    boton_guardar.grid(row=0, column=3, padx=6, pady=4)

    boton_records = tk.Button(botones_abajo, text="RÉCORDS", bg="antiquewhite1", width=19, height=2, command=mostrar_records)
    boton_records.grid(row=1, column=0, padx=6, pady=4)

    boton_rehacer = tk.Button(botones_abajo, text="REHACER JUGADA", bg="orchid2", width=19, height=2, command=rehacer_jugada)
    boton_rehacer.grid(row=1, column=1, padx=6, pady=4)

    boton_terminar = tk.Button(botones_abajo, text="TERMINAR JUEGO", bg="lightcoral", width=19, height=2, command=lambda: terminarJuego(ventana))
    boton_terminar.grid(row=1, column=2, padx=6, pady=4)

    boton_cargar = tk.Button(botones_abajo, text="CARGAR JUEGO", bg="rosybrown", width=19, height=2,command=lambda: cargar_juego(nombre_jugador))
    boton_cargar.grid(row=1, column=3, padx=6, pady=4)


def configurar():
    ventana = tk.Toplevel()
    ventana.title("Configurar Kakuro")
    ventana.geometry("350x300")
    ventana.config(bg="light pink")

    tk.Label(ventana, text="Seleccione el nivel:", bg="light pink").pack(pady=5)
    nivel_var = tk.StringVar(value="FACIL")
    for nivel in ["FACIL", "MEDIO", "DIFICIL", "EXPERTO"]:
        tk.Radiobutton(ventana, text=nivel, variable=nivel_var, value=nivel, bg="light pink").pack(anchor="w", padx=20)

    tk.Label(ventana, text="Seleccione el reloj:", bg="light pink").pack(pady=5)
    reloj_var = tk.StringVar(value="ninguno")
    for modo in ["cronometro", "temporizador", "ninguno"]:
        tk.Radiobutton(ventana, text=modo.capitalize(), variable=reloj_var, value=modo, bg="light pink").pack(anchor="w", padx=20)

    frame_tiempo = tk.Frame(ventana, bg="light pink")
    frame_tiempo.pack(pady=5)
    tk.Label(frame_tiempo, text="Horas:", bg="light pink").grid(row=0, column=0)
    tk.Label(frame_tiempo, text="Minutos:", bg="light pink").grid(row=0, column=1)
    tk.Label(frame_tiempo, text="Segundos:", bg="light pink").grid(row=0, column=2)

    entry_h = tk.Entry(frame_tiempo, width=5)
    entry_m = tk.Entry(frame_tiempo, width=5)
    entry_s = tk.Entry(frame_tiempo, width=5)
    entry_h.grid(row=1, column=0, padx=5)
    entry_m.grid(row=1, column=1, padx=5)
    entry_s.grid(row=1, column=2, padx=5)

    def guardar_config():
        nivel = nivel_var.get()
        reloj = reloj_var.get()
        horas = entry_h.get()
        minutos = entry_m.get()
        segundos = entry_s.get()

        # Validar si modo es temporizador
        if reloj == "temporizador":
            try:
                h = int(horas)
                m = int(minutos)
                s = int(segundos)
                if not (0 <= h <= 2 and 0 <= m <= 59 and 0 <= s <= 59):
                    messagebox.showerror("Error", "Horas: 0-2, Minutos/Segundos: 0-59")
                    return
            except:
                messagebox.showerror("Error", "Ingrese números válidos")
                return
        else:
            h = m = s = 0

        # Guardar archivo JSON
        archivo = open("kakuro2025_configuracion.json", "w", encoding="utf-8")
        datos = {
            "nivel": nivel,
            "modo_tiempo": reloj,
            "horas": h,
            "minutos": m,
            "segundos": s
        }
        json.dump(datos, archivo, indent=4)
        archivo.close()

        messagebox.showinfo("OK", "Configuración guardada")
        ventana.destroy()

    tk.Button(ventana, text="Guardar", bg="light green", command=guardar_config).pack(pady=15)


def ayuda():
    messagebox.showinfo("Ayuda")

def acerca_de():
    mensaje = (
        "Nombre del programa : Kakuro 2025\n"
        "Versión             : 1.0\n"
        "Fecha               : 26 de junio del 2025\n"
        "Autora              : Angie Mariela Alpizar Porras\n"
        "Carné               : 2025079783\n"
        "Curso               : Taller de Programación\n"
        "Institución         : Instituto Tecnológico de Costa Rica"
    )
    messagebox.showinfo("Acerca del sistema", mensaje)

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
