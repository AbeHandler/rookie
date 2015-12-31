import re,os,json
import datetime
# import ipdb
import itertools
import time
from experiment.classes import Sentence, Document
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc
from experiment.classes import CONNECTION_STRING

start_time = time.time()
engine = create_engine(CONNECTION_STRING)
Session = sessionmaker(bind=engine)
session = Session()
print "[*] building the session took {}".format(start_time - time.time())

def get_q_and_f(docid, q, f):
    #return session.query(Sentence).filter_by(articleid=docid).order_by(Sentence.sentence_no.desc()).limit(2).all()
    return session.query(Sentence).filter_by(articleid=docid).filter(Sentence.text.ilike("%" + q + "%")).filter(Sentence.text.ilike("%" + f + "%")).order_by(Sentence.sentence_no.desc()).limit(2).all()


def get_q_or_f(docid, q, f):
    #return session.query(Sentence).filter_by(articleid=docid).order_by(Sentence.sentence_no.desc()).limit(1).all()
    return session.query(Sentence).filter_by(articleid=docid).filter(Sentence.text.ilike("%" + q + "%") | Sentence.text.ilike("%" + f + "%")).order_by(Sentence.sentence_no.desc()).limit(1).all()


def get_q(docid, q):
    #return session.query(Sentence).filter_by(articleid=docid).order_by(Sentence.sentence_no.desc()).limit(2).all()
    return session.query(Sentence).filter_by(articleid=docid).filter(Sentence.text.ilike("%" + q + "%")).order_by(Sentence.sentence_no.desc()).limit(2).all()
    
    
def get_anything(docid):
    #return session.query(Sentence).filter_by(articleid=docid).order_by(Sentence.sentence_no.desc()).limit(2).all()
    return session.query(Sentence).filter_by(articleid=docid).order_by(Sentence.sentence_no.desc()).limit(2).all()
    

def find_sentences_q(docid, q):
    sentences = []
    sentences = sentences + get_q(docid, q) # try to get 2 sentences containg q
    if len(sentences) == 2:
        return sentences
    if len(sentences) == 2:
        return sentences
    sentences = sentences + get_anything(docid)
    return sentences[0:2]

def find_sentences_q_and_f(docid, q, f):
    sentences = []
    sentences = sentences + get_q_and_f(docid, q, f) # try to get 2 sentences containg q
    if len(sentences) == 2:
        return sentences
    sentences = sentences + get_q_or_f(docid, q, f) # try to get 2 sentences containg q
    if len(sentences) == 2:
        return sentences
    sentences = sentences + get_anything(docid)
    return sentences[0:2]


def get_snippet_pg(docid, q, f=None):
    if f is not None:
        sentences = find_sentences_q_and_f(docid, q, f)
    if f is None:
        sentences = find_sentences_q(docid, q)
    assert len(sentences) == 2
    # sentences = comress_sentences(sentences)
    # sentences.sort(key=lambda x:x.sentence_no)
    sentences.sort(key=lambda x:x.sentence_no)
    return sentences

def get_snippet2(docid, q, f=None):
    pass

def hilite_hack(text, q, f_aliases=None):
    import termcolor
    qsub = r'|Q> \1 <Q|'
    qsub = termcolor.colored(qsub, 'blue',attrs=['bold'])
    fsub = r'|F> \1 <F|'
    fsub = termcolor.colored(fsub, 'red', attrs=['bold'])

    text1 = text

    f_aliases = sorted(f_aliases, key=lambda f: (-len(f), f))
    fregex = "(" + "|".join(re.escape(f) for f in f_aliases) + ")"
    text2 = re.sub(fregex, fsub, text1, flags=re.I)
    has_f = text2 != text1

    qregex = "(" + re.escape(q) + ")"
    text3 = re.sub(qregex, qsub, text2, flags=re.I)
    has_q = text3 != text2

    return dict(has_q=has_q, has_f=has_f, htext=text3)


## below is only for offline development

class FakeParams(dict):
    def __getattr__(self, name):
        return self[name]

def runq(q):
    # adapted from app.py:medviz() and get_doc_list()
    # need the Q query to populate the alias tables
    # in app.py this is done with a global state object. this is why i had the
    # bug when trying to work with get_doc_list directly.
    from experiment.models import Models
    params = FakeParams(q=q)
    q_docids = Models.get_results(params)
    facets,aliases = Models.get_facets(params, q_docids)
    print "QUERY",q
    print "FACETS",facets
    print "%s q docs" % len(q_docids)

    for f in facets:
        runf(q,f,q_docids,aliases[f])

def runf(q,f,q_docids,aliases):
    from experiment.models import get_doc_metadata, Models
    aliases = set([f] + list(aliases))

    print 
    f_docids = Models.f_occurs_filter(q_docids, facet=f, aliases=aliases)
    print
    print "-----------------------------------------"
    print "Q = %-15s\tF = %-30s has %d docids" % (q,f, len(f_docids))
    print "ALIASES", aliases

    for docid in f_docids[:5]:
        d = get_doc_metadata(docid)
        print
        print "== doc%s\t%s\t%s" % (docid, d['pubdate'], d.get('headline',""))
        print "   DOC&FA: ", sorted(set(d['ngram']) & set(aliases))
        snippet = get_snippet_pg(docid, q=q, f=f)
        hsents = [hilite_hack(sent.text, q=q, f_aliases=aliases) for sent in snippet]
        for sent,h in zip(snippet,hsents):
            print "  s%s\tq=%d f=%d\t%s" % (sent.sentence_no, h['has_q'], h['has_f'], h['htext'])
    # doc_list = mm.Models.get_doclist(results, params, 10)

# if __name__=='__main__':
#     import sys
#     analyze(sys.argv[1])
