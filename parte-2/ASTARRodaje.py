""" Created by Gabriel Rivera Amor in Dec 2024 
Universidad Carlos III de Madrid """
import sys
from Data_Structures.Graph import cargar_mapa


if __name__ == "__main__":
    archivo_mapa = sys.argv[1]
    num_heuristica = int(sys.argv[2])

    start, goal, mapa = cargar_mapa(archivo_mapa)

    for j in range(len(mapa)):
        for i in range(len(mapa[0])):
            print(mapa[i][j])