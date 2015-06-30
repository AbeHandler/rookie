import unittest
import json

from rookie.classes import Span
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
        out = window.get_window(sentence, sentence.ner[3].tokens, 1)
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
                self.assertTrue(len(window) - len(ner.tokens),
                                20 - len(ner.tokens))

    def test_get_windows(self):
        with open("data/sample_wrapper_output_2.json", "r") as to_read:
            py_wrapper_output = json.loads(to_read.read())
        corefs = Coreferences(py_wrapper_output)
        doc = Document(py_wrapper_output, corefs)
        for sentence in doc.sentences:
            for ner in sentence.ner:
                window = Window.get_window(sentence, ner.tokens, 10)
                self.assertTrue(len(window) - len(ner.tokens),
                                20 - len(ner.tokens))

    def test_span(self):
        with open("data/sample_wrapper_output_2.json", "r") as to_read:
            py_wrapper_output = json.loads(to_read.read())
        doc = Document(py_wrapper_output)
        ner = doc.ner
        grams = doc.ngrams
        npe_one = [l for l in ner[0].tokens]
        npe_two = [l for l in grams[3]]
        span = Span(npe_one, npe_two, doc)
        # span is zero. they overlap
        self.assertTrue(span.distance == 0)

        # same with the swap
        span2 = Span(npe_two, npe_one, doc)
        self.assertTrue(span2.distance == 0)

    def test_span_2(self):
        with open("data/sample_wrapper_output_2.json", "r") as to_read:
            py_wrapper_output = json.loads(to_read.read())
        doc = Document(py_wrapper_output)
        ner = doc.ner
        grams = doc.ngrams
        npe_one = [l for l in ner[0].tokens]
        npe_two = [l for l in grams[5]]
        span = Span(npe_one, npe_two, doc)
        # the distance is 11, same sentence
        self.assertTrue(span.distance == 11)
        span2 = Span(npe_two, npe_one, doc)
        # distance should still be 11 even if swapped
        self.assertTrue(span2.distance == 11)

    def test_span_3(self):
        with open("data/sample_wrapper_output_2.json", "r") as to_read:
            py_wrapper_output = json.loads(to_read.read())
        doc = Document(py_wrapper_output)
        ner = doc.ner
        grams = doc.ngrams
        npe_one = [l for l in ner[0].tokens]
        npe_two = [l for l in grams[22]]
        s1 = doc.sentences[npe_one[0].sentence_no]
        s2 = doc.sentences[npe_two[0].sentence_no]
        span = Span(npe_one, npe_two, doc)
        # the distance is 11, same sentence
        self.assertTrue(span.distance == 58)
        span2 = Span(npe_two, npe_one, doc)
        # distance should still be 11 even if swapped
        self.assertTrue(span2.distance == 58)

if __name__ == '__main__':
    unittest.main()
