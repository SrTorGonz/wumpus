import tkinter as tk
import random

# Constantes del juego
CELL_SIZE = 100
GRID_SIZE = 7  # Tamaño inicial del tablero
is_hidden = True  # Ocultar el mundo al inicio
game_running = True
auto_moving = False  # Estado de movimiento automático
treasures_collected = 0
total_treasures = 0
safe_cells = set()     # Celdas que el agente infiere como seguras
danger_cells = set()   # Celdas potencialmente peligrosas
percepciones = {}  # clave: (i,j), valor: "brisa", "hedor", etc.
# Inicializar la ventana principal
window = tk.Tk()
window.title("Mundo de Wumpus")

# Cargar y ajustar el tamaño de las imágenes (ajustando a las celdas)
agente_img = tk.PhotoImage(file="agente.png").subsample(5, 5)  # Redimensionar la imagen para ajustarse
wumpus_img = tk.PhotoImage(file="wumpus.png").subsample(5, 5)
hueco_img = tk.PhotoImage(file="hueco.png").subsample(10, 10)
oro_img = tk.PhotoImage(file="oro.png").subsample(5, 5)
hedor_img = tk.PhotoImage(file="hedor.png").subsample(5, 5)
brisa_img = tk.PhotoImage(file="brisa.png").subsample(5, 5)

# Variables de Canvas y Frame
canvas = tk.Canvas(window, width=GRID_SIZE * CELL_SIZE, height=GRID_SIZE * CELL_SIZE)
canvas.grid(row=0, column=1)  # Colocamos el canvas en la segunda columna

# Crear variables globales para el tablero y elementos
tablero = []
visited = []  # Memoria de casillas visitadas (seguras)

movement_stack = []  # Pila de movimientos (backtracking)
danger_zones = []  # Memoria de casillas peligrosas (hedor, brisa)
elementos = {
    "aventurero": agente_img,
    "wumpus": wumpus_img,
    "tesoro": oro_img,
    "pozo": hueco_img,
    "brisa": brisa_img,
    "hedor": hedor_img,
}


# Función para inicializar el tablero
def inicializar_tablero():
    global tablero, agent_position, treasures_collected, game_running, auto_moving, total_treasures, visited, movement_stack, danger_zones
    game_running = True
    auto_moving = False
    treasures_collected = 0
    total_treasures = 0
    tablero = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]  # Tablero vacío
    visited = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]  # Memoria de casillas visitadas (seguras)
    movement_stack = []  # Pila de movimientos
    danger_zones = []  # Memoria de casillas peligrosas
    agent_position = [0, 0]  # Agente en la posición inicial
    colocar_elementos()
    mostrar_tablero()

# Función para mostrar el tablero con visibilidad ajustada
def mostrar_tablero():
    canvas.delete("all")
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            color = "black" if is_hidden else "white"
            if visited[i][j]:
                color = "green"  # Pintamos las casillas recorridas de verde
            dibujar_celda(i, j, color)
            if tablero[i][j] is not None and not is_hidden:
                canvas.create_image(
                    j * CELL_SIZE + CELL_SIZE // 2,
                    i * CELL_SIZE + CELL_SIZE // 2,
                    image=elementos[tablero[i][j]]
                )
    actualizar_agente()

# Dibujar celdas individuales
def dibujar_celda(fila, columna, color):
    x1, y1 = columna * CELL_SIZE, fila * CELL_SIZE
    x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
    canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")

# Colocar elementos aleatorios en el tablero
def colocar_elementos():
    global treasures_collected, total_treasures
    # Colocar Wumpus
    colocar_elemento_aleatorio("wumpus")

    # Colocar pozos y brisas dinámicamente (2 pozos, 3 brisas)
    max_pozos = 2  # 2 hoyos
    for _ in range(max_pozos):
        colocar_pozo_y_brisa()

    # Colocar tesoros dinámicamente (3 tesoros)
    max_tesoros = 3
    treasures_collected = 0
    total_treasures = max_tesoros
    for _ in range(max_tesoros):
        colocar_elemento_aleatorio("tesoro")

def colocar_elemento_aleatorio(tipo):
    """Coloca un elemento aleatoriamente en una posición vacía del tablero."""
    while True:
        fila, columna = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
        if tablero[fila][columna] is None:
            tablero[fila][columna] = tipo
            if tipo == "wumpus":  # Si es un wumpus, colocar hedor alrededor
                colocar_hedor_alrededor(fila, columna)
            break

def colocar_pozo_y_brisa():
    """Coloca un pozo en una posición aleatoria y genera brisas en las casillas adyacentes."""
    while True:
        fila, columna = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
        if tablero[fila][columna] is None:
            tablero[fila][columna] = "pozo"
            # Colocar brisas en las celdas adyacentes
            for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ni, nj = fila + di, columna + dj
                if 0 <= ni < GRID_SIZE and 0 <= nj < GRID_SIZE and tablero[ni][nj] is None:
                    tablero[ni][nj] = "brisa"
            break

def colocar_hedor_alrededor(fila, columna):
    """Coloca hedor en las casillas adyacentes al Wumpus."""
    for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        ni, nj = fila + di, columna + dj
        if 0 <= ni < GRID_SIZE and 0 <= nj < GRID_SIZE and tablero[ni][nj] is None:
            tablero[ni][nj] = "hedor"



# Función para registrar las casillas peligrosas (hedor o brisa) en el mapa
def registrar_zonas_peligrosas():
    global danger_zones
    danger_zones = []  # Reseteamos la lista de zonas peligrosas
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if tablero[i][j] in ["hedor", "brisa"]:
                danger_zones.append((i, j))  # Agregamos la casilla al mapa de zonas peligrosas

# Reiniciar el tablero
def reiniciar_mundo():
    inicializar_tablero()
    registrar_zonas_peligrosas()  # Actualizamos las zonas peligrosas cada vez que reiniciamos

# Cambiar el tamaño del tablero basado en el input del usuario
def cambiar_tamano():
    global GRID_SIZE
    try:
        nuevo_tamano = int(size_entry.get())
        if nuevo_tamano > 1:  # Validar que el tamaño sea mayor a 1
            GRID_SIZE = nuevo_tamano
            canvas.config(width=GRID_SIZE * CELL_SIZE, height=GRID_SIZE * CELL_SIZE)
            reiniciar_mundo()
        else:
            print("Por favor, ingresa un tamaño mayor a 1.")
    except ValueError:
        print("Por favor, ingresa un número válido.")

# Ocultar o mostrar el mundo
def toggle_mundo():
    global is_hidden
    is_hidden = not is_hidden
    mostrar_tablero()

# Actualizar posición del agente
def actualizar_agente():
    i, j = agent_position
    dibujar_celda(i, j, "")
    if is_hidden:
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                ni, nj = i + di, j + dj
                if 0 <= ni < GRID_SIZE and 0 <= nj < GRID_SIZE:
                    dibujar_celda(ni, nj, "white")
    canvas.create_image(
        j * CELL_SIZE + CELL_SIZE // 2,
        i * CELL_SIZE + CELL_SIZE // 2,
        image=elementos["aventurero"]
    )

# Verificar si el juego termina
def verificar_fin_de_juego():
    i, j = agent_position
    if tablero[i][j] == "wumpus" or tablero[i][j] == "pozo":
        mostrar_pantalla_fin("¡Caíste en una trampa!")
    elif tablero[i][j] == "tesoro":
        tablero[i][j] = None  # Recolectar el tesoro
        global treasures_collected
        treasures_collected += 1
        if treasures_collected >= min(GRID_SIZE // 2, 4):
            mostrar_pantalla_fin("¡Recolectaste todos los tesoros!")

# Pantalla de fin de juego
def mostrar_pantalla_fin(mensaje):
    global game_running, auto_moving
    game_running = False
    auto_moving = False
    fin_ventana = tk.Toplevel(window)
    fin_ventana.title("Mundo Finalizado")
    tk.Label(fin_ventana, text=mensaje).pack(pady=10)
    tk.Button(fin_ventana, text="Volver a Intentar", command=lambda: [fin_ventana.destroy(), reiniciar_mundo()]).pack(pady=5)

def percibir_y_razonar():
    i, j = agent_position
    percepcion = tablero[i][j]

    percepciones[(i, j)] = percepcion
    safe_cells.add((i, j))

    if percepcion not in ["hedor", "brisa"]:
        for di, dj in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            ni, nj = i + di, j + dj
            if 0 <= ni < GRID_SIZE and 0 <= nj < GRID_SIZE:
                safe_cells.add((ni, nj))
    else:
        for di, dj in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            ni, nj = i + di, j + dj
            if (
                0 <= ni < GRID_SIZE and 0 <= nj < GRID_SIZE and
                (ni, nj) not in visited
            ):
                danger_cells.add((ni, nj))

# Movimiento aleatorio del agente
def mover_agente_logico():
    i, j = agent_position
    percibir_y_razonar()  # Actualiza el conocimiento del mundo

    # Buscar celdas adyacentes seguras y no visitadas
    opciones_seguras = []
    for di, dj in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
        ni, nj = i + di, j + dj
        if (
            0 <= ni < GRID_SIZE and 0 <= nj < GRID_SIZE and
            (ni, nj) in safe_cells and
            not visited[ni][nj] and
            (ni, nj) not in danger_cells
        ):
            opciones_seguras.append((ni, nj))

    if opciones_seguras:
        fila, columna = random.choice(opciones_seguras)
        mover_agente(fila, columna)
    else:
        # Evitar volver a celdas con brisa ya visitadas
        alternativas = []
        for di, dj in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            ni, nj = i + di, j + dj
            if (
                0 <= ni < GRID_SIZE and 0 <= nj < GRID_SIZE and
                (ni, nj) in safe_cells and
                not (percepciones.get((ni, nj)) == "brisa" and visited[ni][nj])
            ):
                alternativas.append((ni, nj))

        if alternativas:
            fila, columna = random.choice(alternativas)
            mover_agente(fila, columna)
        else:
            mensaje_label.config(text="No hay opciones seguras sin brisa disponibles. El agente se detiene.")
            print("No hay opciones seguras sin brisa disponibles. El agente se detiene.")
            auto_moving = False


def manejar_peligro(fila, columna):
    print(f"Agente entra en ({fila}, {columna}) con {tablero[fila][columna]}. Marcando como peligrosa y evitando futuras visitas.")
    danger_cells.add((fila, columna))
    safe_cells.discard((fila, columna))
    visited[fila][columna] = True
    mostrar_tablero()

# Movimiento controlado del agente
def mover_agente(fila, columna):
    if game_running and 0 <= fila < GRID_SIZE and 0 <= columna < GRID_SIZE:
          
        # Registrar la casilla como visitada
        visited[fila][columna] = True  # Marcar como visitada
        agent_position[0], agent_position[1] = fila, columna
        movement_stack.append((fila, columna))  # Apilar el movimiento
        mostrar_tablero()
        verificar_fin_de_juego()
        # Manejar peligro con animación
        if tablero[fila][columna] in ["hedor", "brisa"]:
            canvas.after(200, manejar_peligro, fila, columna)
            return

# Movimiento manual
def mover_agente_manual(event):
    mover_agente_logico()

# Movimiento automático continuo
def movimiento_automatico():
    global auto_moving
    if game_running and auto_moving:
        mover_agente_logico()
        window.after(800, movimiento_automatico)  # Movimiento cada 2 segundos

def iniciar_movimiento_automatico():
    global auto_moving
    auto_moving = True
    movimiento_automatico()

# Crear un Frame para los controles en la derecha
control_frame = tk.Frame(window)
control_frame.grid(row=0, column=2, sticky="n")  # Control a la derecha

# Botones y controles en la barra lateral
tk.Button(control_frame, text="Reiniciar Mundo", command=reiniciar_mundo).pack(pady=5)
tk.Button(control_frame, text="Visualizar Mundo", command=toggle_mundo).pack(pady=5)
tk.Button(control_frame, text="Movimiento Automático", command=iniciar_movimiento_automatico).pack(pady=5)

# Entrada para el tamaño del tablero
size_label = tk.Label(control_frame, text="Tamaño del Mundo:")
size_label.pack(pady=5)
size_entry = tk.Entry(control_frame, width=5)
size_entry.insert(0, "7")  # Tamaño inicial 7
size_entry.pack(pady=5)
tk.Button(control_frame, text="Cambiar Tamaño", command=cambiar_tamano).pack(pady=5)

# Crear un Label para mostrar mensajes
mensaje_label = tk.Label(control_frame, text="", fg="red")
mensaje_label.pack(pady=10)

# Enlazar la barra espaciadora para movimiento manual
window.bind("<space>", mover_agente_manual)

# Inicializar el tablero por primera vez
inicializar_tablero()
window.mainloop()
