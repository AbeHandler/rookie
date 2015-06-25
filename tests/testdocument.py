import unittest
import glob
import json
import pdb

from rookie.classes import Document

files = glob.glob("/Volumes/USB 1/lens_processed/*")


class GenericTestCase(unittest.TestCase):

    def test_make_document(self):
        fileone = files[0]
        with open("data/sample_wrapper_output.json", "r") as to_read:
            py_wrapper_output = json.loads(to_read.read())
        doc = Document(py_wrapper_output)
        self.assertTrue(len(doc.sentences) > 0)

    def test_find_entities(self):
        fileone = files[0]
        with open("data/sample_wrapper_output_2.json", "r") as to_read:
            py_wrapper_output = json.loads(to_read.read())
        doc = Document(py_wrapper_output)
        ner = doc.sentences[0].ner
        pdb.set_trace()

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
