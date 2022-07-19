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

def make_or(name, a, b, out):
    return create_gate_2_1(f"OR {bracket(name)}", a, b, out)

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

full_adder_count = 0

def make_full_adder(in_a, in_b, in_c, out_sum, out_carry, minify=False, trace=False):
    global full_adder_count

    full_name = "FULL-ADDER_" + str(full_adder_count)

    if trace:
        name = full_name
    else:
        name = None
    full_adder_count += 1
    if not minify:
        xor_1 = make_xor(name, in_a, in_b, None)
        and_1 = make_and(name, in_a, in_b, None)
        xor_sum = make_xor(name, xor_1, in_c, out_sum)
        and_2 = make_and(name, xor_1, in_c, None)
        or_carry = make_or(name, and_1, and_2, out_carry)
        return {'sum': xor_sum, 'carry': or_carry}
    else:
        ident = create_gate_3_2(full_name, in_a, in_b, in_c, out_sum, out_carry)
        return {'carry': ident, 'sum': ident}

# expects array of in_a and in_b for each 2 bits, array of out_carry for each 2 bits and 
def make_n_bit_adder(bit_count, in_a, in_b, out_sum, out_carry):
    out = []

    last_carry = make_input("1")
    for i in range(bit_count):
        adder = make_full_adder(in_a[i], in_b[i], last_carry, out_sum[i], out_carry[i])
        out.append(adder)
        last_carry = adder['carry']

    return out

def create_graph_contents():
    in_a = make_input('a')
    in_b = make_input('b')
    in_c = make_input('c')
    out_sum = make_output('sum')
    out_carry = make_output('carry')

    make_full_adder(in_a, in_b, in_c, out_sum, out_carry, False)

main_graph = graphviz.Digraph(engine='dot')
g = main_graph
create_graph_contents()
f = open("output.dot", "w")
f.write(g.source)
f.close()
