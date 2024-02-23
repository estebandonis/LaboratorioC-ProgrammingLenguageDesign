import time

def exec(alfabeto, transiciones, estado_inicial, estados_aceptacion, cadena):

    mensajeError = "La cadena NO cumple con el lenguaje\n"
    mensajeAprobacion = "La cadena SI cumple con el lenguaje\n"

    start_time = time.time()

    for cad in cadena:
        if cad not in alfabeto:
            end_time = time.time()
            print("Tiempo de ejecución: " + str(end_time - start_time))
            print(mensajeError)
            return mensajeError

    error = False
    estado_actual = estado_inicial
    if len(cadena) != 0:
        for cad in cadena:
            pasa = False
            for tran in transiciones:
                if estado_actual == tran[0] and cad == tran[1]:
                    estado_actual = tran[2]
                    pasa = True
                    break
            if pasa == False:
                error = True
                break
            
    end_time = time.time()
    print("Tiempo de ejecución: " + str(end_time - start_time))

    if estado_actual in estados_aceptacion and error == False:
        print(mensajeAprobacion)
    else:
        print(mensajeError)