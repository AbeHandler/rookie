import unittest
from rookie.datamanagement.lensloader import extract_article_entities
from rookie.datamanagement.lensloader import merge_sentence_entities

import pdb


class GenericTestCase(unittest.TestCase):

    def test_extract_article_entities(self):
        s1 = "Professor James Duncan teaches at the Univerisity of Utah"
        s2 = "The University of Utah is located in Salt Lake City, Utah"
        s3 = "."
        sentence_entities = extract_article_entities([s1, s2, s3])
        merged = merge_sentence_entities(sentence_entities)
        self.assertEqual(merged['PERSON'].pop(), "James Duncan")

if __name__ == '__main__':
    unittest.main()
