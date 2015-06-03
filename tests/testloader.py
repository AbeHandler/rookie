import unittest
from rookie.utils import get_node_degrees
from rookie.utils import query_elasticsearch
from rookie.utils import Result


class GenericTestCase(unittest.TestCase):

    def test_query_wrapper(self):
        results = query_elasticsearch("OPSB")
        dummylist = []
        self.assertEqual(type(results), type(dummylist))

if __name__ == '__main__':
    unittest.main()
