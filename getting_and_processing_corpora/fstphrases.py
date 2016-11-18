import time, os, sys
from collections import deque
try:
    import fst # pyfst
except ImportError:
    raise Exception("Need pyfst to be installed.")

## global state crap for convenience

FSTS = {}
CORENLP = None

# global corenlp object for convenience.
# another approach would be to make an abstraction layer over pos taggers.
# could wrap corenlp, nltk, ark-tweet-nlp, and choose based on availability and
# suitability for the data?

def get_corenlp():
    global CORENLP
    if CORENLP is None:
        try:
            from stanford_corenlp_pywrapper import CoreNLP
        except ImportError:
            raise Exception("Need stanford_corenlp_pywrapper to be available")
        CORENLP = CoreNLP(annotators="tokenize,ssplit,pos,lemma")
    return CORENLP

def get_fst(name):
    global FSTS
    if name not in FSTS:
        here = os.path.dirname(__file__)
        fstdir = os.path.join(here, "grammar", "compiled_fsts")
        filename = os.path.join(fstdir, "%s.bin" % name)
        assert os.path.exists(filename), "FST file does not exist: " + filename
        FSTS[name] = fst.read(filename)
        FSTS[name + "_vocab"] = set(sym for sym,num in FSTS[name].isyms.items())
    return FSTS[name]

## Put this straight in here for simplicity
## https://github.com/slavpetrov/universal-pos-tags

ARK2COARSE="""
!       PRT
#       X
$       NUM
&       CONJ
,       .
@       X
A       ADJ
D       DET
E       X
G       X
L       PRT
M       PRT
N       NOUN
O       PRON
P       ADP
R       ADV
S       NOUN
T       PRT
U       X
V       VERB
X       PRT
Y       PRT
Z       NOUN
^       NOUN
~       X
"""
ARK2COARSE = dict(L.strip().split() for L in ARK2COARSE.strip().split("\n"))
ARKTAGS = set(ARK2COARSE.keys())
COARSETAGS=set(ARK2COARSE.values())
assert len(COARSETAGS)==12


## transducer debugging and matching algorithm

def draw_pdf(transducer, outfile=None, symfile=None): #osymbolfile, isymbolfile):
    # see pdfs/drawing.txt for example how to use
    # dot is the commandline tool from graphviz
    # fstdraw is from openfst
    if not outfile:
        outfile = "out.pdf"
    assert outfile.endswith(".pdf")
    import os
    tmp = "/tmp/tmp.trans"
    if symfile is not None:
        osymbolfile=symfile
        isymbolfile=symfile
    elif symfile is None:
        assert transducer.isyms is not None
        isymbolfile = "%s.isyms" % tmp
        osymbolfile = "%s.osyms" % tmp
        with open(isymbolfile,'w') as f:
            for k,v in transducer.isyms.items():
                print>>f, (u"%s\t%d" % (k,v)).encode("utf8")
        with open(osymbolfile,'w') as f:
            for k,v in transducer.osyms.items():
                print>>f, (u"%s\t%d" % (k,v)).encode("utf8")
    transducer.write("%s.bin" % tmp)
    os.system("""
        fstdraw --portrait --osymbols={osymbolfile}  --isymbols={isymbolfile}
        {tmp}.bin {tmp}.dot""".format(**locals()).replace("\n"," "))
    os.system("dot -Tpdf %s.dot > %s" % (tmp, outfile))
    print>>sys.stderr, "Output to", outfile

def dump_paths(t):
    # from http://pyfst.github.io/user_guide.html
    for i, path in enumerate(t.paths()):
        # print ' '.join(str(arc.ilabel) for arc in path)
        path_istring = ' '.join(t.isyms.find(arc.ilabel) for arc in path)
        path_ostring = ' '.join(t.osyms.find(arc.olabel) for arc in path)
        # path_weight = reduce(operator.mul, (arc.weight for arc in path))
        path_weight=0
        print(u'{:5} | {:4} | {} / {}'.format(i, path_istring, path_ostring, path_weight))


def findstarts2(t):
    # (stateid, tokposition)
    queue = deque([ (0,0) ])
    has_been_queued = set([ (0,0) ])
    startlabel = t.osyms.find("START")
    assert t.osyms.find(0) == "@0@"  # epsilon symbol
    while queue:
        stateid,position = queue.popleft()
        for arc in t[stateid].arcs:
            nextstate = arc.nextstate
            nextposition = position + int(arc.ilabel != 0)
            if arc.olabel==startlabel:
                yield nextstate,nextposition
            pair = (nextstate,nextposition)
            if pair not in has_been_queued:
                assert nextstate not in queue
                queue.append(pair)
                has_been_queued.add(pair)
    assert len(has_been_queued) == len(t)

def dfs2(t, stateid, position, prefix):
    # print "ENTER", (stateid,position)
    seen = set(prefix)
    if (stateid,position) in seen: 
        assert False
        return

    startlabel = t.osyms.find("START")
    endlabel = t.osyms.find("END")
    state = t[stateid]
    newprefix = prefix + [(stateid,position)]

    # print "NEWARCS", len(list(state.arcs))
    for arc in state.arcs:
        if arc.olabel == endlabel:
            # print "R",newprefix
            yield newprefix
        elif arc.olabel==startlabel:
            assert False, "shouldnt encounter a startlabel here"
        else:
            # print "NEXT %s --%s:%s-> %s" % (stateid, t.isyms.find(arc.ilabel), t.osyms.find(arc.ilabel), arc.nextstate)
            nextstate = arc.nextstate
            nextposition = position + int(arc.ilabel != 0)
            assert nextstate != stateid
            # if (nextstate,nextposition) in seen: continue
            gen = dfs2(t, nextstate, nextposition, newprefix)
            for result in gen:
                yield result

def extract_from_composition2(t, num_phrases_limit_per_start=100, length_limit=30):
    # outerloop: BFS.  innerloop: DFS
    def gen():
        for stateid,position in findstarts2(t):
            for rnum,result in enumerate(dfs2(t, stateid, position, [])):
                # ack, infinite loop sometimes.
                if rnum >= num_phrases_limit_per_start:
                    # print "LIMIT"
                    break
                yield tuple(i for s,i in result[:-1])
    return set(gen())

def preprocess_tags(pos_seq, vocab, tagset):
    assert 'O' in vocab
    tagset = tagset or 'auto'
    assert tagset in ('auto','ark','coarse','ptb')
    if tagset=='auto':
        if all(len(tag)==1 and tag in ARKTAGS for tag in pos_seq):
            tagset = 'ark'
        elif all(tag in COARSETAGS for tag in pos_seq):
            tagset = 'coarse'
        else:
            tagset = 'ptb'
    if tagset=='ark':
        pos_seq = [ARK2COARSE[t] for t in pos_seq]
        tagset='coarse'
    if tagset=='coarse':
        pos_seq = ["Coarse" + ("DOT" if t=='.' else t) for t in pos_seq]
    if tagset=='ptb':
        pass # dont need to do anything
    pos_seq = [t if t in vocab else 'O' for t in pos_seq]  #tags unknown to grammar
    return pos_seq

def extract_from_poses(pos_seq, phrase_transducer, vocab=None, draw_composition=None, tagset='auto', **kwargs):
    """
    tagset could be:  'ark', 'ptb', 'coarse', 'auto'
        ark: Gimpel et al 2011's twitter tagset
        ptb: Penn Treebank
        coarse: Petrov et al's Universal POS tagset
        auto: try to detect. this may waste time.
    (todo: use NLTK's tagset naming system. nathan contributed to it)
    RETURNS: span indices for phrases
    """
    # t0 = time.time()
    if isinstance(phrase_transducer, (str,unicode)):
        tname = phrase_transducer
        phrase_transducer = get_fst(tname)
        vocab = FSTS[tname + "_vocab"]
    if vocab is None:
        vocab = set(sym for sym,num in phrase_transducer.isyms.items())
    # print "0setup elapsed %.3f ms" % ((time.time() - t0)*1e3)
    # t0 = time.time()

    pos_seq = preprocess_tags(pos_seq, vocab, tagset)
    # print "1tagpreproc elapsed %.3f ms" % ((time.time() - t0)*1e3)
    # t0 = time.time()

    input_transducer = fst.linear_chain(pos_seq, syms=phrase_transducer.isyms)
    # print "2linchain elapsed %.3f ms" % ((time.time() - t0)*1e3)
    # t0 = time.time()

    composed = input_transducer >> phrase_transducer
    if len(composed)==0: return []
    if draw_composition:
        draw_pdf(composed, draw_composition)
    # print "3composition elapsed %.3f ms" % ((time.time() - t0)*1e3)
    # t0 = time.time()

    ret = extract_from_composition2(composed, **kwargs)
    # print "4extraction elapsed %.3f ms" % ((time.time() - t0)*1e3)
    return ret

##########

from fst import Acceptor
def ambigchain(multiseq, syms=None, semiring='tropical'):
    chain = Acceptor(syms, semiring=semiring)
    for i, chars in enumerate(multiseq):
        for c in chars:
            chain.add_arc(i, i+1, c)
    chain[i+1].final = True
    return chain

def extract_from_pos_multiseq(pos_multiseq, phrase_transducer, vocab=None, tagset='auto', **kwargs):
    """pos_multiseq: every position has a sequence of possible tags.
    e.g.  [ ["V","N"], ["N"], ["N"] ] where the first position is ambig bw verb and noun
    """
    if isinstance(phrase_transducer, (str,unicode)):
        tname = phrase_transducer
        phrase_transducer = get_fst(tname)
        vocab = FSTS[tname + "_vocab"]
    if vocab is None:
        assert False
        vocab = set(sym for sym,num in phrase_transducer.isyms.items())

    pos_multiseq = [set(preprocess_tags(tags, vocab,tagset)) for tags in pos_multiseq]
    # print pos_multiseq
    input_transducer = ambigchain(pos_multiseq, syms=phrase_transducer.isyms)
    composed = input_transducer >> phrase_transducer
    # return composed  # XXX
    if len(composed)==0: return []
    ret = extract_from_composition2(composed, **kwargs)
    return sorted(set(tuple(x) for x in ret))

def extract_from_pos_posterior(pos_probs, absthresh=0.1, tagset='ark'):
    """pos_probs is a list of dicts of tag probs:
        [ {"A": 0.3, "N":0.2}, {"N":0.9}, ... ]
    """
    assert tagset != 'auto'
    multiseq = []
    for probs in pos_probs:
        toptag = max(probs, key=lambda t: probs[t])
        goodtags = {t for t,p in probs.iteritems() if p >= absthresh}
        multiseq.append(goodtags | {toptag})
    return extract_from_pos_multiseq(multiseq, "NP", tagset=tagset)

def view_multipos():
    import ujson as json
    ## sys.stdin are lines from the uncertain_tagging/ tagger
    for line in sys.stdin:
        toks,tagprobs,text = line.split("\t")
        toks = toks.decode("utf-8").split()
        tagprobs=json.loads(tagprobs)
        print "TEXT\t%s" % (text.strip())
        for tok,probs in zip(toks,tagprobs):
            items = sorted(probs.items(), key=lambda (t,p): (-p,t))
            rankprobs = ["%s:%.3f" % (t,p) for t,p in items]
            rankprobs = ' '.join(rankprobs)
            print u"\t%s\t%s" % (tok, rankprobs)

def run_multipos(thresh=0.1):
    import ujson as json
    ## sys.stdin are lines from the uncertain_tagging/ tagger
    for line in sys.stdin:
        toks,tagprobs,text = line.split("\t")
        toks = toks.split()
        tagprobs=json.loads(tagprobs)
        print "TEXT\t%s" % (text.strip())
        for span in extract_from_pos_posterior(tagprobs, absthresh=float(thresh)):
            print "P\t%s\t%s" % (json.dumps(span), ' '.join(toks[span[0]:span[-1]+1]))

def run_multipos2():
    import ujson as json
    ## sys.stdin are lines from the uncertain_tagging/ tagger
    for line in sys.stdin:
        toks,tagprobs,text = line.split("\t")
        print toks
        toks = toks.split()
        tagprobs=json.loads(tagprobs)

        spans1 = extract_from_pos_posterior(tagprobs, absthresh=1)
        spans2 = extract_from_pos_posterior(tagprobs, absthresh=.001)
        spans1=set(spans1)
        spans2=set(spans2)
        assert not (spans1 - spans2)

##########

def normalize_phrase(jsent, phrase_positions):
    terms = []
    for i in phrase_positions:
        # todo investigate more magic here
        terms.append(jsent['tokens'][i].lower())
    return u' '.join(terms)

def extract_normalized_phrases_from_jsent(jsent, phrase_transducer, **kwargs):
    """returns a dict for each phrase"""
    phrase_positions = extract_from_poses(jsent['pos'], phrase_transducer, **kwargs)
    phrases = [{'positions':pp, 'normalized': normalize_phrase(jsent, pp)}
            for pp in phrase_positions]
    return phrases

def extract_and_add_to_jdoc(jdoc, phrase_transducer, newkey='phrases', **kwargs):
    for sentence in jdoc['sentences']:
        phrases = extract_normalized_phrases_from_jsent(sentence, phrase_transducer, **kwargs)
        sentence[newkey] = phrases

def extract_from_text(text, phrase_transducer):
    """Runs a tokenizer and POS tagger for you and returns these annotations, *plus* the phrase extractions in the jsent data structure"""
    tagger = get_corenlp()
    if isinstance(text,str) and not isinstance(text,unicode):
        text = text.decode("utf8")
    jdoc = tagger.parse_doc(text)
    extract_and_add_to_jdoc(jdoc, phrase_transducer)
    return jdoc

def view_phrases_from_text(text, phrase_transducer):
    import json
    dumps = lambda x: json.dumps(x, separators=(',',':'))
    jdoc = extract_from_text(text, phrase_transducer)
    for sent in jdoc['sentences']:
        # print "===", u' '.join(sent['tokens'])
        print "===", u' '.join(u"%s_%d" % (sent['tokens'][i],i) for i in range(len(sent['tokens'])))
        for phrase in sent['phrases']:
            print u"\t%s\t%s\t%s" % (phrase['normalized'], u' '.join(sent['pos'][i] for i in phrase['positions']), dumps(phrase['positions']))

if __name__=='__main__':
    eval(sys.argv[1])(*sys.argv[2:])
