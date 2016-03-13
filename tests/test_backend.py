import unittest
import ipdb
from webapp.models import query, get_stuff_ui_needs, Parameters, get_doc_metadata, Models

def get_params():
    p = Parameters()
    p.q = "sdkl.ietmvrslektuvmsldv"
    p.corpus = "lens"
    return p

class TestStringMethods(unittest.TestCase):

  def test_nonsense(self):
      self.assertEqual(get_stuff_ui_needs(get_params())["corpus"], 'lens')

  def test_get_sent(self):
      p = get_params()
      p.q = "Mitch Landrieu"
      p.f = "City Hall"
      results = query("Mitch Landrieu", "lens")
      print Models.get_sent_list(results, p.q, p.f, "lens")

  def test_get_doc_metadata(self):
      md = get_doc_metadata(5, "lens")
      self.assertTrue("as_tokens" in md["sentences"][0].keys())

if __name__ == '__main__':
    unittest.main()
