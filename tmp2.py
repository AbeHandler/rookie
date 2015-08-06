import pickle
import glob
import pdb
import math
import networkx as nx
from collections import defaultdict
from rookie.classes import IncomingFile, Gramner, N_Grammer
from rookie.compressor import sentence_to_graph, show_graph
from networkx.algorithms.traversal.depth_first_search import dfs_tree

apposez = defaultdict(list)
grams_document_frequencies = defaultdict(int)

to_run = glob.glob("data/lens_processed/*")

counter = 0

stop_words = ["members", "board", "board members", "Members", "Board", "Board members"]


def caclulate_df(dictionary, N):
    output = {}
    for key in dictionary.keys():
        count = dictionary[key]
        output[key] = math.log(float(N) / float(count))
    return output


for f in to_run:
    counter += 1
    if counter % 10 == 0:
        print counter
    infile = IncomingFile(f)
    try:
        people = infile.doc.people
    except:
        people = []
    try:
        first_mentions = [str(g[0]) for g in infile.doc.coreferences.groups]
    except:
        first_mentions = []
    for person in people:
        if repr(person) in first_mentions:
            # magic number 5 => five token span
            sentence_tokens = infile.doc.sentences[person.sentence_no].tokens
            g = sentence_to_graph(infile.doc.sentences[person.sentence_no])
            deps = nx.get_edge_attributes(g, 'r')
            for token in person.tokens:
                for e in g.out_edges(token.token_no):
                    if deps[e] == "appos":
                        subtree = dfs_tree(g, e[1])
                        appos = ""
                        nodes = subtree.nodes()
                        nodes.sort()
                        for node in nodes:
                            appos = appos + sentence_tokens[node].raw + " "
                        apposez[str(person)].append(appos.strip())

pickle.dump(apposez, open("pickled/people_windows.p", "w"))
