import tkinter as tk
import random
from PIL import Image, ImageTk

GRID_SIZE = 6
CELL_SIZE = 110

class WumpusGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Juego del Wumpus")
        self.canvas = tk.Canvas(root, width=GRID_SIZE*CELL_SIZE, height=GRID_SIZE*CELL_SIZE, bg="white")
        self.canvas.pack()

        self.btn_frame = tk.Frame(root)
        self.btn_frame.pack()
        self.randomize_btn = tk.Button(self.btn_frame, text="Randomizar", command=self.randomize_world)
        self.randomize_btn.pack(side=tk.LEFT)
        self.start_btn = tk.Button(self.btn_frame, text="Comenzar", command=self.start_game)
        self.start_btn.pack(side=tk.LEFT)

        self.grid = [['' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.agent_pos = (GRID_SIZE-1, 0)
        self.score = 0
        self.arrow_used = False

        self.images = {
            "P": tk.PhotoImage(file="pit.png"),
            "B": tk.PhotoImage(file="brisa.png"),
            "W": tk.PhotoImage(file="wumpus.png"),
            "H": tk.PhotoImage(file="hedor.png"),
            "G": tk.PhotoImage(file="oro.png"),
            "A": tk.PhotoImage(file="agente.png")
        }
        self.load_images()


    def load_images(self):
        image_files = {
            "P": "pit.png",
            "B": "brisa.png",
            "W": "wumpus.png",
            "H": "hedor.png",
            "G": "oro.png",
            "A": "agente.png"
        }

        for key, file in image_files.items():
            img = Image.open(file)
            img = img.resize((CELL_SIZE, CELL_SIZE), Image.Resampling.LANCZOS)
            self.images[key] = ImageTk.PhotoImage(img)

    def randomize_world(self):
        self.grid = [['' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.agent_pos = (GRID_SIZE-1, 0)
        self.grid[self.agent_pos[0]][self.agent_pos[1]] = 'A'

        forbidden = {self.agent_pos, (GRID_SIZE-2, 1)}  # Posición del agente y su diagonal derecha arriba
        positions = [(i, j) for i in range(GRID_SIZE) for j in range(GRID_SIZE) if (i, j) not in forbidden]

        # Pits
        self.pits = random.sample(positions, 2)
        for pit in self.pits:
            self.grid[pit[0]][pit[1]] = 'P'
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                x, y = pit[0] + dx, pit[1] + dy
                if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE and self.grid[x][y] == '':
                    self.grid[x][y] = 'B'  # Brisa

        # Wumpus
        positions = [pos for pos in positions if pos not in self.pits]
        self.wumpus = random.choice(positions)
        self.grid[self.wumpus[0]][self.wumpus[1]] = 'W'
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            x, y = self.wumpus[0] + dx, self.wumpus[1] + dy
            if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE and self.grid[x][y] == '':
                self.grid[x][y] = 'H'  # Hedor

        # Oro
        positions = [pos for pos in positions if pos not in self.pits and pos != self.wumpus]
        self.golds = random.sample(positions, 2)
        for g in self.golds:
            self.grid[g[0]][g[1]] = 'G'

        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                x1 = j * CELL_SIZE
                y1 = i * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black")

                content = self.grid[i][j]
                if content in self.images:
                    self.canvas.create_image(x1 + CELL_SIZE//2, y1 + CELL_SIZE//2, image=self.images[content])

    def start_game(self):
        self.score = 0
        self.arrow_used = False
        # Aquí puedes implementar la lógica de movimiento del agente
        # Recuerda usar -1 por movimiento, -10 si dispara, +1000 si recoge todo el oro y regresa,
        # y -1000 si cae en pit o es devorado por el wumpus.
        print("Iniciando simulación del agente...")

if __name__ == "__main__":
    root = tk.Tk()
    game = WumpusGame(root)
    root.mainloop()
