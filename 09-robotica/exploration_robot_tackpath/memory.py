import struct
import os

# Use um caminho absoluto ou relativo; certifique-se de que o diretório existe
MEMORY_FILE = "route_memory.bin"

class RouteMemory:

    MAX_POINTS = 50

    def __init__(self):
        self.route = []
        self.load()

    def load(self):
        self.route.clear()
        if not os.path.exists(MEMORY_FILE):
            return
        try:
            with open(MEMORY_FILE, "rb") as f:
                while True:
                    data = f.read(8)
                    if not data:
                        break
                    x, offset = struct.unpack("ii", data)
                    self.route.append({"x": x, "offset": offset})
        except Exception as e:
            print(f"Erro ao carregar memória: {e}")

    def save(self):
        try:
            with open(MEMORY_FILE, "wb") as f:
                for item in self.route:
                    f.write(struct.pack("ii", item["x"], item["offset"]))
        except Exception as e:
            print(f"Erro ao salvar memória: {e}")

    def save_point(self, obstacle_x, offset):
        # Evita duplicatas próximas
        for item in self.route:
            if abs(item["x"] - obstacle_x) < 30:
                return
        if len(self.route) >= self.MAX_POINTS:
            return
        self.route.append({"x": obstacle_x, "offset": offset})
        self.save()

    def find_route(self, obstacle_x):
        for item in self.route:
            if abs(item["x"] - obstacle_x) < 30:
                return item
        return None