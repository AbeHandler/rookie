from whoosh.index import create_in
from whoosh.fields import *
from whoosh import writing
from rookie.classes import IncomingFile
from rookie import processed_location
import pdb
import glob

schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT, people=KEYWORD, organizations=KEYWORD)
ix = create_in("indexdir", schema)
writer = ix.writer()


files_to_check = glob.glob(processed_location + "/*")

for counter, infile in enumerate(files_to_check):
    try:
        print counter
        full_text = IncomingFile(infile).doc.full_text
        headline = unicode(IncomingFile(infile).headline)
        people = [unicode(str(i)) for i in IncomingFile(infile).doc.people]
        orgs = [unicode(str(i)) for i in IncomingFile(infile).doc.organizations]
        ngrams = [unicode(str(i)) for i in IncomingFile(infile).doc.organizations]
        if len(headline) > 0 and len(full_text) > 0:
            writer.add_document(title=headline, path=u"/" + str(counter), content=full_text, people=people, organizations=orgs)
    except AttributeError:
        pass


writer.commit(mergetype=writing.CLEAR)
