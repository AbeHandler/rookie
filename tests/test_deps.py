import unittest
import json
import pdb
import re
import matplotlib.pyplot as plt
import pdb
import networkx as nx
from rookie.classes import Document
from rookie.utils import compress_sentence
from rookie.classes import Token


# https://stackoverflow.com/questions/15644684/best-practices-for-querying-graphs-by-edge-and-node-attributes-in-networkx

def show_graph(G):
    nx.write_dot(G, 'test.dot')
    pos = nx.graphviz_layout(G, prog='dot')
    nx.draw(G, pos, with_labels=True)
    edge_labels = nx.get_edge_attributes(G, 'r')
    nx.draw_networkx_edge_labels(G, pos, labels=edge_labels)
    plt.draw()
    plt.show()


def sentence_to_graph(sentence):
    G = nx.DiGraph()

    G.add_node(-1, label="root")

    for tok in range(0, len(sentence.tokens)):
        G.add_node(tok, label=sentence.tokens[tok].raw)

    for dep in sentence.deps:
        G.add_edge(dep[1], dep[2])
        G[dep[1]][dep[2]]['r'] = dep[0]
    return G


def extract_compression_tree(entity, sentence):
    first_token_in_entity = entity[0]
    pdb.set_trace()
    # climb from token until you hit root or cross a subject or object


def get_entity_tokens(entity, sentence):
    entity_appearances = []
    for i in range(0, len(sentence.tokens)):
        toks = [i for i in sentence.tokens[i: i + len(entity)]]
        if [i.raw for i in toks] == entity:
            entity_appearances.append(toks)
    return entity_appearances


class GenericTestCase(unittest.TestCase):

    def test_get_entity_tokens(self):
        with open("data/tests/sample.json", "r") as to_read:
            py_wrapper_output = json.loads(to_read.read())
        doc = Document(py_wrapper_output)
        sentence = doc.sentences[3]
        # show_graph(sentence_to_graph(sentence))
        entity = "New Orleans Civil Service Commission".split(" ")
        entity = [str(i) for i in entity]
        appearances = get_entity_tokens(entity, sentence)
        for appearance in appearances:
            token_string = " ".join([i.raw for i in appearance])
            self.assertEqual(token_string,
                             "New Orleans Civil Service Commission")

    def test_compression(self):
        with open("data/tests/sample.json", "r") as to_read:
            py_wrapper_output = json.loads(to_read.read())
        doc = Document(py_wrapper_output)
        sentence = doc.sentences[3]
        # show_graph(sentence_to_graph(sentence))
        entity = "New Orleans Civil Service Commission".split(" ")
        entity = [str(i) for i in entity]
        # for now assume only one appearance, hence [0]
        appearance = get_entity_tokens(entity, sentence)[0]
        G = sentence_to_graph(sentence)
        root = nx.topological_sort(G)[0]
        verbs = G.successors(root)
        verb = verbs[0]  # assume only 1 verb
        outgoing_from_verb = [(G[t[0]][t[1]]['r'], t[1]) for t in G.edges([verb])]
        subject_object = [sentence.tokens[i[1]] for i in outgoing_from_verb if "subj" in i[0] or "obj" in i[0]]
        output = appearance + [sentence.tokens[i[1]] for i in outgoing_from_verb] + [sentence.tokens[verb]]
        output = set(output)
        output = [i for i in output]
        output.sort(key=lambda x: x.token_no)
        print [i.raw for i in output]
#        I dont think I need this tree searching thing        
#        for out in outgoing_from_verb:
#            tokens_in_tree = [G.node[i] for i in nx.dfs_tree(G, out[1])]
#            tokens_in_tree = outgoing_from_verb
#            if set(tokens_in_tree).issuperset(entity):
#                print tokens_in_tree
#            pdb.set_trace()

if __name__ == '__main__':
    unittest.main()
