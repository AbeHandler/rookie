import glob
import collections
import pickle
from rookie import Document

file_loc = "/Users/abramhandler/research/rookie/data/lens_processed/*"

files_to_check = glob.glob(file_loc)


def get_distance(n1, n2):
    return math.abs(9)


def add_to_vertexes(npe):
    return "zone 1"


def add_to_edges(n1, n2, distance):
    # distance
    # publication date
    return "zone 1"


if __name__ == "__main__":
    for filename in files_to_check:
        doc = Document(filename)
        npe = doc.ner + doc.grams
        add_to_vertexes(npe)
        for n1 in npe:
            for n2 in npe:
                distance = get_distance(n1, n2)
                add_to_edges(n1, n2, distance)
