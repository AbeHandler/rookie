import unittest
import os
import hashlib
from rookie import corpus_loc
from rookie.datamanagement.lensdownloader import get_page


class GenericTestCase(unittest.TestCase):

    def test_downloader_creates_file(self):
        url = "http://thelensnola.org/2015/06/11/judge-delays-city-from-seizing-long-vacant-lake-terrace-shopping-center/"
        hash_url = hashlib.sha224(url).hexdigest()
        file_location = corpus_loc + hash_url
        try:
            os.remove(file_location)
        except OSError:
            pass
        self.assertEqual(os.path.exists(file_location), False)
        page = get_page(url)
        page = get_page(url)
        self.assertEqual(os.path.exists(file_location), True)
        self.assertEqual(page, page)


    def test_downloader_equal_file(self):
        url = "http://thelensnola.org/2015/06/11/judge-delays-city-from-seizing-long-vacant-lake-terrace-shopping-center/"
        hash_url = hashlib.sha224(url).hexdigest()
        file_location = corpus_loc + hash_url
        try:
            os.remove(file_location)
        except OSError:
            pass
        page = get_page(url)
        page = get_page(url)
        self.assertEqual(page, page)

if __name__ == '__main__':
    unittest.main()
