from __future__ import division
import pdb
import pickle
import os
import json
import numpy as np
from dateutil import parser
import pdb
from pylru import lrudecorator
from collections import Counter
from collections import defaultdict
from experiment.models import Models, Parameters
from snippets.utils import flip
from snippets import log
from whoosh.index import create_in
from whoosh.qparser import QueryParser
from whoosh.fields import *
from whoosh import writing


def get_snippet(term, termtype, sentences, original_query):

    # NOTE. this is 2x loose on aliasiing/coreference. if there is enuf intersection, sentence gets
    # bumped up. so there is round 1 of aliasing. then this.

    for directory in ["coastal", "jindal"]:
        if not os.path.exists(directory):
            os.makedirs(directory)
    schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT, date=DATETIME)
    coastal_index = create_in("coastal", schema)
    jindal_index = create_in("jindal", schema)
    ci_writer = coastal_index.writer(mergetype=writing.CLEAR)
    jindal_writer = jindal_index.writer(mergetype=writing.CLEAR)
    sentences_dict = {}
    q = set([i.lower() for i in original_query.split(" ")])
    t = set([i.lower() for i in term.split(" ")])
    for index, sentence in enumerate(sentences):
        pubdate = sentence[1]
        doc_path = sentence[2]
        sentence_set = set([i.lower() for i in sentence[0].split(" ")])
        if len(t.intersection(sentence_set))/(len(t)) >= .5:
            sentence_path = u"{}-{}".format(doc_path, index)
            jindal_writer.add_document(title=sentence_path, path=u"/" + sentence_path, content=sentence[0], date=pubdate)
            sentences_dict[sentence_path] = (sentence[0], parser.parse(pubdate), doc_path, term)
            # if len(q.intersection(sentence_set)) >= .5 * (len(q)):
            #    sentence = unicode(sentence)
            #    ci_writer.add_document(title=unicode(str(docno) + "-" + str(sentenceno)), path=u"/" + str(docno) + "-" + str(sentenceno), content=sentence, date=pubdate)
            #    sentences_dict[unicode(str(docno) + "-" + str(sentenceno))] = (sentence, parser.parse(pubdate))
            #    print "adding q"

    ci_writer.commit()
    jindal_writer.commit()

    final = []

    with jindal_index.searcher() as searcher:
        qp = QueryParser("content", jindal_index.schema)
        myquery = qp.parse(original_query)
        results = searcher.search(myquery, limit=None) #TODO potential bug
        for i in results:
            final.append(sentences_dict[i['title']])

#    with coastal_index.searcher() as searcher:
#        qp = QueryParser("content", coastal_index.schema)
#        myquery = qp.parse(original_query)
#        results = searcher.search(myquery)
#        for i in results[0:5]:
#            final.append(sentences_dict[i['title']])
    final = [o for o in set(final)]
    final.sort(key=lambda x: x[1])
    
    final = [(f[0].split(" "), f[1], f[2], f[3]) for f in final] # TODO deal w/ tokenization for real
    return final

