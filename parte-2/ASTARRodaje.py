""" Created by Gabriel Rivera Amor in Dec 2024 
Universidad Carlos III de Madrid """
import sys
from itertools import product
import time
import math


#################################
##### Estructuras de Datos ######
#################################
movimientos_posibles = [(-1, 0), (1, 0), (0, -1), (0, 1), (0,0)]
#ejecutado desde el directorio parte-2
path_tests = "./ASTAR-tests/"

class Estado:
    def __init__(self,positions, time=0):
        #nuestro estado consiste en un diccionario con las posiciones de cada avión, el cual se identifica con su indice, y el tiempo
        self.positions = {}
        for i in range(len(positions)):
            self.positions[i] = positions[i]
        self.time = time

    def __eq__(self, other):
        """para nuestra implementación solo queremos saber si llegamos
        al estado meta por lo que no importará el tiempo"""
        equal = True
        for i in self.positions.keys():
            if self.positions[i] != other.positions[i]:
                equal = False
        return equal

    #para poder reconocer cada estado de una manera única
    def __hash__(self):
        return hash((tuple(sorted(self.positions.items())), self.time))


class Cuadricula:
    #Clase para guardar la cuadrícula
    def __init__(self, color):
        self.color = color
        self.avion = False

    def __str__(self):
        return str(self.color)

class PriorityQueue(object):
    #Nuestra cola contiene la lista [f,estado] por cada estado que se agregue en la lista abierta)
    def __init__(self):
        self.queue = []

    def isEmpty(self):
        return len(self.queue) == 0

    def insert(self, data):
        self.queue.append(data)

    def pop(self):
        min_val = 0
        for i in range(len(self.queue)):
            if self.queue[i][0] < self.queue[min_val][0]:
                min_val = i
        item = self.queue[min_val][1]
        del self.queue[min_val]
        return item

    #verifica si el estado esta dentro de la cola y actualiza el valor de la función f del estado si es mejor
    def actualizar_valor(self, estado, f):
        dentro = False
        for i in range(len(self.queue)):
            if self.queue[i][1] == estado:
                dentro = True
                if self.queue[i][0] > f:
                    self.queue[i][0] = f
        return dentro

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
    for i in range(len(colors)):
        fila = []
        for j in range(len(colors[0])):
            cuadricula = Cuadricula(colors[i][j])
            fila.append(cuadricula)
        mapa.append(fila)
    return start, goal, mapa

def movimientos_validos(pos, mapa):
    #obtenemos los limites del mapa y la x e y del estado
    filas, columnas = len(mapa), len(mapa[0])
    x, y = pos
    #todas los posibles movimientos en general
    posibles = [(x + dx, y + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]]
    #comprobamos que sean válidos dentro del mapa
    return [(nx, ny) for nx, ny in posibles if (0 <= nx < filas) and (0 <= ny < columnas) and (mapa[nx][ny].color != 'G')]

def manhattan(estado, goal):
    #devolvemos la distancia manhattan maxima entre los aviones
    max = 0
    for i in estado.positions.keys():
        actual = estado.positions[i]
        objetivo = goal.positions[i]
        distancia =  (abs(actual[0] - objetivo[0]) + abs(actual[1] - objetivo[1]))
        if distancia > max:
            max = distancia

    return max

def euclides(estado, goal):
    # devolvemos la distancia de euclides maxima entre os aviones
    max = 0
    for i in estado.positions.keys():
        actual = estado.positions[i]
        objetivo = goal.positions[i]
        distancia = math.sqrt((actual[0] - objetivo[0]) ** 2 + (actual[1] - objetivo[1]) ** 2)
        if distancia > max:
            max = distancia
    return max

def hay_conflicto_cruce(posiciones_actuales, posiciones_nuevas):
    #comprobamos con cada avion que el proximo movimiento no cause ningún conflicto
    for avion1, pos1 in posiciones_actuales.items():
        for avion2, pos2 in posiciones_actuales.items():
            if avion1 != avion2:
                if pos1 == posiciones_nuevas.get(avion2) and pos2 == posiciones_nuevas.get(avion1):
                    return True
    return False

def reconstruir_camino(predecesores, estado_final):
    #Reconstruye el camino desde el estado inicial al objetivo utilizando los predecesores
    camino = []
    actual = estado_final
    while actual in predecesores:
        camino.append(actual)
        actual = predecesores[actual]
    camino.append(actual)  # Añadimos el estado inicial
    camino.reverse()  # Invertimos el camino para que esté en orden
    return camino

def escritura_camino(path, camino):
    with open(path, 'w') as f:
        #por cada avión
        for avion in camino[0].positions.keys():
            #recorremos las posiciones del avion en los distintos estados
            for i in range(len(camino)):
                if i < len(camino) -1:
                    pos_inicial = camino[i].positions[avion]
                    siguiente_pos = camino[i + 1].positions[avion]
                    if pos_inicial == siguiente_pos:
                        f.write(f"({pos_inicial[0]},{pos_inicial[1]}) w ")
                    elif pos_inicial[1] < siguiente_pos[1]:
                        f.write(f"({pos_inicial[0]},{pos_inicial[1]})  → ") #flecha para derecha
                    elif pos_inicial[1] > siguiente_pos[1]:
                        f.write(f"({pos_inicial[0]},{pos_inicial[1]})  ← ") #flecha para izquierda
                    elif pos_inicial[0] < siguiente_pos[0]:
                        f.write(f"({pos_inicial[0]},{pos_inicial[1]})  ↓ ") #flecha para abajo
                    elif pos_inicial[0] > siguiente_pos[0]:
                        f.write(f"({pos_inicial[0]},{pos_inicial[1]}) ↑ ") #flecha para arriba

                else:
                    f.write(f"({camino[i].positions[avion][0]},{camino[i].positions[avion][1]}) \n")

def escritura_stats(path, time, makespan, h_inicial, expanded):
    with open(path, 'w') as f:
        #escribimos las estadísticas proporcionadas
        f.write(f"Tiempo total: {time:.2f}s \n")
        f.write(f"Makespan: {makespan} \n")
        f.write(f"h inicial: {h_inicial} \n")
        f.write(f"Nodos expandidos: {expanded} \n")

#################################
########## Función A* ###########
#################################
def ASTAR(start, goal, mapa, heuristica, output_file=None):
    #creamos la lista abierta, los estados visitados, un diccionario que guarde los costes actuales por cada estado y
    #un diccionario para los predecedores
    open_list = PriorityQueue()
    open_list.insert([0, start])
    visitados = set()
    costes = {start: 0}
    predecesores = {}  # Diccionario para rastrear el camino

    while not open_list.isEmpty():
        #sacamos el estado de la lista abierta
        current = open_list.pop()

        if current == goal:
            #encontramos el objetivo
            print("Objetivo conseguido")
            camino = reconstruir_camino(predecesores, current)
            if heuristica == 1:
                return camino, current.time, manhattan(start, goal), len(visitados)
            else:
                return camino, current.time, euclides(start, goal), len(visitados)

        # Generar todas las combinaciones de movimientos para todos los aviones
        movimientos_aviones = []
        for pos in current.positions.values():
            movimientos_aviones.append(movimientos_validos(pos, mapa) + [pos])  # Agregamos la  espera con +[pos]

        # Crear combinaciones de movimientos paralelos
        for combinacion in product(*movimientos_aviones):  # Todas las combinaciones posibles
            nuevo_positions = {i: combinacion[i] for i in range(len(combinacion))}

            # Comprobamoe que no haya colisiones
            if len(set(nuevo_positions.values())) != len(nuevo_positions):
                continue

            # Comprobamos que no haya conflictos de cruce
            if hay_conflicto_cruce(current.positions, nuevo_positions):
                continue

            # Creamos el nuevo estado
            nuevo_estado = Estado(nuevo_positions, current.time + 1)
            coste = costes[current] + 1  # Todos los movimientos tienen coste 1
            if nuevo_estado in visitados:
                if coste > costes[nuevo_estado]:  # Si el nuevo coste es mayor ignoramos al estado y pasamos al siguiente
                    continue

            if nuevo_estado not in costes or coste < costes[nuevo_estado]:
                costes[nuevo_estado] = coste
                predecesores[nuevo_estado] = current  # Guardamos el predecesor
                if heuristica == 1:
                    heuristic = manhattan(nuevo_estado, goal)
                else:
                    heuristic = euclides(nuevo_estado, goal)
                f = coste + heuristic
                #si se encuentra en la lista abierta y tiene un mejor coste, lo actualizamos, sino, lo agregamos a la lista abierta
                if not open_list.actualizar_valor(nuevo_estado, f):
                    open_list.insert([f, nuevo_estado])

        #agregamos el estado a los que ya hemos visitado
        visitados.add(current)

    print("No se encontró solución.")
    return None, None, None, None

if __name__ == "__main__":
    #empezamos el temporizador y cargamos los datos pasados como argumento
    inicio = time.time()
    archivo_mapa = sys.argv[1]
    #para conseguir el nombre del mapa
    indice_mapa = 14
    nombre_mapa = ""
    for i in  range(indice_mapa,len(archivo_mapa)):
        if archivo_mapa[i] != ".":
            nombre_mapa += archivo_mapa[i]
        else:
            break
    num_heuristica = int(sys.argv[2])
    #cargamos el mapa
    start, goal, mapa = cargar_mapa(archivo_mapa)
    #hacemos la busqueda
    camino, makespan, h_inicial, expanded = ASTAR(start, goal, mapa, num_heuristica)
    #no se encontró una solucion
    if camino == None:
        path = path_tests + "mapa-" + str(num_heuristica) + ".output"
        with open(path, 'w') as f:
            f.write("No existe una solución para este problema")

    else:
        #escribimos el fichero outpu
        path_camino = path_tests + nombre_mapa + "-" + str(num_heuristica) + ".output"
        escritura_camino(path_camino, camino)
        #terminamos el tiempo y calculamos el tiempo total de ejecucion
        fin = time.time()
        tiempo_ejecucion = fin - inicio
        #pasamos todas las estadisticas y escribimos el fichero stat
        path_stat = path_tests + nombre_mapa + "-" + str(num_heuristica) + ".stat"
        escritura_stats(path_stat, tiempo_ejecucion, makespan, h_inicial, expanded)