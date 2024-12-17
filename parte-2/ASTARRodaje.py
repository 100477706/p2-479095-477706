""" Created by Gabriel Rivera Amor in Dec 2024 
Universidad Carlos III de Madrid """
import sys

#################################
##### Estructuras de Datos ######
#################################
movimientos_posibles = [(-1, 0), (1, 0), (0, -1), (0, 1), (0,0)]

class Estado:
    def __init__(self,positions, time=0):
        self.positions = {}
        for i in range(len(positions)):
            self.positions[i] = positions[i]
        self.time = time
        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        """para nuestra implementación solo queremos saber si llegamos
        al estado meta por lo que no importará el tiempo"""
        equal = True
        for i in self.positions.keys():
            if self.positions[i] != other.positions[i]:
                equal = False
        return equal

    def find_adjacent(self, mapa):
        adjacent = []
        aviones = []
        width = len(mapa[0])
        height = len(mapa)
        for movimiento in movimientos_posibles:
            for avion in self.positions.keys():
                col = self.positions[avion][0] + movimiento[0]
                row = self.positions[avion][1] + movimiento[1]
                if self.check_cuadricula(mapa, col, row):
                    aviones.append((col, row))

    def check_cuadricula(self, mapa, col, row):
        posible = True
        width = len(mapa[0])
        height = len(mapa)
        if col >= width or row >= height:
            posible = False
        if col < 0 or row < 0:
            posible = False
        if mapa[col][row].color == 'G':
            posible = False
        if mapa[col][row].avion:
            posible = False

        return posible



class Cuadricula:
    def __init__(self, color):
        self.color = color
        self.avion = False

    def __str__(self):
        return str(self.color)

class PriorityQueue(object):
    """" Nuestra cola contiene la lista [f,estado] por cada estado que se agregue en la lista abierta)"""
    def __init__(self):
        self.queue = []

    def isEmpty(self):
        return len(self.queue) == 0

    def insert(self, data):
        self.queue.append(data)

    def pop(self):
        max_val = 0
        for i in range(len(self.queue)):
            if self.queue[i][0] > self.queue[max_val][0]:
                max_val = i
        item = self.queue[max_val][1]
        del self.queue[max_val]
        return item

    #actualiza el valor de la función f de un estado en la lista abierta
    def actualizar_valor(self, estado, f):
        for i in range(len(self.queue)):
            if self.queue[i][1] == estado:
                if self.queue[i][0] > f:
                    self.queue[i][0] = f

#################################
##### Funciones Auxiliares ######
#################################

def cargar_mapa(archivo):
    #Divido los caracteres dentro del mapa
    with open(archivo, 'r') as f:
        data = [line.strip().split(';') for line in f.readlines()]
    #saco el número de aviones
    num_aviones = int(data[0][0])
    start_positions = []
    goal_positions = []
    prueba = data[1][0]
    #Saco las posiciones iniciales y destino de cada avion
    for i in range(1, num_aviones + 1):
        start = (int(data[i][0][1]), int(data[i][0][3]))
        goal = (int(data[i][0][7]), int(data[i][0][9]))
        start_positions.append(start)
        goal_positions.append(goal)
    # Creamos el estado inicial y el estado meta
    start = Estado(start_positions, 0)
    goal = Estado(goal_positions, 0)
    #Saco las letras del mapa
    colors = [row for row in data[num_aviones + 1:]]
    #creamos el mapa que será una matriz de instancias Cuadricula
    mapa = []
    for j in range(len(colors)):
        fila = []
        for i in range(len(colors[0])):
            cuadricula = Cuadricula(colors[i][j])
            fila.append(cuadricula)
        mapa.append(fila)
    return start, goal, mapa

def movimientos_validos(pos, mapa):
    filas, columnas = len(mapa), len(mapa[0])
    x, y = pos
    posibles = [(x + dx, y + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]]
    return [(nx, ny) for nx, ny in posibles if 0 <= nx < filas and 0 <= ny < columnas and mapa[nx][ny].color != 'G']

def manhattan(estado, goal):
    suma = 0
    for i in estado.positions.keys():
        actual = estado.positions[i]
        objetivo = goal.positions[i]
        suma += (abs(actual[0] - objetivo[0]) + abs(actual[1] - objetivo[1]))

    return suma

def reconstruir_camino(estado):
    pass

#################################
########## Función A* ###########
#################################
def ASTAR(start, goal, mapa, heuristica):
    open_list = PriorityQueue() #frontera
    open_list.insert((0,start))
    visitados = set()
    costes = {start: 0}

    while open_list:
        current = open_list.pop()

        if current == goal:
            return reconstruir_camino(current)

        if current in visitados:
            continue
        visitados.add(current)

        for i, pos in enumerate(current.positions.values()):
            for nuevo_pos in movimientos_validos(pos, mapa) + [pos]:
                nuevo_estado = list(current.positions.values())
                nuevo_estado[i] = nuevo_pos
                nuevo_estado = Estado(nuevo_estado, current.time + 1)

                if nuevo_estado in visitados:
                    continue

                coste = costes[current] + 1  # Todos los movimientos tienen coste 1
                if nuevo_estado not in costes or coste < costes[nuevo_estado]:
                    costes[nuevo_estado] = coste
                    if heuristica == 1:
                        heuristic = manhattan(nuevo_estado, goal)
                    else:
                        heuristic = manhattan(nuevo_estado, goal)
                    #heapq.heappush(frontera, (coste + heur, nuevo_estado))
    return None

if __name__ == "__main__":
    archivo_mapa = sys.argv[1]
    num_heuristica = int(sys.argv[2])
    start, goal, mapa = cargar_mapa(archivo_mapa)
    ASTAR(start, goal, mapa, num_heuristica)


    print(start == goal)