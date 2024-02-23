import time

def epsilon(state, transitions):
    epsilon_closure_set = set(state)
    stack = list(state)

    while stack:
        current_state = stack.pop()
        epsilon_transitions = [
            t[2] for t in transitions if t[0] == current_state and t[1] == 120500
        ]
        for new_state in epsilon_transitions:
            if new_state not in epsilon_closure_set:
                epsilon_closure_set.add(new_state)
                stack.append(new_state)

    return epsilon_closure_set

def move(state, symbol, transitions):
    move_set = set()

    for t in transitions:
        if t[0] in state and t[1] == symbol:
            move_set.add(t[2])

    return move_set

def exec(alfabeto, transiciones, estado_inicial, estados_aceptacion, cadena):
    mensajeError = "La cadena NO cumple con el lenguaje\n"
    mensajeAprobacion = "La cadena SI cumple con el lenguaje\n"
    for element in estados_aceptacion:
        estados_aceptacion = element

    start_time = time.time()

    for cad in cadena:
        if cad not in alfabeto:
            end_time = time.time()
            print("Tiempo de ejecución: " + str(end_time - start_time))
            print(mensajeError)
            return mensajeError

    estado_actual = estado_inicial
    for cad in cadena:
        estado_actuales = epsilon(estado_actual, transiciones)
        estado_actual = move(estado_actuales, cad, transiciones)
    
    estado_actual = epsilon(estado_actual, transiciones)

    end_time = time.time()
    print("Tiempo de ejecución: " + str(end_time - start_time))
    
    if estados_aceptacion in estado_actual:
        print(mensajeAprobacion)
    else:
        print(mensajeError)
