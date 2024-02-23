import shuntingyard as shun
import thompson as thom
import nfa_to_dfa as dfa
import dfa_minimization as dfa_min
import arbol as tree
import dfa_directly as dfa_dir
import simuladorAFD as simAFD
import simuladorAFN as simAFN
import pydotplus as pdp

# Función para verificar si una expresión regular es válida
def is_valid_regex(regex):
    # Verificar balanceo de paréntesis
    if regex.count('(') != regex.count(')'):
        print("Error: Faltan paréntesis en la expresión regular")
        return False

    # Verificar si hay algo dentro de los paréntesis
    if '()' in regex:
        print("Error: Paréntesis vacíos")
        return False

    # Verificar errores en el operador |
    if '|' in regex:
        for i in range(len(regex)):
            if regex[i] == '|':
                if i == 0 or i == len(regex) - 1:
                    print("Error: El operador | no puede estar al principio o al final de la expresión")
                    return False
                if regex[i+1] in '|*+?)':
                    print("Error: No puede haber un operador después de |")
                    return False
                if regex[i-1] in '(|':
                    print("Error: Tiene que haber operandos antes de |")
                    return False
                
    if '*' in regex or '+' in regex or '?' in regex:
        for i in range(len(regex)):
            if regex[i] in '*+?':
                if i == 0:
                    print("Error: Los operadores */+/? no pueden estar al principio de la expresión")
                    return False
                if regex[i-1] in '(*+?':
                    print("Error: No puede haber un operador (incluyendo '(') antes de los operadores */+/?")
                    return False
    
    if ' ' in regex:
        print("Error: No puede haber espacios en la expresión regular")
        return False
        
    return True

# Función donde se ejecutan todos los algoritmos
def main():
    cadena_ingresada = False
    while True:
        print("\nMenú de opciones: ")
        print("1. Ingresar expresión regular")
        print("2. Ingresar cadena")
        print("3. Salir\n")

        if cadena_ingresada:
            print("Expresión regular ingresada: " + infix_regex, "\n")

        option = input("Ingrese la opción: ")
        if option == "3":
            break
        if option == "1":
            while True:
                # Expresión regular en notación infija
                infix_regex = input("\nIngrese la expresión regular en notación infija: ")
            
                if is_valid_regex(infix_regex):
                    cadena_ingresada = True
                    print('\nCadena ingresada')
                    break
            continue

        if option == "2" and cadena_ingresada:
            # Cadena a evaluar
            cadena = input("\nIngrese la cadena a evaluar: ")
        else:
            print("\nError: No ha ingresado una opción válida o no ha ingresado la expresión regular")
            continue

        new_infix = []

        for char in infix_regex:
            new_infix.append(ord(char))

        print("Expresión regular en ASCII: ", new_infix)

        # Convertimos la expresión regular a notación postfija
        postfix_regex = shun.exec(new_infix)

        new_cadena = []
        for char in cadena:
            new_cadena.append(ord(char))
        
        old_infix = []

        for char in postfix_regex:
            old_infix.append(chr(char))
        print("Cadena convertida a postfix: ", old_infix)
        print()

        # Convertimos la expresión a un AFN
        afn = thom.exec(postfix_regex)

        estados = afn[0]
        alfabeto = afn[1]
        transiciones = afn[2]
        estado_inicial = {afn[3]}
        estados_aceptacion = {afn[4][0]}

        print("\nSimulador AFN: ")
        simAFN.exec(alfabeto, transiciones, estado_inicial, estados_aceptacion, new_cadena)

        # Convertimos el AFN a un AFD
        afd = dfa.exec(estados, alfabeto, estado_inicial, estados_aceptacion, transiciones)

        estadosTempo = afd[0]
        alfabetoTempo = afd[1]
        transicionesTempo = afd[2]
        estado_inicialTempo = afd[3]
        estado_inicialAFD = {str(estado_inicialTempo)}
        estados_aceptacionTempo = afd[4]

        print("\nSimulador AFD (Subconjuntos): ")
        simAFD.exec(alfabetoTempo, transicionesTempo, estado_inicialTempo, estados_aceptacionTempo, new_cadena)

        estadosAFD = set()
        for i in estadosTempo:
            estadosAFD.add(str(i))

        alfabetoAFD = set()
        for i in alfabetoTempo:
            alfabetoAFD.add(str(i))

        transicionesAFD = set()
        for tran in transicionesTempo:
            trans = ()
            for t in tran:
                trans = trans + (str(t),)
            transicionesAFD.add(trans)

        estados_aceptacionAFD = set()
        for i in estados_aceptacionTempo:
            estados_aceptacionAFD.add(str(i))

        new_states, symbols, new_transitions, newStart_states, newFinal_states = dfa_min.exec(estadosAFD, alfabetoAFD, transicionesAFD, estado_inicialAFD, estados_aceptacionAFD, "pngs/dfa_graph_minimized_subconjuntos.png")

        print("\nSimulador AFD (Minimizacion de Subconjuntos): ")
        simAFD.exec(symbols, new_transitions, newStart_states, newFinal_states, new_cadena)
        
        stack, node_list, alfabeto = tree.exec(postfix_regex)
        estadoscon, alfabetocon, Dtran, estado_inicialcon, estado_finalcon = dfa_dir.exec(stack, node_list, alfabeto)

        print("\nSimulador AFD (Conversión Directa): ")
        simAFD.exec(alfabetocon, Dtran, estado_inicialcon, estado_finalcon, new_cadena)

        estadosAFD = set()
        for i in estadoscon:
            estadosAFD.add(str(i))

        alfabetoAFD = set()
        for i in alfabetocon:
            alfabetoAFD.add(str(i))

        transicionesAFD = set()
        for tran in Dtran:
            trans = ()
            for t in tran:
                trans = trans + (str(t),)
            transicionesAFD.add(trans)

        estado_inicialAFD = {str(estado_inicialcon)}

        estados_aceptacionAFD = set()
        for i in estado_finalcon:
            estados_aceptacionAFD.add(str(i))

        new_states, symbols, new_transitions, newStart_states, newFinal_states = dfa_min.exec(estadosAFD, alfabetoAFD, transicionesAFD, estado_inicialAFD, estados_aceptacionAFD, "pngs/dfa_graph_minimized_conversion.png")

        print("\nSimulador AFD (Minimizacion de Conversion Directa): ")
        simAFD.exec(symbols, new_transitions, newStart_states, newFinal_states, new_cadena)

main()
