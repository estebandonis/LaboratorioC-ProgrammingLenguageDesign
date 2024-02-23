import pydotplus

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

def dfa_to_nfa(states, symbols, start_state, final_states, transitions):

    dfa_states = [epsilon(start_state, transitions)]
    dfa_transitions = []

    for state in dfa_states:
        for x in symbols:
            new_state = epsilon(move(state, x, transitions), transitions)
            if new_state not in dfa_states:
                dfa_states.append(new_state)

            dfa_transitions.append((state, x, new_state))

    acceptance_states = [state for state in dfa_states if any(
        s in final_states for s in state)]
    start_state = [
        state for state in dfa_states if start_state.issubset(state)][0]

    # check if E is in a transition, if so add it to states
    # for transition in dfa_transitions:
    #     if transition[2] == 'E':
    #         dfa_states.append('E')
    #         break

    # # add transition of E to E with all symbols
    # for symbol in symbols:
    #     dfa_transitions.append(('E', symbol, 'E'))

    return (dfa_states, acceptance_states, dfa_transitions, start_state)

def create_dfa_graph(states, acceptance_states, transitions, symbols, start_state):
    # Convert sets to strings
    states = [str(state) for state in states]
    start_state = str(start_state)
    acceptance_states = [str(state) for state in acceptance_states]

    # Create a DOT format representation of the DFA
    dot = pydotplus.Dot()
    dot.set_rankdir("LR")  # Use 'TB' for top to bottom layout
    dot.set_prog("neato")

    # Create nodes for each state
    state_nodes = {}
    num = 0
    for state in states:
        node = pydotplus.Node(num)
        if state == start_state:
            node.set_name("Start")
            node.set_shape("circle")
            node.set_style("filled")

        if state in acceptance_states:
            node.set_shape("doublecircle")  # Final states are double circled
        node.set_fontsize(12)  # Set font size
        node.set_width(0.6)  # Set the desired width
        node.set_height(0.6)  # Set the desired height
        state_nodes[state] = node
        dot.add_node(node)

        num += 1

    # Add transitions as edges
    for (source, symbol, target) in transitions:
        edge = pydotplus.Edge(state_nodes[str(source)], state_nodes[str(target)], label=symbol)
        dot.add_edge(edge)

    return dot

def write_info_to_file(states, final_states, transitions, symbols, start_state, file_path):
    with open(file_path, 'w') as file:
        file.write("Estados = " + str(states) + "\n")
        file.write("Aceptacion = " + str(final_states) + "\n")
        file.write("Transicion = " + str(transitions) + "\n")
        file.write("Simbolos = " + str(symbols) + "\n")
        file.write("Inicio = " + str(start_state) + "\n")

def exec(estados, simbolos, estados_inicial, estados_aceptacion, transiciones):
    symbols = simbolos
    start_state = estados_inicial

    dfa_states, acceptance_states, dfa_transitions, start_state = dfa_to_nfa(
        estados,
        symbols,
        start_state,
        estados_aceptacion,
        transiciones,
    )

    # Remove entries with an empty set from dfa_states
    dfa_states = [state for state in dfa_states if state]

    # Remove entries with an empty set from acceptance_states
    acceptance_states = [state for state in acceptance_states if state]

    # Remove entries with an empty set from dfa_transitions
    dfa_transitions = [(state1, symbol, state2) for state1, symbol, state2 in dfa_transitions if state1 and state2]

    states = dfa_states
    final_states = acceptance_states
    transitions = dfa_transitions

    # Write information to a text file
    write_info_to_file(states, final_states, transitions, symbols, start_state, "texts/dfa_info.txt")

    pydotplus.find_graphviz()

    graph = create_dfa_graph(states, final_states, transitions, symbols, start_state)

    # Save or display the graph
    png_file_path = "pngs/dfa_graph.png"
    graph.write_png(png_file_path)  # Save PNG file

    return states, symbols, transitions, start_state, final_states