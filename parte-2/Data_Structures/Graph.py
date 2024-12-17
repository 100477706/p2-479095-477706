
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

def cargar_mapa(archivo):
    #Divido los caracteres dentro del mapa
    with open(archivo, 'r') as f:
        data = [line.strip().split(';') for line in f.readlines()]
    #saco el número de aviones
    num_aviones = int(data[0][0])
    #Saco las posiciones iniciales y destino de cada avion
    aviones = [((int(data[i][0][1]), int(data[i][0][3])),  # Inicial
                (int(data[i][1][1]), int(data[i][1][3])))  # Destino
               for i in range(1, num_aviones + 1)]
    #Saco las letras del mapa
    colors = [row for row in data[num_aviones + 1:]]
    #Creamos el estado inicial y el estado meta
    start_positions = []
    goal_positions = []
    for avion in aviones:
        start_positions.append(avion[0])
        goal_positions.append(avion[1])
    start = Estado(start_positions, 0)
    goal = Estado(goal_positions, 0)
    #creamos el mapa que será una matriz de instancias Cuadricula
    mapa = []
    for j in range(len(colors)):
        fila = []
        for i in range(len(colors[0])):
            cuadricula = Cuadricula(colors[i][j])
            fila.append(cuadricula)
        mapa.append(fila)
    return start, goal, mapa