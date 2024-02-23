def getPrecedence(ope):
    precedencia = {40: 1, 124: 2, 46: 3, 43: 4, 63: 4, 42: 4}
    if ope not in precedencia:
        return 5
    return precedencia[ope]

def formatear_regex(regex):
    all_operators = [124, 43, 63, 42]
    binary_operators = [124]
    res = []

    for i in range(len(regex)):
        c1 = regex[i]

        if i + 1 < len(regex):
            c2 = regex[i + 1]

            res.append(c1)

            if c1 != 40 and c2 != 41 and c2 not in all_operators and c1 not in binary_operators:
                res.append(46)
    
    res.append(regex[-1])
    return res

def infix_to_postfix(regex):
    stack = []
    postfix = []
    regexp = formatear_regex(regex)
    print("formatear_regex: ", regexp)

    for c in regexp:
        if c == 40:
            stack.append(c)
        elif c == 41:
            while stack[-1] != 40:
                postfix.append(stack.pop())
            stack.pop()
        else:
            while len(stack) > 0:
                peekedChar = stack[-1]
                peekedCharPrecedence = getPrecedence(peekedChar)
                currentCharPrecedence = getPrecedence(c)

                if peekedCharPrecedence >= currentCharPrecedence:
                    postfix.append(stack.pop())
                else:
                    break

            stack.append(c)

    while len(stack) > 0:
        postfix.append(stack.pop())
    return postfix

def exec(expression):
    postfix = infix_to_postfix(expression)
    return postfix