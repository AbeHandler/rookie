import glob
import json
import pdb
import csv
import itertools
import datetime
from rookie.classes import Document
from rookie.classes import NPE
from rookie import processed_location

file_loc = processed_location

files_to_check = glob.glob(file_loc + "/*")

counter = 0

if __name__ == "__main__":
    for filename in files_to_check:
        try:
            counter = counter + 1
            with (open(filename, "r")) as infile:
                json_in = json.loads(infile.read())
                url = json_in['url']
                pubdate = json_in['timestamp']
                data = json_in['lines']
            doc = Document(data)
            sentences = doc.sentences
            sentence_counter = 0
            for sentence in sentences:
                # print datetime.datetime.now()
                sentence_counter = sentence_counter + 1
                # print str(sentence_counter) + " of " + str(len(sentences))
                grams = []
                bigrams = sentence.bigrams
                trigrams = sentence.trigrams
                ner = sentence.ner
                for gram in bigrams:
                    grams.append(NPE(gram, gram[0].sentence_no))
                for gram in trigrams:
                    grams.append(NPE(gram, gram[0].sentence_no))
                npes = grams + ner
                potential_edges = list(itertools.product(npes, npes))
                for pe in potential_edges:
                    with open('graph.csv', 'a') as csvfile:
                        writer = csv.writer(csvfile, delimiter=',',
                                            quotechar='"',
                                            quoting=csv.QUOTE_MINIMAL)
                        writer.writerow([i for i in pe] + [url, pubdate])
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
