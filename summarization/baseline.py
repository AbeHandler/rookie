'''
baseline summary algorithm
'''
from webapp.snippet_maker import hilite
from webapp.models import get_doc_metadata
from dateutil import parser
import math
import re

TAGINFO = dict(q_ltag='<span style="font-weight:bold;color:#0028a3">',
               q_rtag='</span>',
               f_ltag='<span style="font-weight:bold;color:#b33125">',
               f_rtag='</span>',)

CORPUS = "lens"


def prepare_sentences(results, query, facet):
    '''
    Get hilighted sentences for a results set. Make no decisions, just return.

    :param query: query.
    :param facet: facet.
    :param results: list of docids
    :returns: dict. hilighted sentences
    '''
    output = []
    for result in results:
        md = get_doc_metadata(result, CORPUS)
        for sentnum, toktext in enumerate(md['sentences']):
            hsent = hilite(toktext["as_string"], query, facet, taginfo=TAGINFO)
            hsent["sentnum"] = sentnum
            hsent["as_string"] = toktext["as_string"]
            hsent["tokens"] = toktext["as_tokens"]
            hsent["pubdate"] = parser.parse(md["pubdate"])
            output.append(hsent)
    return output

def get_offsets(word, raw_text):
    """get offsets for a word in text via regex"""
    try:
        match = re.search(word, raw_text)
        return (match.start(), match.end())
    except AttributeError: #could not find word
        return (0, 0)

def pluck_tokens(term, sentence, f_term=None):
    """get tokens that contain q + buffer"""
    token_offset = get_offsets(term, sentence["as_string"])
    # token stucture = (string, token_no, offset in doc) => ex. [u'Sheriffs', 0, [5798, 5806]]
    # the start_offset is the char_offset of the first token in the sentence.
    # corenlp gives perdoc offets
    start_offset_docwide = [token[2] for token in sentence["tokens"] if token[1] == 0].pop()[0]
    tok_offset_start = start_offset_docwide + token_offset[0]
    tok_offset_end = start_offset_docwide + token_offset[1]
    print token_offset
    print sentence["as_string"]
    import ipdb
    ipdb.set_trace()
    print sentence["as_string"][token_offset[0]:token_offset[1]]
    return [tok for tok in sentence["tokens"] if
            tok[2][0] > tok_offset_start and tok[2][1] < tok_offset_end]

def select_mid(sentences):
    """return the middle sentence by time"""
    sentences = sorted(sentences, key=lambda sent: sent["pubdate"])
    return sentences[int(math.floor(len(sentences)/2))] # mid item in the list
