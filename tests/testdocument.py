import unittest
import glob
import json
import pdb

from rookie.classes import Document
from rookie.classes import N_Grammer

files = glob.glob("/Volumes/USB 1/lens_processed/*")

valid_two_grams = ["NN", "AN"]
valid_three_grams = ["AAN", "NNN", "ANN"]


class GenericTestCase(unittest.TestCase):

    def test_make_document(self):
        fileone = files[0]
        with open("data/sample_wrapper_output.json", "r") as to_read:
            py_wrapper_output = json.loads(to_read.read())
        doc = Document(py_wrapper_output)
        self.assertTrue(len(doc.sentences) > 0)

    def test_find_entities(self):
        fileone = files[0]
        with open("data/sample_wrapper_output_2.json", "r") as to_read:
            py_wrapper_output = json.loads(to_read.read())
        doc = Document(py_wrapper_output)
        ner = doc.sentences[0].ner[0]
        self.assertEqual(ner.type, "ORGANIZATION")
        org_name = " ".join([i.raw for i in ner.tokens])
        self.assertEqual(org_name, "New Orleans Civil Service Commission")

    def test_create_ngrams(self):
        fileone = files[0]
        with open("data/sample_wrapper_output_2.json", "r") as to_read:
            py_wrapper_output = json.loads(to_read.read())
        doc = Document(py_wrapper_output)
        sentence = doc.sentences[0]
        grams = N_Grammer()
        gram_total = len([(i[0].raw, i[1].raw) for i in
                         grams.get_ngrams(sentence.tokens)])
        self.assertEqual(gram_total + 1, len(sentence.tokens))

    def test_filter_ngrams(self):
        fileone = files[0]
        with open("data/sample_wrapper_output_2.json", "r") as to_read:
            py_wrapper_output = json.loads(to_read.read())
        doc = Document(py_wrapper_output)
        sentence = doc.sentences[0]
        grammer = N_Grammer()
        bigrams = [i for i in grammer.get_ngrams(sentence.tokens)]
        for bigram in bigrams:
            if "".join([(j.abreviated_pos()) for j in bigram]) in valid_two_grams:
                self.assertTrue(bigram[0].is_noun() or bigram[0].is_adjective())
'''
    def test_get_lidstones(self):
        result = query_elasticsearch("KIPP")
        print strftime("%Y-%m-%d %H:%M:%S", gmtime())
        counts = get_corpus_counts("3")
        print strftime("%Y-%m-%d %H:%M:%S", gmtime())
        trigrams = get_lidstones(result.trigrams, counts)
        print strftime("%Y-%m-%d %H:%M:%S", gmtime())
        trigrams = sorted(trigrams,
                          key=lambda x: x[1],
                          reverse=True)
        print trigrams[0:75]
'''

if __name__ == '__main__':
    unittest.main()
