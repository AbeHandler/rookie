import re,os,json
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc
from webapp import CONNECTION_STRING
import ipdb
start_time = time.time()
engine = create_engine(CONNECTION_STRING)
Session = sessionmaker(bind=engine)
session = Session()

############################

def get_snippet2(docid, corpus, q, f_aliases=None, taginfo=None):
    """
    returns list of "highlighted sentence" dictionaries.
    supply taginfo in accordance with docs in hilite()

    algorithm
    where "F-containing" means any alias of the facet (including the facet itself),

    if there is a sentence with both Q and an F: return just it as the snippet.
    else
    select the first Q-containing sentence (if any)
    select the first F-containing sentence (if any)
    sort those (at most two) sentences.
    return them as the snippet.
    """

    from webapp.models import get_doc_metadata
    d = get_doc_metadata(docid, corpus)
    hsents = {'has_q':[], 'has_f':[]}
    for sentnum,toktext in enumerate(d['sentences']):
        hsent = hilite(toktext["as_string"], q, f_aliases, taginfo=taginfo)
        hsent['sentnum'] = sentnum
        if hsent['has_q'] and hsent['has_f']:
            return [hsent]

        if hsent['has_q']:
            #import ipdb; ipdb.set_trace()
            hsents['has_q'].append(hsent)
        if hsent['has_f']:
            hsents['has_f'].append(hsent)

    selection = []

    if hsents['has_q']:
        selection.append(hsents['has_q'][0])
    if hsents['has_f']:
        cand = hsents['has_f'][0]
        # this condition shouldnt be possible assuming the shortcut break in the first Q&F
        if not any(x['sentnum']==cand['sentnum'] for x in selection):
            selection.append(cand)

    if len(selection)==0:
        # hm tricky.
        # i guess an empty selection is ok
        return selection

    selection.sort(key=lambda x: x['sentnum'])
    return selection

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

def hilite(text, q, f_aliases=None, taginfo=None):
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
    print "FACETS", facets
    for f in facets:
        print f, sorted(aliases[f])
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


        t0 = time.time()

        # hsents = get_snippet1(docid, q=q, f_aliases=[f])
        # hsents = get_snippet2(docid, q=q, f_aliases=[f])
        hsents = get_snippet2(docid, q=q, f_aliases=aliases)

        # print "  snippet time", time.time()-t0
        for h in hsents:
            print "  s%s\tq=%d f=%d\t%s" % (h['sentnum'], h['has_q'], h['has_f'], h['htext'])

