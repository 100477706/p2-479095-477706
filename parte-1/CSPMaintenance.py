import csv

from constraint import Problem
import sys


#Función encargada de leer el archivo de entrada
def leer_entrada(ruta_archivo):
    with open(ruta_archivo, 'r') as archivo:
        lineas = archivo.readlines()

    # Extraer franjas horarias
    franjas = int(lineas[0].split(":")[1].strip())

    # Dimensiones de la matriz
    # dimensiones = tuple(map(int, lineas[1].strip().split("x")))
    m_filas = int(lineas[1].split("x")[1].strip())
    m_columnas = int(lineas[1].split("x")[0].strip())

    # Talleres estándar, especialistas y parkings
    talleres_std = [tuple(map(int, pos.strip('()').split(','))) for pos in lineas[2].split(':')[1].strip().split()]
    talleres_spc = [tuple(map(int, pos.strip('()').split(','))) for pos in lineas[3].split(':')[1].strip().split()]
    parkings = [tuple(map(int, pos.strip('()').split(','))) for pos in lineas[4].split(':')[1].strip().split()]

    # Datos de los aviones
    aviones = []
    for linea in lineas[5:]:
        partes = linea.strip().split("-")
        aviones.append({
            'id': int(partes[0]),
            'tipo': partes[1],
            'restr': partes[2] == 'T',
            't1': int(partes[3]),
            't2': int(partes[4]),
        })

    return franjas, m_filas, m_columnas, talleres_std, talleres_spc, parkings, aviones

#Función encargada de garantizar la cantidad de aviones
def restriccion_talleres(*asignaciones):
    conteo = {}
    jumbo_present = set()
    for posicion, avion in zip(asignaciones, aviones):
        if avion['tipo'] == 'JMB':
            if posicion in jumbo_present or conteo.get(posicion, 0) > 0:
                return False  # No más de un JUMBO por taller
            jumbo_present.add(posicion)
            conteo[posicion] = conteo.get(posicion, 0) + 2
        else:
            conteo[posicion] = conteo.get(posicion, 0) + 1
            if conteo[posicion] > 2:
                return False  # No más de dos aviones estándar
    return True

#Función encargada de establecer los posibles dominios segun las tareas a realizar
def restriccion_tipos(posiciones, aviones, talleres_std, talleres_spc, parkings):
    conteo_talleres = {}  # Lleva el registro de aviones en talleres
    jumbo_present = set()  # Lleva el registro de talleres con aviones JUMBO
    conteo_parkings = {}  # Lleva el registro de aviones en parkings

    for avion, posicion in zip(aviones, posiciones):
        if posicion in talleres_spc:
            if (avion['t2'] >= 1) or (avion['t1'] >= 1):  # Taller especializado
                if avion['tipo'] == 'JMB':
                    if posicion in jumbo_present:
                        return False  # No puede haber más de un JUMBO en un taller
                    jumbo_present.add(posicion)
                conteo_talleres[posicion] = conteo_talleres.get(posicion, 0) + 1
                if conteo_talleres[posicion] > 2:
                    return False  # Un taller especializado puede atender solo un avión

        if posicion in talleres_std and avion['t1'] >= 1:  # Taller estándar
            if avion['tipo'] == 'JMB':
                if posicion in jumbo_present:
                    return False  # No puede haber más de un JUMBO en el taller
                jumbo_present.add(posicion)
            conteo_talleres[posicion] = conteo_talleres.get(posicion, 0) + 1
            if conteo_talleres[posicion] > 2:
                return False  # Un taller estándar puede atender hasta 2 aviones

        if posicion in parkings:
            # Verificar que los talleres estén ocupados antes de permitir parking
            if any(count < 2 for pos, count in conteo_talleres.items() if
                   pos in talleres_std) or \
                    any(count < 1 for pos, count in conteo_talleres.items() if
                        pos in talleres_spc):
                return False  # Hay talleres disponibles, no puede ir a un parking
            if avion['tipo'] == 'JMB':
                if posicion in jumbo_present:
                    return False  # No puede haber más de un JUMBO en un taller
                jumbo_present.add(posicion)
            conteo_parkings[posicion] = conteo_parkings.get(posicion, 0) + 1
            if conteo_parkings[posicion] > 2:
                return False  # Un parking solo puede albergar un avión

    return True

#Función encargada de imponer el orden de ejecución de las tareas
def restriccion_orden_tareas(avion, talleres_std, talleres_spc, parkings, *asignaciones):
    t2 = avion['t2']  # Número de tareas tipo 2 pendientes
    t1 = avion['t1']  # Número de tareas tipo 1 pendientes

    for i, posicion in enumerate(asignaciones):
        # Mientras haya tareas de tipo 2 pendientes
        if t2 > 0:
            if posicion not in talleres_spc:
                if posicion in parkings:
                    continue  # Tarea no completada, pero asignado a parking
                return False
            t2 -= 1  # Consumir una tarea de tipo 2

        # Cuando no queden tareas de tipo 2, pero sí de tipo 1
        elif t1 > 0:
            if (posicion in talleres_std or posicion in talleres_spc):
                t1 -= 1  # Consumir una tarea de tipo 1
            else:
                if posicion in parkings:
                    continue  # Tarea no completada, pero asignado a parking
                return False

    # Verificar si al final quedaron tareas sin completar
    if t1 > 0 or t2 > 0:
        return False
    return True

#Función que verifica que todas las tareas se han realizado
def verificar_completitud(asignaciones, tareas, talleres_std, talleres_spc):
    return sum(1 for pos in asignaciones if pos in talleres_std + talleres_spc) >= tareas

# Función que verifica si las tareas T2 están cubiertas en talleres especializados
def verificar_tarea(asignaciones, required_t2, talleres_spc):
    return sum(1 for pos in asignaciones if pos in talleres_spc) >= required_t2

#Función que establece las restricciones de los espacios para permitir la maniobrabilidad
def restriccion_maniobrabilidad(m_fila, m_columna, *asignaciones):
    ocupados = set(asignaciones)
    for posicion in ocupados:
        x, y = posicion
        adyacentes = [
            (x - 1, y), (x + 1, y),  # Vertical
            (x, y - 1), (x, y + 1)  # Horizontal
        ]
        adyacentes_validos = [adj for adj in adyacentes if adj[0] >= 0 and adj[1] >= 0 and adj[0]
                              < m_columna and adj[1] < m_fila]


        # Verificar si al menos uno de los adyacentes está vacío
        if not any(adj not in ocupados for adj in adyacentes_validos):
            return False  # No hay adyacente vacío

    return True

#Función encargada de garantizar los espacios necesarios para mover aviones JUMBO
def restriccion_no_jumbos_adyacentes(aviones, *asignaciones):
    ocupados = set(asignaciones)  # Todas las posiciones asignadas
    jumbos = [avion for avion in aviones if avion['tipo'] == 'JMB']  # Filtrar aviones JUMBO
    jumbo_asignaciones = {pos for avion, pos in zip(aviones, asignaciones) if
                          avion['tipo'] == 'JMB'}

    for posicion in jumbo_asignaciones:
        x, y = posicion

        # Generar las posiciones adyacentes
        adyacentes = [
            (x - 1, y), (x + 1, y),  # Verticales
            (x, y - 1), (x, y + 1)  # Horizontales
        ]

        # Filtrar las posiciones válidas (dentro del tablero y asignadas a JUMBOs)
        adyacentes_jumbos = [adj for adj in adyacentes if adj in jumbo_asignaciones]

        # Si hay algún JUMBO en los adyacentes, la restricción no se cumple
        if adyacentes_jumbos:
            return False

    return True

#Función encargada de escribir en el archivo de salida
def escribir_salida(output_file, solutions, aviones, franjas, talleres_std, talleres_spc):
    """
    Escribe las soluciones en un archivo CSV.
    """
    with open(output_file, mode="w", newline="") as file:
        writer = csv.writer(file)

        # Escribir el número de soluciones
        writer.writerow([f"N. Soluciones: {len(solutions)}"])

        # Iterar sobre las soluciones
        for i, solution in enumerate(solutions, start=1):
            writer.writerow([f"Solución {i}:"])

            # Iterar sobre los aviones
            for avion in aviones:
                asignaciones = []
                for franja in range(franjas):
                    key = f"A{avion['id']}_T{franja}"
                    if key in solution:
                        asignacion = solution[key]
                        if asignacion in talleres_spc:
                            tipo_taller = "SPC"

                        elif asignacion in talleres_std:
                            tipo_taller = "STD"

                        else:
                            tipo_taller = "PRK"  # Para parkings
                        asignaciones.append(f"{tipo_taller}{asignacion}")
                    else:
                        asignaciones.append("None")

                # Escribir la línea del avión
                writer.writerow([
                    f"{avion['id']}-{avion['tipo']}-{avion['restr']}-{avion['t1']}-{avion['t2']}:",
                    " , ".join(asignaciones)
                ])

#Función Principal que llama a las funciones de las restricciones
def definir_modelo(franjas, m_fila, m_columna, talleres_std, talleres_spc, parkings, aviones):
    problema = Problem()

    # Crear variables para cada avión en cada franja horaria
    # Dominios: Cada avión puede ir a cualquier taller estándar o especialista

    # Creamos el dominio de variables
    talleres = talleres_std + talleres_spc + parkings
    for avion in aviones:
        for franja in range(franjas):
            problema.addVariable(f"A{avion['id']}_T{franja}", talleres)

    # Establecemos el dominio para cada tipo de avion
    for franja in range(franjas):
        problema.addConstraint(restriccion_talleres,
                              [f"A{avion['id']}_T{franja}" for avion in aviones])

    # Establecemos la posible distrubucion segun las tareas a realzar
    for franja in range(franjas):
        problema.addConstraint(
            lambda *posiciones, franja=franja: restriccion_tipos(posiciones, aviones, talleres_std,
                                                                 talleres_spc, parkings),
            [f"A{avion['id']}_T{franja}" for avion in aviones]
        )

    # Se encarga de imponer un orden en las tareas
    for avion in aviones:
        if avion['t1'] > 0 or avion['t2'] > 0:
            if avion['restr'] == True:
                problema.addConstraint(
                    lambda *asignaciones, avion=avion: restriccion_orden_tareas(avion, talleres_std,
                                                                                talleres_spc,
                                                                                parkings,
                                                                                *asignaciones),
                    [f"A{avion['id']}_T{t}" for t in range(franjas)]
                )
            else:
                for avion in aviones:
                    tareas = avion['t1'] + avion['t2']
                    variables = [f"A{avion['id']}_T{franja}" for franja in range(franjas)]

                    problema.addConstraint(
                        lambda *asignaciones, req=tareas: verificar_completitud(
                            asignaciones, req, talleres_std, talleres_spc
                        ),
                        variables
                    )

                    problema.addConstraint(
                        lambda *asignaciones, req=avion['t2']: verificar_tarea(
                            asignaciones, req, talleres_spc
                        ),
                        variables
                    )

    # Se encarga que al menos haya un hueco en horizontal o en vertical
    problema.addConstraint(
        lambda *asignaciones: restriccion_maniobrabilidad(m_fila, m_columna, *asignaciones),
        [f"A{avion['id']}_T{t}" for avion in aviones for t in range(franjas)]
    )

    # Se encarga de que garantizar que no haya JUMBOS en vertical y en horizontal cuando hay un
    # JUMBO en esa posicion
    problema.addConstraint(
        lambda *asignaciones: restriccion_no_jumbos_adyacentes(aviones, *asignaciones),
        [f"A{avion['id']}_T{t}" for avion in aviones for t in range(franjas)]
    )

    # Función que genera las soluciones
    soluciones = problema.getSolutions()
    return soluciones






if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Uso: python CSPMaintenance.py <archivo_entrada>")
        sys.exit(1)

    # Leer archivo de entrada
    ruta_archivo = sys.argv[1]
    franjas, m_filas, m_columnas, talleres_std, talleres_spc, parkings, aviones = leer_entrada(
        ruta_archivo)

    # Resolver el problema
    solution = definir_modelo(franjas, m_filas, m_columnas, talleres_std, talleres_spc,
                                parkings, aviones)

    output_file = ruta_archivo.replace(".txt", ".csv")
    # Guardar el resultado en un archivo de salida
    escribir_salida(output_file, solution, aviones, franjas, talleres_std, talleres_spc)

