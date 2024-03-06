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

    # let (a-z)* = *([^=]|['[]*|?.]|' ')+"],

    # ([^])*]|((^( \n))*)+

    # Antes: ( +('*'-'}')*)|( +'|' ('*'-'}')* +{ return ('A'-'Z')* })

    #  +('|' )?('('-'}')+( +{ return ('A'-'Z')+ })?

    # ["| ([a-zl'[al')+ +\{ *return *[A-Z]+ *\}."]

    """
    Machines = {
        "Commentarios": "\(\* (' '-'&''\+'-'}''á''é''í''ó''ú''ñ')* \*\)",
        "Declaration": "let (a-z)* =",
        "Variables": "([(^])*]|^( \n)*)+",
        "Reglas": "rule tokens =",
        "Tokens1": "('&'-'}')+ *{ return ('A'-'Z')* }",
        "Tokens2": "\| ('&'-'}')+ *{ return ('A'-'Z')* }",
        "Tokens3": "('a'-'z')+",
    }
    """

    operadores = ['*', '+', '?', '|', '(', ')', '!']

    Universo = 255

    i = 0
    while i < len(infix_regex):
        char = infix_regex[i]
        if char in operadores:
            new_infix.append(char)
            i += 1
            continue

        elif char == '\\':
            next = infix_regex[i+1]
            if next == '\\' or next in operadores or next == '-' or next == '^':
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
        
        elif char == '^':
            next = infix_regex[i+1]
            if next == '(':
                temp = []
                j = i + 2
                while j < len(infix_regex) and infix_regex[j] != ')':
                    temp.append(infix_regex[j])
                    j += 1
                i = j

                new_temp = []
                a = 0
                while a < len(temp):
                    t = temp[a]
                    if t == '\\':
                        if temp[a+1] == 'n' or temp[a+1] == 't':
                            t = '\n'
                            a += 1
                        elif temp[a+1] == 't':
                            t = '\t'
                            a += 1
                        else:
                            t = temp[a+1]
                            a += 1
                    new_temp.append(ord(t))
                    a += 1 

                j = 0
                for j in range(0, Universo + 1):
                    if j == Universo and j not in new_temp:
                        new_infix.append(j)
                        break
                    if j not in new_temp:
                        new_infix.append(j)
                        new_infix.append('|')
                    j += 1
            else:
                next_ascii = ord(next)
                j = 0
                for j in range(0, Universo + 1):
                    if j == Universo and j != next_ascii:
                        new_infix.append(j)
                        break
                    if j != next_ascii:
                        new_infix.append(j)
                        new_infix.append('|')
                    j += 1

            i += 2
            
        else:
            new_infix.append(ord(char))
            i += 1

    print(new_infix)

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

    operadores = ['*', '+', '?', '|', '(', ')', '!']
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

    Machines = {
        "Commentarios": "\(\* (' '-'&''\+'-'}''á''é''í''ó''ú''ñ')* \*\)",
        "Declaration": "let (a-z)* =",
        "Variables": "([(^])*]|^( \n)*)+",
        "Reglas": "rule tokens =",
        "Tokens1": "('&'-'}')+",
        "Tokens2": "\| *('&'-'}')*",
        "Returns": "{ return ('A'-'Z')* }",
    }

    ascii_comments = Machines['Commentarios']
    print("Generando AFD para comentarios")    
    comments_states, comments_transitions, comments_inicial, comments_final = getMachine(ascii_comments)
    print("AFD para comentarios generado")

    ascii_declaration = Machines['Declaration']
    print("Generando AFD para declaration")
    declaration_states, declaration_transitions, declaration_inicial, declaration_final = getMachine(ascii_declaration)
    print("AFD para declaration generado")

    ascii_variables = Machines['Variables']
    print("Generando AFD para variables")
    variables_states, variables_transitions, variables_inicial, variables_final = getMachine(ascii_variables)
    print("AFD para variables generado")

    ascii_rules = Machines['Reglas']
    print("Generando AFD para reglas")
    rules_states, rules_transitions, rules_inicial, rules_final = getMachine(ascii_rules)
    print("AFD para reglas generado")

    ascii_tokens1 = Machines['Tokens1']
    print("Generando AFD para tokens1")
    tokens1_states, tokens1_transitions, tokens1_inicial, tokens1_final = getMachine(ascii_tokens1)
    print("AFD para tokens1 generado")

    ascii_tokens2 = Machines['Tokens2']
    print("Generando AFD para tokens2")
    tokens2_states, tokens2_transitions, tokens2_inicial, tokens2_final = getMachine(ascii_tokens2)
    print("AFD para tokens2 generado")

    ascii_returns = Machines['Returns']
    print("Generando AFD para returns")
    returns_states, returns_transitions, returns_inicial, returns_final = getMachine(ascii_returns)
    print("AFD para returns generado")

    data = readYalexFile('slr-1.yal')

    i = 0
    diccionario = {}
    variables = []
    values = {}
    tokens = []
    temp_tokens = []
    tokens_dictionary = {}
    contador = 0
    length_data = len(data)
    read_tokens = False
    while i < length_data:
        bol, num, valores = simAFD.exec(comments_transitions, comments_inicial, comments_final, data, i)
        if bol:
            print("Comentario: " + valores)
            diccionario[contador] = valores
            contador += 1
            i = num
            continue

        bol, num, valores = simAFD.exec(rules_transitions, rules_inicial, rules_final, data, i)
        if bol:
            print("Rules: " + valores)
            diccionario[contador] = valores
            contador += 1
            read_tokens = True
            i = num
            continue
        
        if read_tokens == False:
            bol, num, valores = simAFD.exec(declaration_transitions, declaration_inicial, declaration_final, data, i)
            if bol:
                print("Declaration: " + valores)
                diccionario[contador] = valores
                listValues = valores.split()
                variables.append(listValues[1])
                contador += 1
                i = num
                continue

            bol, num, valores = simAFD.exec(variables_transitions, variables_inicial, variables_final, data, i)
            if bol:
                print("Variables: " + valores)
                diccionario[contador] = valores
                values[variables.pop()] = valores
                temp_tokens.append(valores)
                contador += 1
                i = num
                continue
    
        if read_tokens:
            bol, num, valores = simAFD.exec(returns_transitions, returns_inicial, returns_final, data, i)
            if bol:
                print("Returns: " + valores)
                diccionario[contador] = valores
                tokens_dictionary[temp_tokens.pop()] = valores
                contador += 1
                i = num
                continue

            bol, num, valores = simAFD.exec(tokens2_transitions, tokens2_inicial, tokens2_final, data, i)
            if bol:
                print("Tokens2: " + valores)
                diccionario[contador] = valores
                listValues = valores.split()
                tokens.append(listValues[0])
                tokens.append(listValues[1])
                temp_tokens.append(listValues[1])
                contador += 1
                i = num
                continue

            bol, num, valores = simAFD.exec(tokens1_transitions, tokens1_inicial, tokens1_final, data, i)
            if bol:
                print("Tokens1: " + valores)
                diccionario[contador] = valores
                tokens.append(valores)
                temp_tokens.append(valores)
                contador += 1
                i = num
                continue
    
        if data[i] == ' ' or data[i] == '\n' or data[i] == '\t':
            i += 1
            continue
    
        else:
            print("Error lexico en la linea: ", data[i])
            break
    
    print("Diccionario")
    for i in diccionario:
        print(i, ": ", diccionario[i])

    # num = 0
    # while num < len(tokens):
    #     ton = tokens[num]
    #     print(ton)
    #     print('\'' in ton)
    #     if '\'' in ton:
    #         ton = ord(ton.replace('\'', ''))
    #         tokens[num] = ton
    #     num += 1
        
    # for i in tokens_dictionary:
    #     print(i, ": ", tokens_dictionary[i])

    # for val in values:
    #     value = values[val]

    #     start = value.find('[')
    #     end = value.find(']')

    #     ASCIIList = ASCIITransformer(value[start+1:end])
    #     replacement = ''.join(str(i) for i in ASCIIList)

    #     if start != -1 and end != -1:
    #         new_string = value[:start] + '(' + replacement + ')' + value[end+1:]
    #         values[val] = new_string

    print("Values: ")
    for val in values:
        print(val, ": ", values[val])
    print()

    for val in values:
        valor = values[val]
        for valo in values:
            first = valor.find(valo)
            last = 0
            if first != -1:
                last = first + len(valo)

            if first != -1:
                new_string = valor[:first] + values[valo] + valor[last:]
                valor = new_string
                values[val] = new_string

            while first != -1:
                first = valor.find(valo)
                if first != -1:
                    last = first + len(valo)

                if first != -1:
                    new_string = valor[:first] + values[valo] + valor[last:]
                    valor = new_string
                    values[val] = new_string


    print()
    print("Values Final: ")
    for lal in values:
        print(lal, ": ", values[lal])

    i = 0
    while i < len(tokens):
        if tokens[i] in values:
            tokens[i] = values[tokens[i]]
        i += 1

    print()
    print("Tokens Final: ")
    print(tokens)

    super_string = ''.join(str(i) for i in tokens)

    print("Super String: ")
    print(super_string)

    ascii_super = ASCIITransformer(super_string)

    super_postfix = shun.exec(ascii_super)
    print(super_postfix)
    stack, node_list, alfabeto = tree.exec(super_postfix, True)


    # print("Tokens: ", new_tokens)

main()