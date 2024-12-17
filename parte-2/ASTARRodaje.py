""" Created by Gabriel Rivera Amor in Dec 2024 
Universidad Carlos III de Madrid """
import sys

#################################
##### Estructuras de Datos ######
#################################

class Estado:
    def __init__(self,positions, time=0):
        self.positions = {}
        for i in range(len(positions)):
            self.positions[i+1] = positions[i]
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

class Cuadricula:
    def __init__(self, color):
        self.color = color
        self.avion = False

    def __str__(self):
        return str(self.color)

class PriorityQueue(object):
    def __init__(self):
        self.queue = []

    def __str__(self):
        return ' '.join([str(i) for i in self.queue])

    # for checking if the queue is empty
    def isEmpty(self):
        return len(self.queue) == 0

    # for inserting an element in the queue
    def insert(self, data):
        self.queue.append(data)

    # for popping an element based on Priority
    def delete(self):
        try:
            max_val = 0
            for i in range(len(self.queue)):
                if self.queue[i][0] > self.queue[max_val]:
                    max_val = i
            item = self.queue[max_val][0]
            del self.queue[max_val]
            return item
        except IndexError:
            print()
            exit()

class ASTAR:
    def __init__(self,start:object, goal:object, map, heuristic):
        self.map = map
        self.start = start
        self.goal = goal
        if heuristic ==1:
            self.heuristic = 1
        else:
            self.heuristic = 2

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


if __name__ == "__main__":
    archivo_mapa = sys.argv[1]
    num_heuristica = int(sys.argv[2])
    start, goal, mapa = cargar_mapa(archivo_mapa)

    print(start == goal)