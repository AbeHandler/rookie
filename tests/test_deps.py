import unittest
import json
import pdb
from rookie.classes import Document
from rookie.utils import compress_sentence


class GenericTestCase(unittest.TestCase):

    def test_compress_sentence(self):
        with open("data/tests/sample.json", "r") as to_read:
            py_wrapper_output = json.loads(to_read.read())
        doc = Document(py_wrapper_output)
        pdb.set_trace()
        for sentence in doc.sentences:
            print [i.raw for i in sentence.tokens]

if __name__ == '__main__':
    unittest.main()
