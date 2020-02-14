'''
This module loads documents into whoosh and creates a sentence index
'''
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
from whoosh import writing
from collections import defaultdict
import csv
import os
import ipdb
import sys
import re
csv.field_size_limit(sys.maxsize)
import ujson
import argparse
from dateutil.parser import parse


'''build connection to db'''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from webapp import CONNECTION_STRING
engine = create_engine(CONNECTION_STRING)
Session = sessionmaker(bind=engine)
session = Session()


def getcorpusid():
    go = lambda *args: session.connection().execute(*args)
    for i in go("select corpusid from corpora where corpusname='{}'".format(args.corpus)):
        return i[0]


def stop_word(w):
    return False # TODO: corpus specific stop words


def load(index_location, processed_location):
    '''
    Load documents from procesed location into whoosh @ index_location
    '''

    s_counter = 0 # only increments when doc actually added to whoosh
    # w/o this kludge, doc ids cause index errors b/c loop counter higher b/c ~15 docs error on load

    schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT)
    ix = create_in(index_location, schema)
    writer = ix.writer()

    ngram_pubdate_index = defaultdict(list)

    headlines_so_far = set() # eliminate dupes. eventually fancier methods?
    go = lambda *args: session.connection().execute(*args)
    go('delete from doc_metadata where corpusid={}'.format(CORPUSID))
    go('delete from sentences_preproc where corpusid={}'.format(CORPUSID))
    session.commit()
    with open("corpora/{}/processed/all.anno_plus".format(args.corpus), "r") as raw:
        for ln, line in enumerate(raw):
            # print ln
            try:
                # ipdb.set_trace()
                line_json = ujson.loads(line.replace("\n", ""))
                try:
                    headline = line_json["headline"]
                except KeyError:
                    headline = "Headline: NA"
                
                
                try:
                    pubdate = parse(line_json["pubdate"])

                except ValueError: # sometimes throws typerror, other times value error. huh?
                    # nyt world news date format = 19870101_0000087
                    nytdate = re.match("[0-9]{8}(?=_)", line_json["pubdate"]).group(0)
                    assert len(nytdate) == 8
                    pubdate = parse(nytdate)
                except TypeError: 
                    # nyt world news date format = 19870101_0000087
                    nytdate = re.match("[0-9]{8}(?=_)", line_json["pubdate"]).group(0)
                    assert len(nytdate) == 8
                    pubdate = parse(nytdate)

                try:
                    url = line_json["url"]
                except KeyError:
                    url = "unknown"

                full_text = " ".join(t for s in line_json["text"]["sentences"]
                                     for t in s["tokens"])
                ngrams = []
                for sent in line_json["text"]["sentences"]:
                    ngrams = ngrams + [o["regular"] for o in sent["phrases"]]

                ngrams = filter(lambda x: len(x.split()) > 1, ngrams)
      
                sentences = line_json["text"]["sentences"]
                preprocsentences = "###$$$###".join([sen["as_string"] for sen
                                                     in line_json["text"]["sentences"]])


                if len(headline) > 0 and len(full_text) > 0 and headline not in headlines_so_far:
                    headlines_so_far.add(headline)
                    writer.add_document(title=headline, path=u"/" + str(s_counter),
                                        content=full_text)
                    per_doc_json_blob = {'headline': headline,
                                        'pubdate': pubdate.strftime('%Y-%m-%d'),
                                        'ngrams': ngrams,
                                        "url": url,
                                        "sentences": sentences}
                    go("""INSERT INTO doc_metadata (docid, data, corpusid) VALUES (%s, %s, %s)""", s_counter, ujson.dumps(per_doc_json_blob), CORPUSID)
                    go("""INSERT INTO sentences_preproc (corpusid, docid, delmited_sentences) VALUES (%s, %s, %s)""", CORPUSID, s_counter, preprocsentences)
                    for ngram in ngrams:
                        ngram_pubdate_index[ngram].append(pubdate.strftime('%Y-%m-%d'))
                    s_counter += 1
                    if s_counter % 1000==0:
                        sys.stdout.write("...%s" % s_counter); sys.stdout.flush()
            except UnicodeError:
                pass
        # create_pubdate_index(ngram_pubdate_index)
        #print "Committing to whoosh"
        writer.commit(mergetype=writing.CLEAR)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--corpus', help='the thing in the middle of corpus/{}/raw', required=True)
    args = parser.parse_args()

    CORPUSID = getcorpusid()

    print "adding {} to whoosh and checking ngrams".format(args.corpus)

    directory = "indexes/" + args.corpus
    if not os.path.exists(directory):
        os.makedirs(directory)
    load(directory, args.corpus)
    session.commit()
