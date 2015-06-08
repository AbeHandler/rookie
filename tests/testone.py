import unittest
from rookie.utils import get_node_degrees
from rookie.utils import query_elasticsearch
from rookie.utils import Result


class GenericTestCase(unittest.TestCase):

    def test_query_wrapper(self):
        results = query_elasticsearch("OPSB")
        dummylist = []
        self.assertEqual(type(results), type(dummylist))

    def test_len_result(self):
        results = query_elasticsearch("OPSB")
        result = results.pop()
        self.assertTrue(len(result.headline) > 0)

    def test_links(self):
        results = query_elasticsearch("OPSB")
        result = results.pop()
        dummylist = []
        self.assertTrue(type(result.links), dummylist)

    def test_node_degrees(self):
        results = query_elasticsearch("OPSB")
        degrees = get_node_degrees(results)
        self.assertTrue(1 == 1)

    def test_node_degrees(self):
        results = query_elasticsearch("OPSB")
        result = results.pop()
        self.assertTrue(len(result.entities.keys()) > 0)

if __name__ == '__main__':
    unittest.main()
