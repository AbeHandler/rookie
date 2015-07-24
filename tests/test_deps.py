import unittest
import json
import pdb
import glob
import re
import pdb
from rookie.classes import Document
from rookie.compressor import sentence_to_graph, get_root, get_entity_tokens, compress


def extract_compression_tree(entity, sentence):
    first_token_in_entity = entity[0]
    pdb.set_trace()
    # climb from token until you hit root or cross a subject or object


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
        entity = "New Orleans Civil Service Commission".split(" ")
        entity = [str(i) for i in entity]
        print compress(sentence, entity)

    def test_lots_o_compression(self):
        filest = glob.glob("data/lens_processed/*")
        entity = "Mitch Landrieu".split(" ")
        entity = [str(i) for i in entity]
        for f in filest:
            with open(f, "r") as to_read:
                py_wrapper_output = json.loads(to_read.read())['lines']
                # print f
            try:
                doc = Document(py_wrapper_output)
                for sentence in doc.sentences:
                    text = " ".join([i.raw for i in sentence.tokens])
                    if "Mitch Landrieu" in text:
                        print f
                        print " ".join([i.raw for i in sentence.tokens])
                        print compress(sentence, entity)
            except TypeError:
                pass
            except IndexError:
                pass
#        I dont think I need this tree searching thing        
#        for out in outgoing_from_verb:
#            tokens_in_tree = [G.node[i] for i in nx.dfs_tree(G, out[1])]
#            tokens_in_tree = outgoing_from_verb
#            if set(tokens_in_tree).issuperset(entity):
#                print tokens_in_tree
#            pdb.set_trace()

if __name__ == '__main__':
    unittest.main()
