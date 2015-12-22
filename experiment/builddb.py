'''
This module loads documents into whoosh and creates a sentence index
'''
import glob
import ipdb
import datetime
from rookie import processed_location
from experiment.classes import Document, Facet, Sentence, DocumentFacet
from rookie.classes import IncomingFile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from experiment.classes import CONNECTION_STRING


def build(processed_location):
    '''
    Loop thru corpus and build a db
    '''
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

if __name__ == '__main__':
    engine = create_engine(CONNECTION_STRING)
    Session = sessionmaker(bind=engine)
    session = Session()
    build(processed_location)
    session.commit()
