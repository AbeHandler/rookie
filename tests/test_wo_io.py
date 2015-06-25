import unittest

from rookie.scripts.windower import get_window
from rookie.utils import clean_punctuation


class GenericTestCase(unittest.TestCase):

    def test_clean_punctuation(self):
        string = "I think . this should clean all ? of the ! punctuation"
        new_string = clean_punctuation(string)
        target = "I think   this should clean all   of the   punctuation"
        self.assertEqual(new_string, target)

    def test_windower(self):
        doc = "hello my name is mitch landrieu i am the mayor of new orleans"
        tokens = doc.split(" ")
        ner = "mitch landrieu"
        window = get_window(tokens, ner, 2)
        target = ["name", "is", "i", "am"]
        self.assertEqual(target, window)

    def test_windower_edges(self):
        doc = "hello my name is mitch landrieu i am the mayor of new orleans"
        tokens = doc.split(" ")
        ner = "new orleans"
        window = get_window(tokens, ner, 2)
        target = ["mayor", "of"]
        self.assertEqual(target, window)

if __name__ == '__main__':
    unittest.main()
