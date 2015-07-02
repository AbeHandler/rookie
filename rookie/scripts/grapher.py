import glob
import json
import pdb
import itertools
import datetime
import csv

from py2neo import Graph, Path
from py2neo import Node, Relationship
from rookie.classes import Document
from rookie.classes import NPE
from rookie.classes import Span

file_loc = "/Users/abramhandler/research/rookie/data/lens_processed/*"

files_to_check = glob.glob(file_loc)

G = Graph()

G.delete_all()

tx = G.cypher.begin()


def add_to_vertexes(node):
    node = repr(node)
    query = "MATCH (person:Person { name:'" + node + "' }) RETURN person"
    records = G.cypher.execute(query).records
    if len(records) == 0:
        new_node = Node("Person", name=node, courpus_count=1)
        G.create(new_node)
    else:
        first = records[0]
        # TODO
        # first[0].properties['courpus_count']
        '''
        # q = "MATCH (person:Person { name:'8' })
        SET person.lastSeen = 'r'  RETURN person"
        '''
        # pdb.set_trace()
        # noo = graph.cypher.execute(query).records
        # pdb.set_trace()
        pass
        # print "already have" + node


def add_to_edges(n1, n2, distance):
    q = 'MATCH (n1:Person {name:"' + repr(n1) + '"}), (n2:Person {name:"' + repr(n2) + '"}) CREATE (n1)-[:WITH{ distance:' + repr(distance) + '}]->(n2)'
    G.cypher.execute(q)


def unicode_it(node):
    return tmp.decode("ascii", "ignore").encode("ascii", "ignore")

counter = 0


if __name__ == "__main__":
    for filename in files_to_check:
        try:
            print counter
            print datetime.datetime.now()
            counter = counter + 1
            with (open(filename, "r")) as infile:
                data = json.loads(infile.read())['lines']
            doc = Document(data)
            sentences = doc.sentences
            sentence_counter = 0
            for sentence in sentences:
                print datetime.datetime.now()
                sentence_counter = sentence_counter + 1
                print str(sentence_counter) + " of " + str(len(sentences))
                grams = []
                bigrams = sentence.bigrams
                trigrams = sentence.trigrams
                ner = sentence.ner
                for gram in bigrams:
                    grams.append(NPE(gram, gram[0].sentence_no))
                for gram in trigrams:
                    grams.append(NPE(gram, gram[0].sentence_no))
                print datetime.datetime.now()
                npes = grams + ner
                for npe in npes:
                    tmp = repr(npe)
                    tmp = unicode_it(tmp)
                    print datetime.datetime.now()
                    #  add_to_vertexes(npe)
                    print datetime.datetime.now()
                potential_edges = list(itertools.product(npes, npes))
                edge_counter = 0
                for pe in potential_edges:
                    edge_counter = edge_counter + 1
                    distance = 1  # just count as one #Span(pe[0], pe[1], doc).distance
                    if distance > 0:
                        print datetime.datetime.now()
                        add_to_edges(pe[0], pe[1], distance)
                        print datetime.datetime.now()
        except KeyError:
            pass
        except KeyError:
            pass
        except TypeError:
            pass
        except ValueError:
            pass
        except UnicodeEncodeError:
            pass
