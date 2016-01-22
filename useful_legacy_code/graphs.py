import pdb
import networkx as nx
import matplotlib.pyplot as plt
from experiment.classes import Sentence
# https://stackoverflow.com/questions/15644684/best-practices-for-querying-graphs-by-edge-and-node-attributes-in-networkx


def compress(sentence, entity):
    '''
    A sentence is defined in rookie/classes
    An entiy is a list of strings like "Fire Department"
    '''
    # for now assume only one appearance, hence [0]
    appearance = get_entity_tokens(entity, sentence)[0]
    G = sentence_to_graph(sentence)
    root = get_root(G)
    verbs = G.successors(root)
    verb = verbs[0]  # assume only 1 verb
    outgoing_from_verb = [(G[t[0]][t[1]]['r'], t[1]) for t in G.edges([verb])]
    output = appearance + [sentence.tokens[i[1]] for i in outgoing_from_verb] + [sentence.tokens[verb]]
    output = [sentence.tokens[i[1]] for i in outgoing_from_verb] + [sentence.tokens[verb]]
    output = set(output)
    output = [i for i in output]
    output.sort(key=lambda x: x.token_no)
    return [i.raw for i in output]


def show_graph(G):
    nx.write_dot(G, 'test.dot')
    pos = nx.graphviz_layout(G, prog='dot')
    nx.draw(G, pos, with_labels=True)
    edge_labels = nx.get_edge_attributes(G, 'r')
    nx.draw_networkx_edge_labels(G, pos, labels=edge_labels)
    plt.draw()
    plt.show()


def get_root(G):
    return nx.topological_sort(G)[0]


def sentence_to_graph(sentence):
    G = nx.DiGraph()

    G.add_node(-1, label="root")

    for tok in range(0, len(sentence.tokens)):
        G.add_node(tok, label=sentence.tokens[tok].raw)

    for dep in sentence.deps:
        G.add_edge(dep[1], dep[2])
        G[dep[1]][dep[2]]['r'] = dep[0]
    return G


def get_entity_tokens(entity, sentence):
    entity_appearances = []
    for i in range(0, len(sentence.tokens)):
        toks = [i for i in sentence.tokens[i: i + len(entity)]]
        if [i.raw for i in toks] == entity:
            entity_appearances.append(toks)
    return entity_appearances