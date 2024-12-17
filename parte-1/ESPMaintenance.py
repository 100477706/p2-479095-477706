from constraint import Problem

# def restriccion_talleres(*asignaciones):
#     conteo = {}
#     for avion, posicion in zip(aviones, asignaciones):
#         if avion['tipo'] == 'JMB':
#             if posicion in conteo:
#                 return False  # Un taller ya está ocupado por otro avión
#             else:
#                 conteo[posicion] = 2  # Un JUMBO ocupa
#         else:
#             conteo[posicion] = conteo.get(posicion, 0) + 1
#             if conteo[posicion] > 2:
#                 return False  # Más de dos aviones en un taller
#     return True

def restriccion_talleres(*asignaciones):
    conteo = {}
    jumbo_present = set()
    for posicion, avion in zip(asignaciones, aviones):
        if avion['tipo'] == 'JMB':
            if posicion in jumbo_present or conteo.get(posicion, 0) > 0:
                return False  # No más de un JUMBO por taller
            jumbo_present.add(posicion)
        else:
            conteo[posicion] = conteo.get(posicion, 0) + 1
            if conteo[posicion] > 2:
                return False  # No más de dos aviones estándar
    return True


# def restriccion_tipos(posiciones, aviones, talleres_std, talleres_spc, parkings):
#     conteo_talleres = {}  # Llevar un registro de talleres ocupados
#     conteo_parkings = {}  # Llevar un registro de parkings ocupados
#
#     for avion, posicion in zip(aviones, posiciones):
#         # Caso 1: Avión sin tareas pendientes (t1 == 0 y t2 == 0)
#         if avion['t1'] == 0 and avion['t2'] == 0:
#             if posicion not in parkings:
#                 return False  # Avión sin tareas debe ir a un parking
#
#         # Caso 2: Avión con tareas pendientes (t1 > 0 o t2 > 0)
#         else:
#             if posicion in talleres_spc and avion['t2'] >= 1:
#                 # Taller especializado compatible
#                 conteo_talleres[posicion] = conteo_talleres.get(posicion, 0) + 1
#                 if conteo_talleres[posicion] > 1:
#                     return False  # Un taller solo puede atender un avión especializado
#             elif posicion in talleres_std and avion['t1'] >= 1:
#                 # Taller estándar compatible
#                 conteo_talleres[posicion] = conteo_talleres.get(posicion, 0) + 1
#                 if conteo_talleres[posicion] > 2:
#                     return False  # Un taller estándar puede atender hasta 2 aviones
#             elif posicion in parkings:
#                 # Verificar que los talleres estén ocupados antes de permitir parking
#                 if any(count < 2 for pos, count in conteo_talleres.items() if pos in talleres_std) or \
#                    any(count < 1 for pos, count in conteo_talleres.items() if pos in talleres_spc):
#                     return False  # Hay talleres disponibles, no puede ir a un parking
#                 conteo_parkings[posicion] = conteo_parkings.get(posicion, 0) + 1
#                 if conteo_parkings[posicion] > 1:
#                     return False  # Un parking solo puede albergar un avión
#             else:
#                 return False  # Posición inválida
#
#         # Verificar exclusividad del taller o parking
#         if posicion in conteo_talleres or posicion in conteo_parkings:
#             if conteo_talleres.get(posicion, 0) > 2 or conteo_parkings.get(posicion, 0) > 1:
#                 return False
#
#     return True

def restriccion_orden_tareas(avion, talleres_std, talleres_spc, *asignaciones):
    t2 = avion['t2']  # Número de tareas tipo 2 pendientes
    t1 = avion['t1']  # Número de tareas tipo 1 pendientes

    for i, posicion in enumerate(asignaciones):
        # Mientras haya tareas de tipo 2 pendientes
        if t2 > 0:
            if posicion not in talleres_spc:
                print(f"Restricción violada: En franja {i}, tarea tipo 2 no está en taller especializado.")
                return False
            t2 -= 1  # Consumir una tarea de tipo 2

        # Cuando no queden tareas de tipo 2, pero sí de tipo 1
        elif t1 > 0:
            if posicion not in talleres_std:
                print(f"Restricción violada: En franja {i}, tarea tipo 1 no está en taller estándar.")
                return False
            t1 -= 1  # Consumir una tarea de tipo 1

        # Si no quedan tareas de ningún tipo, no hay restricciones en la franja
        else:
            if posicion not in parkings:
                print(f"Restricción violada: En franja {i}, no se asignó un parking.")
                return False

    return True

def restriccion_tipos(posiciones, aviones, talleres_std, talleres_spc, parkings):
    conteo_talleres = {}  # Lleva el registro de aviones en talleres
    jumbo_present = set()  # Lleva el registro de talleres con aviones JUMBO
    conteo_parkings = {}  # Lleva el registro de aviones en parkings

    for avion, posicion in zip(aviones, posiciones):
        # Caso 1: Avión sin tareas pendientes debe ir a un parking
        if avion['t1'] == 0 and avion['t2'] == 0:
            if posicion not in parkings:
                return False  # Avión sin tareas debe ir a un parking
            if avion['tipo'] == 'JMB':
                if posicion in jumbo_present:
                    return False  # No puede haber más de un JUMBO en un taller
                jumbo_present.add(posicion)
            conteo_parkings[posicion] = conteo_parkings.get(posicion, 0) + 1
            if conteo_parkings[posicion] > 2:
                return False  # Un parking solo puede albergar dos aviones

        # Caso 2: Avión con tareas pendientes
        else:
            if posicion in talleres_spc and avion['t2'] >= 1:  # Taller especializado
                if avion['tipo'] == 'JMB':
                    if posicion in jumbo_present:
                        return False  # No puede haber más de un JUMBO en un taller
                    jumbo_present.add(posicion)
                conteo_talleres[posicion] = conteo_talleres.get(posicion, 0) + 1
                if conteo_talleres[posicion] > 2:
                    return False  # Un taller especializado puede atender solo un avión

            elif posicion in talleres_std and avion['t1'] >= 1:  # Taller estándar
                if avion['tipo'] == 'JMB':
                    if posicion in jumbo_present:
                        return False  # No puede haber más de un JUMBO en el taller
                    jumbo_present.add(posicion)
                conteo_talleres[posicion] = conteo_talleres.get(posicion, 0) + 1
                if conteo_talleres[posicion] > 2:
                    return False  # Un taller estándar puede atender hasta 2 aviones

            elif posicion in parkings:
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

            else:
                return False  # Posición inválida (ni taller ni parking)

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

    talleres = talleres_std + talleres_spc + parkings
    for avion in aviones:
        for franja in range(franjas):
            problema.addVariable(f"A{avion['id']}_T{franja}", talleres)

    # ubicaciones = talleres_std + talleres_spc + parkings
    # for avion in aviones:
    #     problema.addVariable(f"A{avion['id']}", ubicaciones)

    for franja in range(franjas):
        problema.addConstraint(restriccion_talleres,
                              [f"A{avion['id']}_T{franja}" for avion in aviones])

    for franja in range(franjas):
        problema.addConstraint(
            lambda *posiciones, franja=franja: restriccion_tipos(posiciones, aviones, talleres_std,
                                                                 talleres_spc, parkings),
            [f"A{avion['id']}_T{franja}" for avion in aviones]
        )

    for avion in aviones:
        if avion['t1'] > 0 or avion['t2'] > 0:
            if avion['restr'] == True:
                problema.addConstraint(
                    lambda *asignaciones, avion=avion: restriccion_orden_tareas(avion, talleres_std,
                                                                                talleres_spc,
                                                                                *asignaciones),
                    [f"A{avion['id']}_T{t}" for t in range(franjas)]
                )

    problema.addConstraint(
        restriccion_maniobrabilidad,
        [f"A{avion['id']}_T{t}" for avion in aviones for t in range(franjas)]
    )

    problema.addConstraint(
        lambda *asignaciones: restriccion_no_jumbos_adyacentes(aviones, *asignaciones),
        [f"A{avion['id']}_T{t}" for avion in aviones for t in range(franjas)]
    )

    # problema.addConstraint(
    #     lambda *posiciones: restriccion_tipos(posiciones, aviones, talleres_std, talleres_spc,
    #                                           parkings),
    #     [f"A{avion['id']}" for avion in aviones]
    # )
    # problema.addConstraint(restriccion_maniobrabilidad)
    # problema.addConstraint(
    #     lambda *asignaciones: restriccion_no_jumbos_adyacentes(aviones, *asignaciones),
    #     [f"A{avion['id']}" for avion in aviones]
    # )

    # Forzar que el avión 2 esté en la posición (2, 1) en la franja 0
    problema.addConstraint(lambda posicion: posicion == (2, 3), (f"A2_T0",))
    problema.addConstraint(lambda posicion: posicion == (2, 1), (f"A3_T0",))
    problema.addConstraint(lambda posicion: posicion == (3, 0), (f"A4_T0",))
    problema.addConstraint(lambda posicion: posicion == (3, 3), (f"A5_T0",))
    problema.addConstraint(lambda posicion: posicion == (0, 3), (f"A6_T0",))


    soluciones = problema.getSolutions()
    # Imprimir las soluciones en consola
    print(f"N. Soluciones: {len(soluciones)}")
    for i, solucion in enumerate(soluciones):
        print(f"Solución {i + 1}:")
        for avion in aviones:
            for franja in range(franjas):
                asignacion = solucion[f"A{avion['id']}_T{franja}"]
                print(f"Avión {avion['id']} - Franja {franja}: {asignacion}")


if __name__ == "__main__":

    # Definición directa de las variables
    franjas = 1
    m_filas = 5
    m_columnas = 5
    talleres_std = [(0, 2), (0, 4), (1, 1), (1, 2), (1, 3), (2, 0), (2, 2), (4, 1), (4, 2)]
    talleres_spc = [(0, 3), (2, 1), (2, 3), (3, 0), (3, 3)]
    parkings = [(0, 0), (0, 1), (1, 0), (1, 4), (2, 4), (3, 1), (3, 2), (3, 4), (4, 0), (4, 4)]
    aviones = [
        {'id': 1, 'tipo': 'JMB', 'restr': True, 't1': 1, 't2': 1},
        {'id': 2, 'tipo': 'JMB', 'restr': True, 't1': 0, 't2': 1},
        {'id': 3, 'tipo': 'JMB', 'restr': True, 't1': 0, 't2': 1},
        {'id': 4, 'tipo': 'JMB', 'restr': True, 't1': 0, 't2': 1},
        {'id': 5, 'tipo': 'JMB', 'restr': True, 't1': 0, 't2': 1},
        {'id': 6, 'tipo': 'JMB', 'restr': True, 't1': 0, 't2': 1}

    ]

    # Llamado a la función
    definir_modelo(franjas, m_filas, m_columnas, talleres_std, talleres_spc, parkings, aviones)