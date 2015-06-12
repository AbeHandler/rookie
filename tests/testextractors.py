import unittest
from rookie.utils import POS_tag
from rookie.datamanagement.lensloader import extract_article_entities


class GenericTestCase(unittest.TestCase):

    def test_extrat_article_entities(self):
        sentence = "Professor James Duncan teaches at the Univerisity of Utah"
        entities = extract_article_entities([sentence])
        self.assertEqual("n", wn_tag)

    def test_POS_tag(self):
        tags = POS_tag("Hello operator, please give me number nine")
        self.assertEqual(tags[1][1], "NN")  # operator is noun in PENN tbank

if __name__ == '__main__':
    unittest.main()
