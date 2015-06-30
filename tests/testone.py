import unittest
import redis
import pdb


from time import gmtime, strftime
from rookie.classes import Window
from rookie.utils import query_elasticsearch
from rookie.utils import clean_titles
from rookie.utils import clean_punctuation
from rookie.utils import get_corpus_counts
from rookie.utils import get_lidstones
from rookie.utils import load_cache


class GenericTestCase(unittest.TestCase):

    def test_clean_punctuation(self):
        string = "I think . this should clean all ? of the ! punctuation"
        new_string = clean_punctuation(string)
        target = "I think   this should clean all   of the   punctuation"
        self.assertEqual(new_string, target)

    def test_len_result(self):
        results = query_elasticsearch("Sheriff")
        result = results.results.pop()
        self.assertTrue(len(result.headline) > 0)

    def test_get_corpus_counts(self):
        grams = get_corpus_counts("1")
        self.assertTrue(len(grams.keys()) > 0)

    def test_entity_cleaning(self):
        entity = "Gov. Bobby Jindal"
        entity = clean_titles(entity)
        self.assertEqual(entity, "Bobby Jindal")

    def test_windower(self):
        doc = "hello my name is mitch landrieu i am the mayor of new orleans"
        tokens = doc.split(" ")
        ner = "mitch lanrieu"
        get_window(tokens, ner, 3)


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
