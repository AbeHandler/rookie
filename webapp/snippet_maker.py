import re
import time
import hashlib
import json
import pickle
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from webapp import CONNECTION_STRING

from pylru import lrudecorator
from queue import PriorityQueue

@lrudecorator(10000)
def load_preproc_sentences(corpus):
    with open("db/{}.sentences_preproc.json".format(corpus), "r") as inf:
        return json.load(inf)

@lrudecorator(10000)
def get_preproc_sentences(docid, corpus):
    """
    load preproc sentences
    """
    # print docid, corpusid
    dt = load_preproc_sentences(corpus)[docid].split("$$$")
    return dt

@lrudecorator(100)
def get_unigram_key(corpus):
    with open("indexes/{}/unigram_key.p".format(corpus), "rb") as inf:
        return pickle.load(inf)

@lrudecorator(100)
def get_nsentences_key(corpus):
    with open("indexes/{}/how_many_sents_in_doc.p".format(corpus), "rb") as inf:
        return pickle.load(inf)


############################

taginfo = dict(q_ltag='<span style="font-weight:bold;color:#0028a3">',
                                     q_rtag='</span>',
                                     f_ltag='<span style="font-weight:bold;color:#b33125">',
                                     f_rtag='</span>')

@lrudecorator(10000)
def get_snippet3(docid, corpus, q, f):
    """
    returns single "highlighted sentence" dictionary.
    supply taginfo in accordance with docs in hilite()

    algorithm
    where "F-containing" means any alias of the facet (including the facet itself),

    if there is a sentence with both Q and an F: return just it as the snippet.
    else
    select the first Q-containing sentence or F-containing sentence (whichever comes first)

    if neither, return sentence 1 in doc (this is news!)
    """
    f_aliases = [] # get rid of this eventually
    if f is not None:
        f_aliases.append(f)
    all_n_sentences = range(get_nsentences_key(corpus)[docid])
    
    priority_queue = PriorityQueue()
    sentences = get_preproc_sentences(docid, corpus) 
    for sentnum in all_n_sentences:
        toktext = sentences[sentnum]
        hsent = hilite(toktext, q, sentnum, docid, f_aliases, taginfo=taginfo)
        if hsent['has_q'] and hsent['has_f']:
            priority_queue.put((1, sentnum, hsent))
        elif hsent['has_q'] or hsent['has_f']:
            priority_queue.put((2, sentnum, hsent))
        else:
            priority_queue.put((3, sentnum, hsent))

    return priority_queue.get(timeout=3)[2]


# regex matching system: always have groups
# (thing being matched)(right)

def f_regex(f_aliases):
    # longest first to ensure longest matches get selected
    # if we had NFAs we wouldnt need hacks like this. long live the DFA
    fa = sorted(f_aliases, key=lambda f: (-len(f), f))
    fa = r"\b(" + "|".join(re.escape(f) for f in fa) + r")(\S{0,4})\b"
    return fa

def q_regex(q):
    qregex = r"\b(" + re.escape(q) + r")(\S{0,4})\b"
    return qregex

def hilite(text, q, sentnum, docid, f_aliases=None, taginfo=None):
    """e.g.
    taginfo=dict(
        q_ltag = "<span style='color:blue'>, q_rtag = "</span>",
        f_ltag = "<span style='color:red'>, f_rtag = "</span>")
    """

    if not taginfo:
        # console-mode defaults
        REDSTART = '\x1b[1m\x1b[31m'
        BLUESTART= '\x1b[1m\x1b[34m'
        END = '\x1b[0m'
        qsub = r'%s|Q> \1 <Q|%s\2' % (BLUESTART, END)
        fsub = r'%s|F> \1 <F|%s\2' % (REDSTART, END)
    else:
        qsub = r'%s\1%s\2' % (taginfo['q_ltag'], taginfo['q_rtag'])
        fsub = r'%s\1%s\2' % (taginfo['f_ltag'], taginfo['f_rtag'])

    text1 = text

    if f_aliases:
        fregex = f_regex(f_aliases)
        text2 = re.sub(fregex, fsub, text1, flags=re.I)
    else:
        text2 = text1
    has_f = text2 != text1

    qregex = q_regex(q)
    text3 = re.sub(qregex, qsub, text2, flags=re.I)
    has_q = text3 != text2
    docid = str(docid)

    docid = docid.encode()
    return dict(has_q=has_q, has_f=has_f, htext=text3, sentnum=sentnum, hash = hashlib.md5(docid).hexdigest())


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
    facets, aliases = Models.get_facets(params, q_docids)

    for f in facets:
        runf(q, f, q_docids, aliases[f])


def runf(q,f,q_docids,aliases):
    from experiment.models import get_doc_metadata, Models
    aliases = set([f] + list(aliases))

    f_docids = Models.f_occurs_filter(q_docids, facet=f, aliases=aliases)

    for docid in f_docids[:5]:
        d = get_doc_metadata(docid)

        t0 = time.time()

