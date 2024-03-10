import sys

import shuntingyard as shun
import dfa_directly as dfa_dir
import dfa_minimization as dfa_min
import simuladorAFD as simAFD
import arbol as tree

def readYalexFile(file):
    with open(file, 'r') as file:
        data = file.read()
    return data


def ASCIITransformer(infix_regex, check_operators = False):
    new_infix = []

    def handle_slash (infix_regex, i, new_infix):

        next = infix_regex[i+1]

        if next == 'n':
            new_infix.append(ord('\n'))
            i += 2
        elif next == 't':
            new_infix.append(ord('\t'))
            i += 2
        elif next == 's':
            new_infix.append(ord(' '))
            i += 2
        elif next == '\\':
            new_infix.append(ord('\\'))
            i += 2
        elif next == '\"':
            new_infix.append(ord('\"'))
            i += 2
        elif next == '\'':
            new_infix.append(ord('\''))
            i += 2
        else:
            print("Error léxico, operador no reconocido despues de slash: ", next)
            sys.exit()

        return infix_regex, i, new_infix
    

    def handle_comilla (infix_regex, i, new_infix):
        if i + 2 < len(infix_regex):
            next = infix_regex[i + 1]
            if i - 1 >= 0 and infix_regex[i - 1] == '\'' and infix_regex[i] == '\'' and next == '\'':
                print("Error léxico, no se puede tener dos comillas simples seguidas")
                sys.exit()
            elif next == '\'':
                new_infix.append('|')
                i += 1
            elif next == '\\':
                i += 1
                infix_regex, i, new_infix = handle_slash(infix_regex, i, new_infix)
            elif infix_regex[i + 2] == '\'':
                new_infix.append(ord(next))
                i += 3
                if i < len(infix_regex):
                    if infix_regex[i] == '\'' or infix_regex[i] == '\"':
                        new_infix.append('|')
            else:
                i += 1

        else:
            i += 1

        return infix_regex, i, new_infix
    

    def handle_double_comilla (infix_regex, i, new_infix):
        temp_regex = []
        j = i + 1

        if infix_regex[j] == '\"':
            print("Error léxico, no se puede tener dos comillas dobles seguidas")
            sys.exit()

        while j < len(infix_regex) and infix_regex[j] != '\"':
            temp_regex.append(infix_regex[j])
            j += 1

        h = 0
        while h < len(temp_regex):
            if temp_regex[h] == '\\':
                infix_regex, h, new_infix = handle_slash(temp_regex, h, new_infix)
                continue
            else:
                new_infix.append(ord(temp_regex[h]))
                h += 1
            
        if j + 1 < len(infix_regex) and (infix_regex[j + 1] == '\'' or infix_regex[j + 1] == '\"'):
            new_infix.append('|')

        i = j + 1

        return infix_regex, j + 1, new_infix
    
    def handle_double_comilla_brackets (infix_regex, i, new_infix):
        temp_regex = []

        if infix_regex[i + 1] == '\"':
            print("Error léxico, no se puede tener dos comillas seguidas")
            sys.exit()

        j = i + 1

        while j < len(infix_regex) and infix_regex[j] != '\"':
            temp_regex.append(infix_regex[j])
            j += 1

        h = 0
        while h < len(temp_regex):
            if temp_regex[h] == '\\':
                infix_regex, h, new_infix = handle_slash(temp_regex, h, new_infix)
                continue
            else:
                new_infix.append(ord(temp_regex[h]))
                h += 1
                
            if h < (len(temp_regex)):
                new_infix.append('|')

        i = j + 1

        return infix_regex, j + 1, new_infix
    

    def handle_brackets (infix_regex, i, new_infix):
        temp_regex = []
        new_infix.append('(')
        j = i + 1

        while j < len(infix_regex) and infix_regex[j] != ']':
            if infix_regex[j] == '[':
                print("Error léxico, no se puede no se cerro el corchete")
                sys.exit()
            temp_regex.append(infix_regex[j])
            j += 1

        l = 0
        while l < len(temp_regex):
            char = temp_regex[l]
            if char == '-':
                first = new_infix.pop()
                second = temp_regex[l+1]
                if second == '\'':
                    second = ord(temp_regex[l+2])
                    l += 1
                else:
                    second = ord(second)

                p = first
                for p in range(first, second + 1):
                    if p == second:
                        new_infix.append(p)
                        break
                    new_infix.append(p)
                    new_infix.append('|')
                    p += 1

                l += 2
                continue

            elif char == '\'':
                temp_regex, l, new_infix = handle_comilla(temp_regex, l, new_infix)
                continue

            elif char == '\\':
                temp_regex, l, new_infix = handle_slash(temp_regex, l, new_infix)
                continue

            elif char == '^':
                temp_regex, l, new_infix = handle_negate(temp_regex, l, new_infix)
                continue

            elif char == '\"':
                temp_regex, l, new_infix = handle_double_comilla_brackets(temp_regex, l, new_infix)
                continue
            else: 
                new_infix.append(ord(char))
                l += 1
        
        i = j + 1
        new_infix.append(')')
        return infix_regex, i, new_infix
    
    
    def handle_negate (infix_regex, i, new_infix):
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
                    temp, a, new_infix = handle_slash(temp, a, new_infix)
                    continue
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
                
        elif next == '[':
            Set = []
            infix_regex, i, Set = handle_brackets(infix_regex, i, Set)

            Set = set(Set)

            Set.discard(')')
            Set.discard('(')
            Set.discard('|')

            j = 0
            for j in range(0, Universo + 1):
                if j == Universo and j not in Set:
                    new_infix.append(j)
                    break
                if j not in Set:
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

        return infix_regex, i, new_infix
    

    def char_universe (infix_regex, i, new_infix):
        p = 0
        for p in range(0, Universo + 1):
            if p == Universo:
                new_infix.append(p)
                break
            new_infix.append(p)
            new_infix.append('|')
            p += 1

        i += 1

        return infix_regex, i, new_infix
    

    def char_arroba (infix_regex, i, new_infix):
        i += 1

        first_set = set()
        new_infix.pop()
        value_pop = ''
        while value_pop != '(':
            value_pop = new_infix.pop()
            if value_pop != '(' and value_pop != '|' and value_pop != ')':
                first_set.add(value_pop)

        second_set = []
        infix_regex, i, second_set = handle_brackets(infix_regex, i, second_set)

        second_set = set(second_set)

        second_set.discard(')')
        second_set.discard('(')
        second_set.discard('|')

        new_set = first_set.difference(second_set)

        new_infix.append('(')

        var = 0
        for varia in new_set:
            new_infix.append(varia)
            if var < (len(new_set) - 1):
                new_infix.append('|')
            var += 1

        new_infix.append(')')

        return infix_regex, i, new_infix
    

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
            infix_regex, i, new_infix = handle_slash(infix_regex, i, new_infix)
            continue
        
        elif char == '\'':
            infix_regex, i, new_infix = handle_comilla(infix_regex, i, new_infix)
            continue

        elif char == '[':
            infix_regex, i, new_infix = handle_brackets(infix_regex, i, new_infix)
            continue
        
        elif char == '^':
            infix_regex, i, new_infix = handle_negate(infix_regex, i, new_infix)
            continue

        elif char == '\"':
            infix_regex, i, new_infix = handle_double_comilla(infix_regex, i, new_infix)
            continue

        elif char == '_':
            infix_regex, i, new_infix = char_universe(infix_regex, i, new_infix)
            continue
        
        elif char == '#':
            infix_regex, i, new_infix = char_arroba(infix_regex, i, new_infix)
            continue
            
        else:
            if check_operators:
                print("Error léxico, operador no reconocido: ", char)
                sys.exit()             
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

    operadores = ['*', '+', '?', '|', '(', ')', '!']
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

    archivo = "slr-3.yal"

    Machines = {
        "Commentarios": "\"(*\" *[' '-'&''+'-'}''á''é''í''ó''ú''ñ''\n''\t']* *\"*)\"",
        "Declaration": "let +['a'-'z']* +=",
        "Variables": "('['(^])*]|^( \n)*)+",
        "Reglas": "rule *tokens *=",
        "Tokens1": "['&'-'}']+",
        "Tokens2": "'|' *['\"'-'}']*",
        "Returns": "{ *return *['A'-'Z']* *}",
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

    data = readYalexFile(archivo)

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
            if variables != []:
                print("Error léxico, existe un id sin definición")
                print(variables)
                print(values)
                sys.exit()
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
                if variables != [] and len(variables) < 2:
                    values[variables.pop()] = valores
                else:
                    print("Error léxico, existe un id sin definición")
                    print("valores: ", valores)
                    print(variables)
                    print(values)
                    sys.exit()
                temp_tokens.append(valores)
                contador += 1
                i = num
                continue
    
        if read_tokens:
            bol, num, valores = simAFD.exec(returns_transitions, returns_inicial, returns_final, data, i)
            if bol:
                print("Returns: " + valores)
                diccionario[contador] = valores
                if temp_tokens != []:
                    tokens_dictionary[temp_tokens.pop()] = valores
                else:
                    print("Error léxico, no existe un token para el siguiente return")
                    sys.exit()
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
            sys.exit()

    if tokens == []:
        print("Error léxico, no se encontraron tokens")
        sys.exit()
    
    print("Diccionario")
    for i in diccionario:
        print(i, ": ", diccionario[i])

    print("Values: ")
    for val in values:
        print(val, ": ", values[val])
    print()

    for val in values:
        valor = values[val]

        if 'let ' in valor:
            print("Error léxico, no se cerro el corchete ", valor.split()[0])
            sys.exit()

        for valo in reversed(values):
            first = valor.find(valo)
            last = 0
            if first != -1:
                last = first + len(valo)

            if first != -1:
                if first - 1 >= 0 and valor[first - 1] == '\'' and last < len(valor) and valor[last] == '\'':
                    print("entro")
                    continue
                new_string = valor[:first] + values[valo] + valor[last:]
                valor = new_string
                values[val] = new_string

            while first != -1:

                first = valor.find(valo)
                if first != -1:
                    last = first + len(valo)

                if first != -1:
                    if first - 1 >= 0 and valor[first - 1] == '\'' and last < len(valor) and valor[last] == '\'':
                        print("entro")
                        continue
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

    ascii_super = ASCIITransformer(super_string, True)

    print()
    print(ascii_super)
    print()

    super_postfix = shun.exec(ascii_super)
    print(super_postfix)
    stack, node_list, alfabeto = tree.exec(super_postfix, True)

main()