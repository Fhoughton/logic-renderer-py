import graphviz

node_count = 0

def create_gate_2_1(name, node_a, node_b, node_out):
    global g, node_count
    ident = str(node_count)
    g.node(ident, name, shape='rectangle')

    if node_a != None:
        g.edge(node_a, ident)
    if node_b != None:
        g.edge(node_b, ident)
    if node_out != None:
        g.edge(ident, node_out)
    node_count += 1

    return ident

def create_gate_2_2(name, node_a, node_b, node_out_a, node_out_b):
    global g, node_count
    ident = str(node_count)
    g.node(ident, name, shape='rectangle')

    if node_a != None:
        g.edge(node_a, ident)
    if node_b != None:
        g.edge(node_b, ident)
    if node_out_a != None:
        g.edge(ident, node_out_a)
    if node_out_b != None:
        g.edge(ident, node_out_b)
    node_count += 1

    return ident

def create_gate_3_2(name, node_a, node_b, node_c, node_out_a, node_out_b):
    global g, node_count
    ident = str(node_count)
    g.node(ident, name, shape='rectangle')

    if node_a != None:
        g.edge(node_a, ident)
    if node_b != None:
        g.edge(node_b, ident)
    if node_c != None:
        g.edge(node_c, ident)
    if node_out_a != None:
        g.edge(ident, node_out_a)
    if node_out_b != None:
        g.edge(ident, node_out_b)
    node_count += 1

    return ident

def bracket(string):
    if string == None:
        return ""
    return "(" + string + ")"

def make_and(name, a, b, out):
    return create_gate_2_1(f"AND {bracket(name)}", a, b, out)

def make_xor(name, a, b, out):
    return create_gate_2_1(f"XOR {bracket(name)}", a, b, out)

def make_input(name):
    global g, node_count
    ident = str(node_count)
    g.node(ident, name, shape='doublecircle')
    node_count += 1
    return ident

def make_output(name):
    global g, node_count
    ident = str(node_count)
    g.node(ident, name, shape='doubleoctagon')
    node_count += 1
    return ident

half_adder_count = 0

def make_half_adder(in_a, in_b, out_h, out_l, minify=False, trace=False):
    global g, node_count, main_graph, half_adder_count
    name = "HALF-ADDER_" + str(half_adder_count)
    half_adder_count += 1

    if not minify:
        if trace:
            h_last = make_and(name + " [h]", in_a, in_b, out_h)
            l_last = make_xor(name + " [l]", in_a, in_b, out_l)
        else:
            h_last = make_and(None, in_a, in_b, out_h)
            l_last = make_xor(None, in_a, in_b, out_l)
        return {'h': h_last, 'l': l_last}
    else:
        ident = create_gate_2_2(name, in_a, in_b, out_h, out_l)
        return {'h': ident, 'l': ident}

full_adder_count = 0

def make_full_adder(in_a, in_b, in_c, out_h, out_l, minify=False):
    global full_adder_count
    name = "FULL-ADDER_" + str(full_adder_count)
    full_adder_count += 1
    if not minify:
        hadd1 = make_half_adder(in_a, in_b, None, None)
        hadd2 = make_half_adder(hadd1['l'], in_c, None, out_l)
        hadd3 = make_half_adder(hadd1['h'], hadd2['h'], None, out_h)
        return hadd3
    else:
        ident = create_gate_3_2(name, in_a, in_b, in_c, out_h, out_l)
        return {'h': ident, 'l': ident}

def create_graph_contents():
    in_a = make_input('a')
    in_b = make_input('b')
    in_c = make_input('c')
    out_h = make_output('h')
    out_l = make_output('l')

    make_full_adder(in_a, in_b, in_c, out_h, out_l, False)

main_graph = graphviz.Digraph(engine='dot')
g = main_graph
create_graph_contents()
f = open("output.dot", "w")
f.write(g.source)
f.close()
