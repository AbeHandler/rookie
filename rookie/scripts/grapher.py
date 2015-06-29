import glob
import collections
import pickle
from rookie import Document

file_loc = "/Users/abramhandler/research/rookie/data/lens_processed/*"

files_to_check = glob.glob(file_loc)

if __name__ == "__main__":
    for filename in files_to_check:
        doc = Document(filename)