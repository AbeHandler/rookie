import glob
import json
import pdb
import itertools

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
            counter = counter + 1
            with (open(filename, "r")) as infile:
                data = json.loads(infile.read())['lines']
            doc = Document(data)
            grams = []
            for gram in doc.ngrams:
                grams.append(NPE(gram, gram[0].sentence_no))
            npes = doc.ner + grams
            for npe in npes:
                tmp = repr(npe)
                tmp = unicode_it(tmp)
                add_to_vertexes(npe)
            potential_edges = list(itertools.product(npes, npes))
            print "edges " + str(len(potential_edges))
            edge_counter = 0
            for pe in potential_edges:
                if edge_counter % 1000 == 0:
                    print edge_counter
                edge_counter = edge_counter + 1
                distance = Span(pe[0], pe[1], doc).distance
                if distance > 0:
                    add_to_edges(pe[0], pe[1], distance)
        except KeyError:
            pass
        except TypeError:
            pass
        except UnicodeEncodeError:
            pass
        except ValueError:
            pass
