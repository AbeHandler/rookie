import unittest

from rookie.utils import clean_punctuation


class GenericTestCase(unittest.TestCase):

    def test_clean_punctuation(self):
        string = "I think . this should clean all ? of the ! punctuation"
        new_string = clean_punctuation(string)
        target = "I think   this should clean all   of the   punctuation"
        self.assertEqual(new_string, target)

if __name__ == '__main__':
    unittest.main()
