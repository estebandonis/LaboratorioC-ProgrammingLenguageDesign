class Node:
    def __init__(self, value, id):
        self.value = value
        self.id = id
        self.number = None
        self.nullable = False
        self.primerapos = set()
        self.ultimapos = set()
        self.siguientepos = set()
        self.padre = None
        self.left = None
        self.right = None

    def id_return(self):
        return self.id
    
def search_node(stack, id):
    for i in range(len(stack)):
        item = stack[i]
        if item.id == id:
            return item
    return None

def search_node_by_number(stack, number):
    for i in range(len(stack)):
        item = stack[i]
        if item.number == number:
            return item
    return None

def siguiente_pos(stack, node_list, pos, primerapos):
    pos_node = search_node_by_number(stack, pos)
    pos_node.siguientepos = pos_node.siguientepos.union(primerapos)
    node_list[pos_node.number] = [pos_node.value, pos_node.siguientepos]
    index = stack.index(pos_node)
    stack[index] = pos_node
    return stack, node_list

def or_operation(stack, temp_stack, contador_simbolos, left_node, right_node):
    or_node = Node(124, contador_simbolos)
    left_node.padre = or_node.id
    or_node.left = left_node.id
    stack.append(left_node)
    right_node.padre = or_node.id
    or_node.right = right_node.id
    stack.append(right_node)
    temp_stack.append(or_node)
    contador_simbolos += 1
    return stack, temp_stack, contador_simbolos

def kleene_operation(stack, temp_stack, contador_simbolos, left_node):
    kleene_node = Node(42, contador_simbolos)
    left_node.padre = kleene_node.id
    kleene_node.left = left_node.id
    kleene_node.nullable = True
    stack.append(left_node)
    temp_stack.append(kleene_node)
    contador_simbolos += 1
    return stack, temp_stack, contador_simbolos

def concat_operation(stack, temp_stack, contador_simbolos, left_node, right_node):
    concat_node = Node(46, contador_simbolos)
    left_node.padre = concat_node.id
    concat_node.left = left_node.id
    stack.append(left_node)
    right_node.padre = concat_node.id
    concat_node.right = right_node.id
    stack.append(right_node)
    temp_stack.append(concat_node)
    contador_simbolos += 1
    return stack, temp_stack, contador_simbolos    

def operando_operation(temp_stack, alfabeto, simbolo, contador_simbolos, contador_leafs):
    if simbolo not in alfabeto and simbolo != 120500 and simbolo != 35:
        alfabeto.append(simbolo)

    leaf_node = Node(simbolo, contador_simbolos)
    if simbolo == 120500:
        leaf_node.nullable = True
    leaf_node.number = contador_leafs
    leaf_node.primerapos.add(contador_leafs)
    leaf_node.ultimapos.add(contador_leafs)
    temp_stack.append(leaf_node)
    contador_simbolos += 1
    contador_leafs += 1
    return temp_stack, alfabeto, contador_simbolos, contador_leafs

def exec(postfix):
    postfix.append(35)
    postfix.append(46)
    stack = []
    temp_stack = []
    alfabeto = []

    contador_simbolos = 0
    contador = 0
    contador_leafs = 1

    while contador < len(postfix):
        simbolo = postfix[contador]
        if simbolo == 124:
            right_node = temp_stack.pop()
            left_node = temp_stack.pop()
            stack, temp_stack, contador_simbolos = or_operation(stack, temp_stack, contador_simbolos, left_node, right_node)

        elif simbolo == 46:
            right_node = temp_stack.pop()
            left_node = temp_stack.pop()
            stack, temp_stack, contador_simbolos = concat_operation(stack, temp_stack, contador_simbolos, left_node, right_node)

        elif simbolo == 42:
            left_node = temp_stack.pop()
            stack, temp_stack, contador_simbolos = kleene_operation(stack, temp_stack, contador_simbolos, left_node)
        
        elif simbolo == 43:
            left_node = temp_stack.pop()
            temp_stack, alfabeto, contador_simbolos, contador_leafs = operando_operation(temp_stack, alfabeto, left_node.value, contador_simbolos, contador_leafs)
            stack, temp_stack, contador_simbolos = kleene_operation(stack, temp_stack, contador_simbolos, temp_stack.pop())
            right_node = temp_stack.pop()
            stack, temp_stack, contador_simbolos = concat_operation(stack, temp_stack, contador_simbolos, left_node, right_node)

        elif simbolo == 63:
            left_node = temp_stack.pop()
            temp_stack, alfabeto, contador_simbolos, contador_leafs = operando_operation(temp_stack, alfabeto, 120500, contador_simbolos, contador_leafs)
            right_node = temp_stack.pop()
            stack, temp_stack, contador_simbolos = or_operation(stack, temp_stack, contador_simbolos, left_node, right_node)

        else:
            temp_stack, alfabeto, contador_simbolos, contador_leafs = operando_operation(temp_stack, alfabeto, simbolo, contador_simbolos, contador_leafs)

        contador += 1
    
    if len(temp_stack) > 0:
        stack.append(temp_stack.pop())

    for i in range(len(stack)):
        item = stack[i]
        if item.left != None and item.right != None:
            if item.value == 124:
                item.nullable = search_node(stack, item.left).nullable or search_node(stack, item.right).nullable
                stack[i] = item
            elif item.value == 46:
                item.nullable = search_node(stack, item.left).nullable and search_node(stack, item.right).nullable
                stack[i] = item 
    
    for i in range(len(stack)):
        item = stack[i]
        if item.left != None and item.right != None:
            item_left = search_node(stack, item.left)
            item_right = search_node(stack, item.right)
            if item.value == 124:
                item.primerapos = item_left.primerapos.union(item_right.primerapos)
                stack[i] = item
            elif item.value == 46:
                if item_left.nullable:
                    item.primerapos = item_left.primerapos.union(item_right.primerapos)
                else:
                    item.primerapos = item_left.primerapos
                stack[i] = item
        elif item.value == 42:
            item.primerapos = search_node(stack, item.left).primerapos
            stack[i] = item
                
    for i in range(len(stack)):
        item = stack[i]
        if item.left != None and item.right != None:
            item_left = search_node(stack, item.left)
            item_right = search_node(stack, item.right)
            if item.value == 124:
                item.ultimapos = item_left.ultimapos.union(item_right.ultimapos)
                stack[i] = item
            elif item.value == 46:
                if item_right.nullable:
                    item.ultimapos = item_left.ultimapos.union(item_right.ultimapos)
                else:
                    item.ultimapos = item_right.ultimapos
                stack[i] = item
        elif item.value == 42:
            item.ultimapos = search_node(stack, item.left).ultimapos
            stack[i] = item        

    node_list = {}

    for i in range(len(stack)):
        item = stack[i]
        if item.value == 46:
            item_left = search_node(stack, item.left)
            item_right = search_node(stack, item.right)
            for pos in item_left.ultimapos:
                stack, node_list = siguiente_pos(stack, node_list, pos, item_right.primerapos)        
        elif item.value == 42:
            for pos in item.ultimapos:
                stack, node_list = siguiente_pos(stack, node_list, pos, item.primerapos)

    for i in range(len(stack)):
        node = stack[i]
        if node.value == 35:
            node_list[node.number] = [node.value, node.siguientepos]

    return stack, node_list, alfabeto