from constraint import Problem

def restriccion_talleres(*asignaciones):
    conteo = {}
    for avion, posicion in zip(aviones, asignaciones):
        if avion['tipo'] == 'JMB':
            if posicion in conteo:
                return False  # Un taller ya está ocupado por otro avión
            else:
                conteo[posicion] = 2  # Un JUMBO ocupa
        else:
            conteo[posicion] = conteo.get(posicion, 0) + 1
            if conteo[posicion] > 2:
                return False  # Más de dos aviones en un taller
    return True


def restriccion_tipos_original(posiciones, aviones, talleres_std, talleres_spc, parkings):
    conteo = {}   # Llevar un registro de talleres ocupados

    for avion, posicion in zip(aviones, posiciones):
        # Verificar compatibilidad del avión con el taller
        if avion['t1'] == 0 and avion['t2'] == 0:
            if posicion not in parkings:
                return False

        else:
            if posicion in talleres_spc and avion['t2'] < 1:
                return False  # Avión no puede usar taller especializado
            elif posicion in talleres_std and avion['t1'] < 1:
                return False  # Avión no puede usar taller estándar
            elif posicion in parkings and (avion['t2'] >= 1 or avion['t1'] >= 1):
                return False # Avión no puede estar en un parking si tiene tareas por hacer

        # Verificar exclusividad del taller
        if posicion in conteo:
            return False  # Taller ya ocupado por otro avión
        conteo[posicion] = True

    return True


def restriccion_tipos(posiciones, aviones, talleres_std, talleres_spc, parkings):
    conteo_talleres = {}  # Llevar un registro de talleres ocupados
    conteo_parkings = {}  # Llevar un registro de parkings ocupados

    for avion, posicion in zip(aviones, posiciones):
        # Caso 1: Avión sin tareas pendientes (t1 == 0 y t2 == 0)
        if avion['t1'] == 0 and avion['t2'] == 0:
            if posicion not in parkings:
                return False  # Avión sin tareas debe ir a un parking

        # Caso 2: Avión con tareas pendientes (t1 > 0 o t2 > 0)
        else:
            if posicion in talleres_spc and avion['t2'] >= 1:
                # Taller especializado compatible
                conteo_talleres[posicion] = conteo_talleres.get(posicion, 0) + 1
                if conteo_talleres[posicion] > 1:
                    return False  # Un taller solo puede atender un avión especializado
            elif posicion in talleres_std and avion['t1'] >= 1:
                # Taller estándar compatible
                conteo_talleres[posicion] = conteo_talleres.get(posicion, 0) + 1
                if conteo_talleres[posicion] > 2:
                    return False  # Un taller estándar puede atender hasta 2 aviones
            elif posicion in parkings:
                # Verificar que los talleres estén ocupados antes de permitir parking
                if any(count < 2 for pos, count in conteo_talleres.items() if pos in talleres_std) or \
                   any(count < 1 for pos, count in conteo_talleres.items() if pos in talleres_spc):
                    return False  # Hay talleres disponibles, no puede ir a un parking
                conteo_parkings[posicion] = conteo_parkings.get(posicion, 0) + 1
                if conteo_parkings[posicion] > 1:
                    return False  # Un parking solo puede albergar un avión
            else:
                return False  # Posición inválida

        # Verificar exclusividad del taller o parking
        if posicion in conteo_talleres or posicion in conteo_parkings:
            if conteo_talleres.get(posicion, 0) > 2 or conteo_parkings.get(posicion, 0) > 1:
                return False

    return True

def restriccion_maniobrabilidad(*asignaciones):
    ocupados = set(asignaciones)
    print(f"Posiciones ocupadas: {ocupados}")
    for posicion in ocupados:
        x, y = posicion
        adyacentes = [
            (x - 1, y), (x + 1, y),  # Vertical
            (x, y - 1), (x, y + 1)  # Horizontal
        ]
        adyacentes_validos = [adj for adj in adyacentes if adj[0] >= 0 and adj[1] >= 0]

        print(f"Revisando posición {posicion}, adyacentes válidos: {adyacentes_validos}")

        # Verificar si al menos uno de los adyacentes está vacío
        if not any(adj not in ocupados for adj in adyacentes_validos):
            print(f"Restricción violada en posición: {posicion}")
            return False  # No hay adyacente vacío

    return True

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
            print(
                f"Restricción violada: Talleres adyacentes ocupados por JUMBOS: {posicion} y {adyacentes_jumbos}")
            return False

    return True



def definir_modelo(franjas, m_fila, m_columna, talleres_std, talleres_spc, parkings, aviones):
    problema = Problem()

    # Crear variables para cada avión en cada franja horaria

    # Dominios: Cada avión puede ir a cualquier taller estándar o especialista
    ubicaciones = talleres_std + talleres_spc + parkings
    for avion in aviones:
        problema.addVariable(f"A{avion['id']}", ubicaciones)

    problema.addConstraint(restriccion_talleres, [f"A{avion['id']}" for avion in aviones])
    problema.addConstraint(
        lambda *posiciones: restriccion_tipos(posiciones, aviones, talleres_std, talleres_spc,
                                              parkings),
        [f"A{avion['id']}" for avion in aviones]
    )
    problema.addConstraint(restriccion_maniobrabilidad)
    problema.addConstraint(
        lambda *asignaciones: restriccion_no_jumbos_adyacentes(aviones, *asignaciones),
        [f"A{avion['id']}" for avion in aviones]
    )

    problema.addConstraint(lambda posicion: posicion == (2, 1), ("A2",))
    problema.addConstraint(lambda posicion: posicion == (2, 3), ("A3",))
    problema.addConstraint(lambda posicion: posicion == (3, 0), ("A4",))
    problema.addConstraint(lambda posicion: posicion == (3, 3), ("A5",))
    problema.addConstraint(lambda posicion: posicion == (0, 3), ("A6",))


    soluciones = problema.getSolutions()
    # Imprimir las soluciones en consola
    print(f"N. Soluciones: {len(soluciones)}")
    for i, solucion in enumerate(soluciones):
        print(f"Solución {i + 1}:")
        for avion in aviones:
            asignacion = solucion[f"A{avion['id']}"]
            print(f"Avión {avion['id']}: {asignacion}")

if __name__ == "__main__":

    # Definición directa de las variables
    franjas = 4
    m_filas = 5
    m_columnas = 5
    talleres_std = [(0, 2), (0, 4), (1, 1), (1, 2), (1, 3), (2, 0), (2, 2), (4, 1), (4, 2)]
    talleres_spc = [(0, 3), (2, 1), (2, 3), (3, 0), (3, 3)]
    parkings = [(0, 0), (0, 1), (1, 0), (1, 4), (2, 4), (3, 1), (3, 2), (3, 4), (4, 0), (4, 4)]
    aviones = [
        {'id': 1, 'tipo': 'JMB', 'restr': True, 't1': 0, 't2': 1},
        {'id': 2, 'tipo': 'JMB', 'restr': True, 't1': 0, 't2': 1},
        {'id': 3, 'tipo': 'JMB', 'restr': True, 't1': 0, 't2': 1},
        {'id': 4, 'tipo': 'STD', 'restr': True, 't1': 0, 't2': 1},
        {'id': 5, 'tipo': 'STD', 'restr': True, 't1': 0, 't2': 1},
        {'id': 6, 'tipo': 'STD', 'restr': True, 't1': 0, 't2': 1}

    ]

    # Llamado a la función
    definir_modelo(franjas, m_filas, m_columnas, talleres_std, talleres_spc, parkings, aviones)