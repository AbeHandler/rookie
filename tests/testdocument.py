import unittest
import json
import pdb
import glob

from rookie.classes import Document
from rookie.classes import Window
from rookie.classes import Coreferences
from rookie.classes import N_Grammer
from rookie.classes import propagate_first_mentions


class GenericTestCase(unittest.TestCase):

    def test_make_document(self):
        with open("data/sample_wrapper_output.json", "r") as to_read:
            py_wrapper_output = json.loads(to_read.read())
        doc = Document(py_wrapper_output)
        self.assertTrue(len(doc.sentences) > 0)

    def test_find_entities(self):
        with open("data/sample_wrapper_output_2.json", "r") as to_read:
            py_wrapper_output = json.loads(to_read.read())
        doc = Document(py_wrapper_output)
        ner = doc.sentences[0].ner[0]
        self.assertEqual(ner.type, "ORGANIZATION")
        org_name = " ".join([i.raw for i in ner.tokens])
        self.assertEqual(org_name, "New Orleans Civil Service Commission")

    def test_create_ngrams(self):
        with open("data/sample_wrapper_output_2.json", "r") as to_read:
            py_wrapper_output = json.loads(to_read.read())
        doc = Document(py_wrapper_output)
        sentence = doc.sentences[0]
        grams = N_Grammer()
        gram_total = len([(i[0].raw, i[1].raw) for i in
                         grams.get_ngrams(sentence.tokens)])
        self.assertEqual(gram_total + 1, len(sentence.tokens))

    def test_filter_ngrams(self):
        with open("data/sample_wrapper_output_2.json", "r") as to_read:
            py_wrapper_output = json.loads(to_read.read())
        doc = Document(py_wrapper_output)
        sentence = doc.sentences[0]
        grammer = N_Grammer()
        bigrams = grammer.get_syntactic_ngrams(sentence.tokens)
        self.assertTrue(all(bigram[0].is_noun() or
                            bigram[0].is_adjective()) for b in bigrams)
        trigrams = grammer.get_syntactic_ngrams(sentence.tokens, 3)
        self.assertTrue(all(bigram[0].is_noun() or
                        bigram[0].is_adjective()) for b in trigrams)

    def test_find_window(self):
        with open("data/sample_wrapper_output_2.json", "r") as to_read:
            py_wrapper_output = json.loads(to_read.read())
        doc = Document(py_wrapper_output)
        sentence = doc.sentences[0]
        window = Window()
        out = window.get_window(sentence, sentence.ner[3], 1)
        self.assertEqual(str(out[0].raw), "Mayor")
        self.assertEqual(str(out[1].raw), "Great")

    def test_coref_groups(self):
        with open("data/sample_wrapper_output_2.json", "r") as to_read:
            py_wrapper_output = json.loads(to_read.read())
        corefs = Coreferences(py_wrapper_output)
        doc = Document(py_wrapper_output, corefs)
        self.assertTrue(len(corefs.groups) > -1)

    def test_coref_groups(self):
        with open("data/sample_wrapper_output_2.json", "r") as to_read:
            py_wrapper_output = json.loads(to_read.read())
        corefs = Coreferences(py_wrapper_output)
        doc = Document(py_wrapper_output, corefs)
        for group in [doc.coreferences.groups[155]]:
            for mention in [group[0]]:
                alltoks = doc.sentences[mention.sentence].tokens
                mentiontokens = alltoks[mention.span_start:mention.span_end]
                raws = [t.raw for t in mentiontokens]
                tags = [t.ner_tag for t in mentiontokens]
                self.assertEqual(raws[0], "Alexandra")
                self.assertEqual(tags[0], "PERSON")

    def test_first_mention_person_or_org(self):
        with open("data/sample_wrapper_output_2.json", "r") as to_read:
            py_wrapper_output = json.loads(to_read.read())
        corefs = Coreferences(py_wrapper_output)
        doc = Document(py_wrapper_output, corefs)
        propagate_first_mentions(doc)

    def test_get_windows(self):
        with open("data/sample_wrapper_output_2.json", "r") as to_read:
            py_wrapper_output = json.loads(to_read.read())
        corefs = Coreferences(py_wrapper_output)
        doc = Document(py_wrapper_output, corefs)
        for sentence in doc.sentences:
            for ner in sentence.ner:
                window = Window.get_window(sentence, ner, 10)
                print " ".join([t.raw for t in window]) + " surround "
                print " ".join([i.raw for i in ner.tokens])

if __name__ == '__main__':
    unittest.main()
