import graphviz
import json

# CIRCUIT SIMULATION
def classify_node(node):
    node = list(node)
    node[2] = classify_shape(node[2])
    return tuple(node)

def classify_shape(shape):
    if shape == 'rectangle':
        return "Gate"
    elif shape == 'doublecircle':
        return "Input"
    elif shape == 'doubleoctagon':
        return "Output"
    else:
        raise Exception(f"Unknown shape: {shape}")

class SimNode():
    def __init__(self, internal_id, identifier, label, nodeType, value=0):
        self.internal_id = internal_id
        self.identifier = identifier
        self.label = label.rstrip().lstrip()
        self.nodeType = nodeType
        self.value = value

        if nodeType == "Gate":
            self.inputs = []

    def receive(self, value):
        #print("receive", self.nodeType)
        if self.nodeType == "Gate":
            self.inputs.append(value)
        else:
            self.value = value

    def evaluate(self):
        if self.nodeType != "Gate":
            raise Exception("EVALUATED SOMETHING OTHER THAN A GATE")
        
        #print(self.label, self.inputs)
        if self.label == "XOR":
            return bool(self.inputs[0]) ^ bool(self.inputs[1])
        elif self.label == "OR":
            return bool(self.inputs[0]) or bool(self.inputs[1])
        elif self.label == "AND":
            return bool(self.inputs[0]) and bool(self.inputs[1])

def do_simulation(graph, bindings={}):
    json_string = graph.pipe('json').decode()
    json_dict = json.loads(json_string)

    # now, you have a JSON dictionary that has two relevant keys:
    # 'objects' for nodes and 'edges' for, well, edges.
    # you can iterate over the nodes and get the (x,y) position for each node as follows:
    nodes = []

    for obj in json_dict['objects']:
        nodes.append( (obj['name'], obj['label'], obj['shape'], tuple(map(float, obj['pos'].split(","))), obj['_gvid'] ) )

    nodes.sort(key = lambda x: x[3][1], reverse=True) # sort by Y coord
    for i in range(len(nodes)):
        nodes[i] = classify_node(nodes[i])

    node_classes = []

    for node in nodes:
        node_classes.append( SimNode(node[4], node[0], node[1], node[2]) )

    edge_classes = []

    for edge in json_dict['edges']:
        edge_classes.append( (edge['tail'], edge['head']) ) # I flipped these maybe that's wrong too, who knows lol

    outputs = []

    # Now we loop through the nodes and propogate their values to their connections one by one, if it's a gate we evaluate it
    for i in range(len(node_classes)):
        node = node_classes[i]
        # Evaluate
        if node.nodeType == "Input":
            if node.label == "0":
                node.value = 0
            elif node.label == "1":
                node.value = 1
            else:
                if node.label in bindings:
                    node.value = bindings[node.label]
                else:
                    node.value = int(int(input(f"Enter input for input {node.label}: ")) > 0)
        elif node.nodeType == "Output":
            outputs.append( (node.label, node.value) )
        elif node.nodeType == "Gate":
            node.value = node.evaluate()
        else:
            raise Exception(f"Evaluate in simulator got invalid node type {node.nodeType}")

        # Propogate
        for edge in edge_classes:
            head = edge[0]
            tail = edge[1]

            # propogate to the tail!
            if head == node.internal_id:
                target = None
                for child in node_classes:
                    if child.internal_id == tail:
                        target = child

                
                target.receive(node.value)

    # Display outputs
    for output in outputs:
        print(output[0], "=", output[1])


# DIAGRAM RENDERING WITH GRAPHVIZ
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

# expects array of in_a and in_b for each 2 bits, array of out_sum for each 2 bits and 
def make_n_bit_adder(bit_count, in_a, in_b, out_sum, initial_carry, final_carry):
    out = []

    bit_count = int(bit_count / 2)

    # Previous carry from last two bits added
    last_carry = initial_carry

    for i in range(bit_count):
        if i == bit_count - 1:
            adder = make_full_adder(in_a[i], in_b[i], last_carry, out_sum[i], final_carry)
        else:
            adder = make_full_adder(in_a[i], in_b[i], last_carry, out_sum[i], None)
        out.append(adder)
        last_carry = adder['carry']

    return out

def add16(in_a, in_b, out_sum, initial_carry, final_carry):
    return make_n_bit_adder(16, in_a, in_b, out_sum, initial_carry, final_carry)

#b = least significant bit
#b3 = most significant bit
def create_graph_contents():
    in_a = make_input('a')
    in_b = make_input('b')
    in_a2 = make_input('a2')
    in_b2 = make_input('b2')
    in_a3 = make_input('a3')
    in_b3 = make_input('b3')
    out_sum = make_output('sum')
    out_sum2 = make_output('sum2')
    out_sum3 = make_output('sum3')
    out_final_carry = make_output('final_carry')

    initial_carry = make_input("1")

    make_n_bit_adder(6, [in_a, in_a2, in_a3], [in_b, in_b2, in_b3], [out_sum, out_sum2, out_sum3], initial_carry, out_final_carry)
    #make_n_bit_adder(4, [in_a, in_a2], [in_b, in_b2], [out_sum, out_sum2], initial_carry, out_final_carry)

main_graph = graphviz.Digraph(engine='dot')
g = main_graph
create_graph_contents()
f = open("output.dot", "w")
f.write(g.source)
f.close()

do_simulation(g, {
        "a":1,
        "a2":1,
        "a3":1,
        "b":1,
        "b2":1,
        "b3":1
    })
