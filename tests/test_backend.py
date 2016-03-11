import unittest
import ipdb
from webapp.models import get_stuff_ui_needs, Parameters, get_doc_metadata

class TestStringMethods(unittest.TestCase):


  def test_nonsense(self):
      def params():
          p = Parameters()
          p.q = "sdkl.ietmvrslektuvmsldv"
          p.corpus = "lens"
          return p
      self.assertEqual(get_stuff_ui_needs(params())["corpus"], 'lens')

  def test_get_doc_metadata(self):
      md = get_doc_metadata(5, "lens")
      self.assertTrue("as_tokens" in md["sentences"][0].keys())

if __name__ == '__main__':
    unittest.main()
