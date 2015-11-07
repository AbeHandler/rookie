from whoosh.index import create_in
from whoosh.fields import *
from whoosh import writing
from rookie.classes import IncomingFile
from rookie import processed_location
import pdb
import json
import glob

schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT, people=KEYWORD, organizations=KEYWORD)
ix = create_in("rookieindex", schema)
writer = ix.writer()

people_org_ngram_index = {}

files_to_check = glob.glob(processed_location + "/*")

for counter, infile in enumerate(files_to_check):
    try:
        if counter % 100 == 0:
            print counter
        full_text = IncomingFile(infile).doc.full_text
        headline = unicode(IncomingFile(infile).headline)
        people = u"|||".join([unicode(str(i)) for i in IncomingFile(infile).doc.people])
        orgs = u"|||".join([unicode(str(i)) for i in IncomingFile(infile).doc.organizations])
        ngrams = u"|||".join([unicode(" ".join(i.raw for i in j)) for j in IncomingFile(infile).doc.ngrams])
        meta_data = {}
        meta_data['people'] = [unicode(str(i)) for i in IncomingFile(infile).doc.people]
        meta_data['org'] = [unicode(str(i)) for i in IncomingFile(infile).doc.organizations]
        meta_data['ngram'] = [unicode(" ".join(i.raw for i in j)) for j in IncomingFile(infile).doc.ngrams]
        sentences = [" ".join([j.raw for j in i.tokens]) for i in IncomingFile(infile).doc.sentences]
        meta_data['sentences'] = sentences
        with open("articles/{}".format(counter), "w") as outfile:
            outfile.write(full_text.encode("ascii", "ignore"))
        meta_data['pubdate'] = IncomingFile(infile).pubdate
        people_org_ngram_index[counter] = meta_data
        if len(headline) > 0 and len(full_text) > 0:
            writer.add_document(title=headline, path=u"/" + str(counter), content=full_text, people=people, organizations=orgs)
    except AttributeError:
        print "error"

writer.commit(mergetype=writing.CLEAR)

with open('data/meta_data.json', 'w') as outfile:
    json.dump(people_org_ngram_index, outfile)