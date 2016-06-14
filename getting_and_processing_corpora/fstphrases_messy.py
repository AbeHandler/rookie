import time, os, sys, ujson as json
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

def NPS_ENUM():
    return set([tuple(i.replace("\n", "").split(" ")[1:]) for i in open("grammar/fixedlength_NP_sequences.txt", "r")])


def get_corenlp():
    global CORENLP
    if CORENLP is None:
        try:
            from stanford_corenlp_pywrapper import CoreNLP
        except ImportError:
            raise Exception("Need stanford_corenlp_pywrapper to be available")
        CORENLP = CoreNLP(annotators="tokenize,ssplit,pos,lemma,parse", corenlp_jars=["/Users/ahandler/research/nytweddings/stanford-corenlp-full-2015-04-20/*"])
    return CORENLP

def get_fst(name):
    global FSTS
    if name not in FSTS:
        here = os.path.dirname(__file__)
        fstdir = os.path.join(here, "grammar", "compiled_fsts")
        filename = os.path.join(fstdir, "%s.bin" % name)
        assert os.path.exists(filename), "FST file does not exist: " + filename
        FSTS[name] = fst.read(filename)
    return FSTS[name]

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

def bfs_find_starts(t):
    # the fact this is bfs doesnt matter, we just need to find all START-entered states.
    found = set()
    start_id = t.osyms.find("START")
    assert t.osyms.find(0) == "@0@"  # epsilon symbol
    stateid2position = {0:0}
    queue = deque([0])
    has_been_queued = set([0])
    while queue:
        stateid = queue.popleft()
        for arc in t[stateid].arcs:
            if arc.olabel==start_id:
                found.add(arc.nextstate)
            if arc.nextstate not in has_been_queued:
                assert arc.nextstate not in queue
                queue.append(arc.nextstate)
                has_been_queued.add(arc.nextstate)
                prev = stateid2position[stateid]
                here = prev + int(arc.ilabel != 0)
                if arc.nextstate not in stateid2position:
                    stateid2position[arc.nextstate] = here
                else:
                    assert stateid2position[arc.nextstate] == here
    assert len(has_been_queued) == len(t)
    assert len(stateid2position) == len(t)
    return found, stateid2position

def dfs_until_endsymbol(t, stateid, prefix, length_limit):
    # in simple cases, only one path to an endsymbol.
    # more complex ones have multiple thus need dfs.
    # JJ JJ NN NN
    # there's a START at the very start.
    # ends either with JJ JJ NN or can continue to JJ JJ NN NN.

    # TODO: length_limit was supposed to be a length limit on number of tokens
    # ... but it appears to not do that and instead let things through with a
    # greater count. not sure what's going on.  would be esp bad if it
    # disallowed things that were shorter than the advertised length_limit.

    if len(prefix) >= length_limit:
        return

    start_id = t.osyms.find("START")
    end_id = t.osyms.find("END")
    state = t[stateid]
    for arc in state.arcs:
        if arc.olabel == end_id:
            yield prefix + [(stateid,arc)]
        elif arc.olabel == start_id:
            assert False, "shouldnt encounter startid symbol, i think"
        else:
            for result in dfs_until_endsymbol(
                    t, arc.nextstate, prefix+[(stateid,arc)],
                    length_limit=length_limit):
                yield result

def extract_from_composition(t, num_phrases_limit=1000, length_limit=30):
    """Generates a sequence of tuples of phrase spans.
    Each tuple contains the index positions of all the words in the phrase."""
    # t0 = time.time()
    num_phrases_found = 0
    startstates, stateid2position = bfs_find_starts(t)
    # print "elapsed %.3f ms from bfs" % ((time.time() - t0)*1e3)
    for sid in startstates:
        for path in dfs_until_endsymbol(t, sid, [], length_limit=length_limit):
            ## return the full path
            positions = tuple(stateid2position[sid] for sid,arc in path[:-1])
            assert len(positions)==len(set(positions))
            if len(positions)==0:
                # hack around issue #1 zero-length rewrites
                continue

            yield positions
            num_phrases_found += 1
            if num_phrases_found >= num_phrases_limit:
                break

            ## alternative: start,end pair being returned
            ## this way doesnt generalize to gappy patterns, sadly
            ## maybe it's ok to just do the full path.
            # start = path[0]
            # end = path[-1]+1
            # # note this also tests for ascending order and uniqueness
            # assert path==range(start,end)  # slow, need to disable
            # yield (start,end)



def enumerate_and_check(pos_seq):
    # http://locallyoptimal.com/blog/2013/01/20/elegant-n-gram-generation-in-python/
    def find_ngrams(input_list, n):
        return zip(*[input_list[i:] for i in range(n)])
    output = []
    NPS_E = NPS_ENUM()
    for i in range(1, 5):
        ngrams = find_ngrams(pos_seq, i)
        output = output + [gram for gram in ngrams if gram in NPS_E]
    return output

def extract_from_poses(pos_seq, phrase_transducer, vocab=None, draw_composition=None, **kwargs):
    """returns span indices for phrases"""
    # t0 = time.time()
    if isinstance(phrase_transducer, (str,unicode)):
        phrase_transducer = get_fst(phrase_transducer)
    if vocab is None:
        vocab = set(sym for sym,num in phrase_transducer.isyms.items())
    oovize = lambda seq: [x if x in vocab else 'O' for x in seq]
    a = set([(k,v) for k,v in kwargs.iteritems()])
    b = set(pos_seq)
    assert 'O' in vocab

    pos_seq = oovize(pos_seq)
    # print "setup elapsed %.3f ms" % ((time.time() - t0)*1e3)
    input_transducer = fst.linear_chain(pos_seq, syms=phrase_transducer.isyms)
    #print vocab
    #print input_transducer
    composed = input_transducer >> phrase_transducer
    if len(composed)==0: return []
    #draw_pdf(input_transducer, "t.pdf")
    if draw_composition:
        draw_pdf(composed, draw_composition)
    # print "%s states" % len(composed)
    # print "composition elapsed %.3f ms" % ((time.time() - t0)*1e3)
    ret = extract_from_composition(composed, **kwargs)
    ret = list(ret)  # might not always be necessary?
    # print "extraction elapsed %.3f ms" % ((time.time() - t0)*1e3)
    return ret

def normalize_phrase(jsent, phrase_positions):
    terms = []
    for i in phrase_positions:
        # todo investigate more magic here
        terms.append(jsent['tokens'][i].lower())
    return u' '.join(terms)

def non_normalized_phrase(jsent, phrase_positions):
    terms = []
    for i in phrase_positions:
        # todo investigate more magic here
        terms.append(jsent['tokens'][i])
    return u' '.join(terms)

def extract_normalized_phrases_from_jsent(jsent, phrase_transducer):
    """returns a dict for each phrase"""
    # ipdb.set_trace()
    phrase_positions = extract_from_poses(jsent['pos'], phrase_transducer)
    phrases = [{'positions':pp, 'regular':non_normalized_phrase(jsent, pp), 'normalized': normalize_phrase(jsent, pp)}
            for pp in phrase_positions]
    return phrases

def extract_and_add_to_jdoc(jdoc, phrase_transducer, newkey='phrases'):
    for sentence in jdoc['text']['sentences']:
        phrases = extract_normalized_phrases_from_jsent(sentence, phrase_transducer)
        sentence[newkey] = phrases

def add_to_jdoc(text, phrase_transducer, jdoc):
    """same as extract_from_text, but bring yr own jdoc"""
    if isinstance(text,str) and not isinstance(text,unicode):
        text = text.decode("utf8")
    extract_and_add_to_jdoc(jdoc, phrase_transducer)
    return jdoc

#https://github.com/AbeHandler/rookie/issues/167
def full_text(jdoc):
    '''
    input: CoreNLP json for a doc
    output: the doc as a long unicode string
    '''
    output = []
    for sent_no, sent in enumerate(jdoc['text']['sentences']):
        for tok_no, token in enumerate(sent["tokens"]):
            tok_char_start = jdoc['text']["sentences"][sent_no]["char_offsets"][tok_no][0]
            if tok_no > 0:
                prev_tok_char_end = jdoc['text']["sentences"][sent_no]["char_offsets"][tok_no-1][1]
                if prev_tok_char_end < tok_char_start:
                    output.append(" ")
            output.append(unicode(token))
        output.append(' ')
    return "".join(output)


def remove(fn):
    '''remove a file'''
    try:
        os.remove(fn)
    except OSError:
        pass

 
def make_anno_plus_2(anno_file):
    '''take an anno file written on disk and make an anno plus w/ phrases'''
    trans = "NP" ## ???? @brenocon if len(sys.argv)<2 else sys.argv[1]
    assert anno_file[-5:] == ".anno"
    remove(anno.replace('.anno', '.anno_plus'))
    with open(anno) as inf:    # TODO: this step will add meaningless time in benchmarking.
        for ln_no, ln in enumerate(inf):
            if ln_no % 10000 == 0:
                print ln_no
            jdoc = json.loads(ln)
            text = full_text(jdoc)
            add_to_jdoc(text, trans, jdoc)
            with open(anno.replace('.anno', '.anno_plus'), "a") as outf:    
                json_string = json.dumps(jdoc)
                outf.write(json_string + "\n")


def extract_from_text(text, phrase_transducer):
    """Runs a tokenizer and POS tagger for you and returns these annotations, *plus* the phrase extractions in the jsent data structure"""
    tagger = get_corenlp()
    if isinstance(text,str) and not isinstance(text,unicode):
        text = text.decode("utf8")
    jdoc = tagger.parse_doc(text)
    extract_and_add_to_jdoc(jdoc, phrase_transducer)
    return jdoc

def view_phrases_from_text(text, phrase_transducer):
    dumps = lambda x: json.dumps(x, separators=(',',':'))
    return extract_from_text(text, phrase_transducer)

if __name__=='__main__':
    anno = sys.argv[1]
    make_anno_plus_2(anno)