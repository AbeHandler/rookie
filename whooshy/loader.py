'''
This module loads documents into whoosh and creates a sentence index
'''
from whoosh.index import create_in
from whoosh.fields import *
from whoosh import writing
from rookie.classes import IncomingFile
from collections import defaultdict
from rookie import processed_location
import pdb
import itertools
import os
import json
import glob

def load(index_location, processed_location):
    schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT, people=KEYWORD, organizations=KEYWORD)
    ix = create_in(index_location, schema)
    writer = ix.writer()

    people_org_ngram_index = {}

    #this index stores when a string appears in publication
    string_to_pubdate_index = defaultdict(list)

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
            meta_data['headline'] = IncomingFile(infile).headline
            meta_data['url'] = IncomingFile(infile).url
            meta_data['pubdate'] = IncomingFile(infile).pubdate
            path, fn = os.path.split(infile)
            meta_data['raw'] = fn
            meta_data['facet_index'] = defaultdict(list)
            sentences = [" ".join([j.raw for j in i.tokens]) for i in IncomingFile(infile).doc.sentences]
            print counter
            for s_index, sentence in enumerate(IncomingFile(infile).doc.sentences):
                for ne in sentence.ner:
                    meta_data['facet_index'][str(ne).decode("ascii", "ignore")].append(s_index)
                    string_to_pubdate_index[str(ne)].append(IncomingFile(infile).pubdate)
                for ng in sentence.ngrams:
                    tmp = " ".join([i.raw.encode("ascii", "ignore") for i in ng])
                    meta_data['facet_index'][tmp].append(s_index)
                    meta_data['facet_index'][tmp] = list(set(meta_data['facet_index'][tmp]))
                    string_to_pubdate_index[tmp].append(IncomingFile(infile).pubdate)
            meta_data['facet_index'] = dict(meta_data['facet_index'])
            meta_data['sentences'] = sentences
            tokens = itertools.chain(*[[j.raw for j in i.tokens] for i in IncomingFile(infile).doc.sentences])
            with open('articles/{}'.format(counter), 'w') as outfile:
                tokens = [i.encode("ascii", "ignore") for i in tokens]
                toks = {}
                for index, i in enumerate(tokens):
                    toks[index] = i
                json.dump(toks, outfile)
            meta_data['pubdate'] = IncomingFile(infile).pubdate
            people_org_ngram_index[counter] = meta_data
            if len(headline) > 0 and len(full_text) > 0:
                writer.add_document(title=headline, path=u"/" + str(counter), content=full_text, people=people, organizations=orgs)
        except AttributeError:
            print "error"

    writer.commit(mergetype=writing.CLEAR)

    with open(index_location + '/meta_data.json', 'w') as outfile:
        json.dump(people_org_ngram_index, outfile)
    with open(index_location + '/string_to_pubdate.json', 'w') as outfile:
        json.dump(dict(string_to_pubdate_index), outfile)

if __name__ == '__main__':
    load("rookieindex", processed_location)
