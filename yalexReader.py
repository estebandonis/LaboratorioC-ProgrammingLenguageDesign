import shuntingyard as shun
import dfa_directly as dfa_dir
import dfa_minimization as dfa_min
import simuladorAFD as simAFD
import arbol as tree

def readYalexFile(file):
    with open(file, 'r') as file:
        data = file.read()
    return data


def ASCIITransformer(infix_regex):
    new_infix = []

    # \(\* (' '-'&''\+'-'}''á''é''í''ó''ú''ñ')* \*\)

    # let (a-z)* = ([(' '-'\''^'-'}')*]|(('\('-'Z''\'-'}')*))*

    # ( +('*'-'}')*)|( +'|' ('*'-'}')* +{ return ('A'-'Z')* })

    operadores = ['*', '+', '?', '|', '(', ')', '!']

    print(infix_regex)

    i = 0
    while i < len(infix_regex):
        char = infix_regex[i]
        if char in operadores:
            new_infix.append(char)
            i += 1
            continue

        elif char == '\\':
            next = infix_regex[i+1]
            if next == '\\' or next in operadores or next == '-' :
                new_infix.append(ord(next))
                i += 2
                continue
            elif next == 'n':
                new_infix.append(ord('\n'))
                i += 2
                continue
            elif next == 't':
                new_infix.append(ord('\t'))
                i += 2
                continue
            else:
                new_infix.append(ord(char))
                i += 1
                continue
        
        elif char == '-':
            first = new_infix.pop()
            second = infix_regex[i+1]
            if second == '\'':
                second = ord(infix_regex[i+2])
                i += 1
            else:
                second = ord(second)

            j = first
            for j in range(first, second + 1):
                if j == second:
                    new_infix.append(j)
                    break
                new_infix.append(j)
                new_infix.append('|')
                j += 1

            i += 2
            continue

        elif char == '\'':
            if i + 1 < len(infix_regex):
                next = infix_regex[i + 1]
                if next == '\'':
                    new_infix.append('|')
                    i += 2
                elif i + 2 < len(infix_regex):
                    next_next = infix_regex[i + 2]
                    if next != '-' and next_next == '\'':
                        new_infix.append(ord(next))
                        i += 2
                        continue
                    else:
                        i += 1
                        continue
                else:
                    i += 1
                    continue

            else:
                i += 1
                continue

        else:
            new_infix.append(ord(char))
            i += 1

    return new_infix

def getMachine(regex):
    ascii_regex = ASCIITransformer(regex)
    postfix_regex = shun.exec(ascii_regex)
    stack, node_list, alfabeto = tree.exec(postfix_regex)
    estadoscon, alfabetocon, Dtran, estado_inicialcon, estado_finalcon = dfa_dir.exec(stack, node_list, alfabeto)
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
    return new_states, new_transitions, newStart_states, newFinal_states


def main():

    Machines = {
        "Commentarios": "\(\* (' '-'&''\+'-'}''á''é''í''ó''ú''ñ')* \*\)",
        "Variables": "let (a-z)* = ([(' '-'\\''^'-'}')*]|(('\('-'Z''\\'-'}')*))*",
        "Reglas": "rule tokens =",
        "Tokens": "( +('*'-'}')*)|( +'|' ('&'-'}')* +{ return ('A'-'Z')* })",
    }

    ascii_comments = Machines['Commentarios']
    
    comments_states, comments_transitions, comments_inicial, comments_final = getMachine(ascii_comments)

    ascii_variables = Machines['Variables']

    variables_states, variables_transitions, variables_inicial, variables_final = getMachine(ascii_variables)

    ascii_rules = Machines['Reglas']

    rules_states, rules_transitions, rules_inicial, rules_final = getMachine(ascii_rules)

    ascii_tokens = Machines['Tokens']

    tokens_states, tokens_transitions, tokens_inicial, tokens_final = getMachine(ascii_tokens)

    data = readYalexFile('slr-1.yal')

    i = 0
    diccionario = {}
    values = {}
    tokens = []
    contador = 0
    length_data = len(data)
    while i < length_data:
        bol, num, valores = simAFD.exec(comments_transitions, comments_inicial, comments_final, data, i)
        if (bol):
            diccionario[contador] = valores
            contador += 1
            i = num
            continue

        bol, num, valores = simAFD.exec(variables_transitions, variables_inicial, variables_final, data, i)
        if (bol):
            diccionario[contador] = valores
            listValues = valores.split(' ', 3)
            values[listValues[1]] = listValues[3]
            contador += 1
            i = num
            continue
            
        
        bol, num, valores = simAFD.exec(rules_transitions, rules_inicial, rules_final, data, i)
        if (bol):
            diccionario[contador] = valores
            contador += 1
            i = num
            continue
    
        bol, num, valores = simAFD.exec(tokens_transitions, tokens_inicial, tokens_final, data, i)
        if (bol):
            diccionario[contador] = valores
            listValues = valores.split()
            print("listValues: ", listValues)
            if len(listValues) < 2 and listValues != []:
                tokens.append(listValues[0])
            elif listValues != []:
                tokens.append(listValues[0])
                tokens.append(listValues[1].replace('\'', ''))
            contador += 1
            i = num
            continue
    
        if (data[i] == ' ' or data[i] == '\n' or data[i] == '\t'):
            i += 1
            continue
    
        else:
            break
    
    print("Diccionario")
    for i in diccionario:
        print(i, ": ", diccionario[i])

    print("Values: ")
    for val in values:
        print(val, ": ", values[val])

    print("Tokens: ")
    print(tokens)

main()