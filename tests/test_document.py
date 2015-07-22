import unittest
import json
import pdb
import glob
import itertools

from rookie.classes import NPEPair
from rookie.utils import dedupe_people
from rookie import processed_location
from rookie.classes import Document
from rookie.classes import Window
from rookie.classes import Coreferences
from rookie.classes import N_Grammer
from rookie.classes import propagate_first_mentions
from rookie.utils import stop_word, get_gramner


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
        bigrams = grammer.get_syntactic_ngrams(sentence.tokens)[0]
        self.assertTrue(all(bigram[0].is_noun() or
                            bigram[0].is_adjective()) for b in bigrams)
        trigrams = grammer.get_syntactic_ngrams(sentence.tokens)[1]
        self.assertTrue(all(bigram[0].is_noun() or
                        bigram[0].is_adjective()) for b in trigrams)

    def test_find_window(self):
        with open("data/sample_wrapper_output_2.json", "r") as to_read:
            py_wrapper_output = json.loads(to_read.read())
        doc = Document(py_wrapper_output)
        sentence = doc.sentences[0]
        window = Window()
        out = window.get_window(sentence.tokens, sentence.ner[3].tokens, 1)
        out = " ".join([i.raw for i in out])
        target = "Mayor Mitch Landrieus Great"
        self.assertEqual(out, target)

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
                window = Window.get_window(sentence.tokens, ner.tokens, 10)
                self.assertTrue(len(window) - len(ner.tokens),
                                20 - len(ner.tokens))

    def test_strip_stop_words(self):
        with open("data/sample_wrapper_output_2.json", "r") as to_read:
            py_wrapper_output = json.loads(to_read.read())
        corefs = Coreferences(py_wrapper_output)
        doc = Document(py_wrapper_output, corefs)
        sentence = doc.sentences[0]
        valids = [i for i in get_gramner(sentence, True)]
        self.assertEqual(len(valids), 25)  # 2 stop gramner stripped out
        # 27 gramner to start
        self.assertEqual(len(get_gramner(sentence, False)), 27)

    def test_strip_stop_words2(self):
        self.assertTrue(stop_word("NEW ORLEANS"))

    def test_merging_people(self):
        with open("data/sample_wrapper_output3.json", "r") as to_read:
            py_wrapper_output = json.loads(to_read.read())['lines']
            corefs = Coreferences(py_wrapper_output)
            doc = Document(py_wrapper_output, corefs)
            sentence = doc.sentences[0]
            ner = sentence.ner
            ner2 = dedupe_people(list(ner))  # pass a new copy
            # The NER "Serpas" should lose to the NER "Ronal Serpas"
            self.assertEqual(len(ner2) + 1, len(ner))

if __name__ == '__main__':
    unittest.main()
