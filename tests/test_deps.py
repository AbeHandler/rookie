import unittest
import json
import pdb
import matplotlib.pyplot as plt
import pdb
import networkx as nx
from rookie.classes import Document
from rookie.utils import compress_sentence
from rookie.classes import Token


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
    for dep in sentence.deps:
        G.add_edge(str(dep[1]) + "-" + sentence.tokens[dep[1]].raw, str(dep[2]) + "-" + sentence.tokens[dep[2]].raw)
        G[str(dep[1]) + "-" + sentence.tokens[dep[1]].raw][str(dep[2]) + "-" + sentence.tokens[dep[2]].raw]['r'] = dep[0]
    return G


def extract_compression_tree(entity, sentence):
    first_token_in_entity = entity[0]
    pdb.set_trace()


def get_entity_tokens(entity, sentence):
    entity_appearances = []
    for i in range(0, len(sentence.tokens)):
        toks = [str(i.raw) for i in sentence.tokens[i: i + len(entity)]]
        if toks == entity:
            entity_appearances.append(toks)
    return entity_appearances


class GenericTestCase(unittest.TestCase):

    def test_compress_sentence(self):
        with open("data/tests/sample.json", "r") as to_read:
            py_wrapper_output = json.loads(to_read.read())
        doc = Document(py_wrapper_output)
        sentence = doc.sentences[3]
        # show_graph(sentence_to_graph(sentence))
        entity = "New Orleans Civil Service Commission".split(" ")
        entity = [str(i) for i in entity]
        appearances = get_entity_tokens(entity, sentence)
        for appearance in appearances:
            token_string = [i.raw for i in appearance]
            self.assertEqual(token_string,
                             "New Orleans Civil Service Commission")

if __name__ == '__main__':
    unittest.main()
