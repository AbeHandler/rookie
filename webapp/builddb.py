'''
This module loads documents into whoosh and creates a sentence index
'''
import glob,time,sys
import ujson
import pickle
import ipdb
import datetime
import dateutil.parser
from rookie import processed_location
from experiment.classes import Document, Facet, Sentence, DocumentFacet
from rookie.classes import IncomingFile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from experiment.classes import CONNECTION_STRING

'''
def build(processed_location):
I THINK DEAD CODE
    files_to_check = glob.glob(processed_location + "/*")

    facetcounter = 0
    for counter, infile in enumerate(files_to_check):
        try:
            if counter % 100 == 0:
                print counter
            full_text = IncomingFile(infile).doc.full_text
            headline = unicode(IncomingFile(infile).headline).encode("ascii", "ignore")
            pubdate = IncomingFile(infile).pubdate
            ed_user = Document(pubdate=pubdate, headline=headline, docid=counter)
            session.add(ed_user)
            session.flush()
            for s_index, sentence in enumerate(IncomingFile(infile).doc.sentences):
                s_db = Sentence(str(sentence), counter, s_index)
                session.add(s_db)
                for ne in sentence.ner:
                    facet = Facet(str(ne).decode("ascii", "ignore"), facetcounter)
                    docfacet = DocumentFacet(counter, facetcounter)
                    session.add(facet)
                    session.flush()
                    session.add(docfacet)
                    session.flush()
                    facetcounter += 1
                for ng in sentence.ngrams:
                    facet = Facet(" ".join([i.raw.encode("ascii", "ignore") for i in ng]), facetcounter)
                    docfacet = DocumentFacet(counter, facetcounter)
                    session.add(facet)
                    session.flush()
                    session.add(docfacet)
                    session.flush()
                    facetcounter += 1

        except AttributeError:
            print "error"
'''

def doc_metadata_to_db():
    print "building per-doc metadata table"
    go = lambda *args: session.connection().execute(*args)
    go("drop table if exists doc_metadata")
    go("create table doc_metadata (docid integer not null primary key, data jsonb)")

    mt = ujson.load(open("rookieindex/meta_data.json"))
    print len(mt), "docs in metadata json"
    docids = mt.keys()
    docids = [int(i) for i in docids]
    docids.sort()
    for docid in docids:
        print docid
        go("""INSERT INTO doc_metadata (docid, data) VALUES (%s, %s)""", 
            docid, ujson.dumps(mt[str(docid)]))
    print "Num docs in metadata table:", go("select count(1) from doc_metadata").fetchone()[0]

def create_pubdate_index():
    go = lambda *args: session.connection().execute(*args)

    print "building pubdate index"
    go("drop table if exists ngram_pubdates")
    go("create table ngram_pubdates (ngram text, pubdates jsonb)")
    # string to pubdate matrix created in building matrix
    with open("rookieindex/string_to_pubdate_index.p") as inf:
        metadata = pickle.load(inf)
    for i,ngram in enumerate(metadata):
        if i % 1000==0:
            sys.stdout.write("...%s" % i); sys.stdout.flush()
        dates = metadata[ngram]
        dates = sorted(set(dates))
        go(u"""INSERT INTO ngram_pubdates (ngram, pubdates) VALUES (%s, %s)""",
                ngram, ujson.dumps(dates))
        
    print "\nindexing"
    go("create index on ngram_pubdates (ngram)")
    print "pubdate index built over %s terms" % (go("select count(1) from ngram_pubdates").fetchone()[0])

if __name__ == '__main__':
    engine = create_engine(CONNECTION_STRING)
    Session = sessionmaker(bind=engine)
    session = Session()

    #build(processed_location)
    doc_metadata_to_db()
    create_pubdate_index()

    session.commit()
