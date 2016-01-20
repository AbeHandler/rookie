'''
This module loads documents into whoosh and creates a sentence index
'''
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
from whoosh import writing
from rookie.classes import IncomingFile
from collections import defaultdict
from rookie import processed_location
import ipdb
import os
import json
import glob
from dateutil.parser import parse


def load(index_location, processed_location):
    '''
    Load documents from procesed location into whoosh @ index_location
    '''

    s_counter = 0 # only increments when doc actually added to whoosh
    # w/o this kludge, doc ids cause index errors b/c loop counter higher b/c ~15 docs error on load

    schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT)
    ix = create_in(index_location, schema)
    writer = ix.writer()

    people_org_ngram_index = {}

    #this index stores when a string appears in publication
    string_to_pubdate_index = defaultdict(list)

    files_to_check = glob.glob(processed_location + "/*")

    for infile in files_to_check:
        try:
            full_text = IncomingFile(infile).doc.full_text
            headline = unicode(IncomingFile(infile).headline)
            meta_data = {}
            meta_data['people'] = [unicode(str(i)) for i in IncomingFile(infile).doc.people]
            meta_data['org'] = [unicode(str(i)) for i in IncomingFile(infile).doc.organizations]
            meta_data['ngram'] = [unicode(" ".join(i.raw for i in j)) \
                                  for j in IncomingFile(infile).doc.ngrams]
            meta_data['headline'] = IncomingFile(infile).headline
            meta_data['url'] = IncomingFile(infile).url
            meta_data['pubdate'] = IncomingFile(infile).pubdate
            meta_data['raw'] = os.path.split(infile)[1]
            meta_data['facet_index'] = defaultdict(list)
            sentences = [" ".join([j.raw for j in i.tokens]) \
                         for i in IncomingFile(infile).doc.sentences]
            meta_data['facet_index'] = dict(meta_data['facet_index'])
            meta_data['sentences'] = sentences
            meta_data['pubdate'] = IncomingFile(infile).pubdate
            # NOTE:
            # pubdate_index is set in facets/build_matrix.py
            # NOTE: only adding articles after 2010
            if len(headline) > 0 and len(full_text) > 0 and parse(meta_data['pubdate']).year >= 2010:
                writer.add_document(title=headline, path=u"/" + str(s_counter), content=full_text)
                people_org_ngram_index[s_counter] = meta_data
                s_counter += 1
                print s_counter
        except AttributeError:
            print "error"

    writer.commit(mergetype=writing.CLEAR)

    with open(index_location + '/meta_data.json', 'w') as outfile:
        json.dump(people_org_ngram_index, outfile)
    with open(index_location + '/string_to_pubdate.json', 'w') as outfile:
        json.dump(dict(string_to_pubdate_index), outfile)

if __name__ == '__main__':
    load("rookieindex", processed_location)
