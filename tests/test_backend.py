import unittest
from webapp.models import get_stuff_ui_needs, Parameters

class TestStringMethods(unittest.TestCase):


  def test_nonsense(self):
      def params():
          p = Parameters()
          p.q = "sdkl.ietmvrslektuvmsldv"
          p.corpus = "lens"
          return p
      self.assertEqual(get_stuff_ui_needs(params())["corpus"], 'lens')

if __name__ == '__main__':
    unittest.main()