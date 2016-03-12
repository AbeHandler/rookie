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

def pluck_tokens(term, sentence, n_buffer_chars, f_term=None):
    """get tokens that contain q + buffer"""
    token_offset = get_offsets(term, sentence["as_string"])
    if token_offset[0] == token_offset[1] == 0:
        return []
    #token stucture = (string, token_no, offset in doc) => ex. [u'Sheriffs', 0, [5798, 5806]]
    # the start_offset is the char_offset of the first token in the sentence.
    # corenlp gives perdoc offets
    start_offset_docwide = [token[2] for token in sentence["tokens"] if token[1] == 0].pop()[0]
    tok_offset_start = start_offset_docwide + token_offset[0]
    tok_offset_end = start_offset_docwide + token_offset[1]
    #indexing from token_start, hence tok[2][0] b/c regex might match midway thru token
    kernel = [tok[1] for tok in sentence["tokens"] if
              tok[2][0] >= tok_offset_start and tok[2][0] <= tok_offset_end]
    #kernel is the tokens that contain q
    end_tok = (len(sentence["tokens"]) - 1
               if max(kernel) + n_buffer_chars -1 > len(sentence["tokens"])
               else max(kernel) + n_buffer_chars)
    start_tok = 0 if min(kernel) - n_buffer_chars < 0 else min(kernel) - n_buffer_chars
    return " ".join(i[0] for i in sentence["tokens"][start_tok:end_tok])

def select_mid(sentences):
    """return the middle sentence by time"""
    sentences = sorted(sentences, key=lambda sent: sent["pubdate"])
    return sentences[int(math.floor(len(sentences)/2))] # mid item in the list

def summarize_helper(results, sentences, sum_params):
    """a recursive helper"""
    has_q = [sent for sent in sentences if sent["has_q"] == True]
    if len(has_q) > 0:
        mid = select_mid(has_q)
    else:
        mid = select_mid(sentences)
    output = pluck_tokens(sum_params["query"], mid, sum_params["n_buffer_chars"])
    return (summarize_helper(results, [sent for sent in sentences if sent["pubdate"] < mid["pubdate"]], sum_params) + 
           output + 
           summarize_helper(results, [sent for sent in sentences if sent["pubdate"] >= mid["pubdate"]], sum_params))


# TODO this will loop forever if charbudget is too low
def summarize(results, params):
    """the baseline algorithm"""
    sentences = prepare_sentences(results, params["query"], params["facet"])
    return summarize_helper(results, sentences, params)
