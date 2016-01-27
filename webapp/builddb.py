'''
This module loads documents into whoosh and creates a sentence index
'''
import glob,time,sys
import ujson
import pickle
import ipdb
import datetime
import argparse
import dateutil.parser

#TODO : ini file not hardcoded


from webapp.classes import Document, Facet, Sentence, DocumentFacet
from webapp.classes import IncomingFile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from webapp.classes import CONNECTION_STRING

parser = argparse.ArgumentParser()
parser.add_argument('--corpus', help='the thing in the middle of corpus/{}/raw', required=True)
args = parser.parse_args()

def doc_metadata_to_db():
    print "building per-doc metadata table now handled in load_to_whoosh 1.27.16"
    
    '''
    go = lambda *args: session.connection().execute(*args)
    go("drop table if exists doc_metadata")
    go("create table doc_metadata (docid integer not null primary key, data jsonb)")

    mt = ujson.load(open("indexes/{}/meta_data.json".format(args.corpus)))
    print len(mt), "docs in metadata json"
    docids = mt.keys()
    docids = [int(i) for i in docids]
    docids.sort()
    for docid in docids:
        go("""INSERT INTO doc_metadata (docid, data) VALUES (%s, %s)""", 
            docid, ujson.dumps(mt[str(docid)]))
    print "Num docs in metadata table:", go("select count(1) from doc_metadata").fetchone()[0]
    '''

def create_pubdate_index():
    '''
    go = lambda *args: session.connection().execute(*args)

    print "building pubdate index"
    go("drop table if exists ngram_pubdates")
    go("create table ngram_pubdates (ngram text, pubdates jsonb)")
    # string to pubdate matrix created in building matrix
    with open("indexes/lens/string_to_pubdate_index.p") as inf: #TODO: lens hardcoded
        metadata = pickle.load(inf)
    for i,ngram in enumerate(metadata):
        dates = metadata[ngram]
        dates = sorted(set(dates))
        go(u"""INSERT INTO ngram_pubdates (ngram, pubdates) VALUES (%s, %s)""",
                ngram, ujson.dumps(dates))
        
    print "\nindexing"
    go("create index on ngram_pubdates (ngram)")
    print "pubdate index built over %s terms" % (go("select count(1) from ngram_pubdates").fetchone()[0])
    '''

if __name__ == '__main__':
    engine = create_engine(CONNECTION_STRING)
    Session = sessionmaker(bind=engine)
    session = Session()

    #build(processed_location)
    doc_metadata_to_db()
    create_pubdate_index()

    session.commit()
