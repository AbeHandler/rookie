import unittest
import pdb
from rookie.simplemerger import Merger
from collections import Counter


class GenericTestCase(unittest.TestCase):

    def test_make_document(self):
        counter = Counter(['Mitch Landrieu', 'Mitch Landrieus'])
        counter = [(k, v) for k, v in counter.items()]
        pdb.set_trace()
        merge = Merger().merge_lists(counter)
        self.assertEqual(merge[0], "Mitch Landrieus")


if __name__ == '__main__':
    unittest.main()
