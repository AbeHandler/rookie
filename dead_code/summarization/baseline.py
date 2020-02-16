'''
baseline summary algorithm
'''
from __future__ import division
from webapp.snippet_maker import hilite
from webapp.models import get_doc_metadata
from dateutil import parser
import math
import random
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

def pluck_tokens(term, sentence, n_buffer_toks, char_budget, f_term=None):
    """get tokens that contain q + buffer"""
    token_offset = get_offsets(term, sentence["as_string"])
    if token_offset[0] == token_offset[1] == 0:
        return ""
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
    max_end_tok = (len(sentence["tokens"]) - 1
               if max(kernel) + n_buffer_toks -1 > len(sentence["tokens"])
               else max(kernel) + n_buffer_toks)
    max_start_tok = 0 if min(kernel) - n_buffer_toks < 0 else min(kernel) - n_buffer_toks
    output = " ".join([sentence["tokens"][i][0] for i in kernel])
    counter_l = kernel[0] - 1 # token to L of kernel
    counter_r = kernel[len(kernel) - 1] + 1 # token to R of kernel
    r_or_l = "R"
    def has_room(r_l, out, char_bud):
        """if room, return true"""
        if r_l == "R":
            if len(out) + len(sentence["tokens"][counter_r][0]) < char_bud:
                return True
            else:
                return False
        if r_l == "L":
            if len(out) + len(sentence["tokens"][counter_l][0]) < char_bud:
                return True
            else:
                return False
    while counter_l >=0 and counter_r <= len(sentence["tokens"]) - 1 and has_room(r_or_l, output, char_budget) and (counter_l >= max_start_tok or counter_r <= max_end_tok):
        if r_or_l == "R":
            r_or_l = "L"
            output = output + " " + sentence["tokens"][counter_r][0]
            counter_r += 1
        else:
            r_or_l = "R"
            output = sentence["tokens"][counter_l][0] + " " + output
            counter_l -= 1
    return output    

def select_mid(sentences):
    """return the middle sentence by time"""
    sentences = sorted(sentences, key=lambda sent: sent["pubdate"])
    return sentences[int(math.floor(len(sentences)/2))] # mid item in the list

def summarize_helper(results, sentences, sum_params, char_budget):
    """a recursive helper"""
    has_q = [sent for sent in sentences if sent["has_q"] == True]
    if len(sentences) == 0:
        print "throw away {}".format(char_budget)
        return ""
    if len(has_q) > 0:
        mid = select_mid(has_q)
    else:
        mid = select_mid(sentences)
    output = pluck_tokens(sum_params["q"], mid, sum_params["n_buffer_toks"], char_budget)
    if len(output) > char_budget:
        print "throw away {}".format(char_budget)
        return ""
    if output == "charter school":
        ipdb.set_trace()
    if ((char_budget - len(output)) / 2) > 75:  # if half is less than 75 you get these little useless 25 char chunks
        char_budget = (char_budget - len(output))/ 2
        if char_budget < 0: 
            char_budget = 0
        #the greater than or less than means that only one sentence is allowed per pubdate. short fix for infinite recursion
        left = summarize_helper(results, [sent for sent in sentences if sent["pubdate"] < mid["pubdate"]], sum_params, char_budget)
        right = summarize_helper(results, [sent for sent in sentences if sent["pubdate"] > mid["pubdate"]], sum_params, char_budget)
        return left + "..." + output + right 
    else:
        char_budget = char_budget - len(output) # if half is less than 75 you get these little useless 25 char chunks
        if char_budget < 0: 
            char_budget = 0
        #the greater than or less than means that only one sentence is allowed per pubdate. short fix for infinite recursion
        
        # so pick randomly between left and right
        left = summarize_helper(results, [sent for sent in sentences if sent["pubdate"] < mid["pubdate"]], sum_params, char_budget)
        return left + "..." + output


# TODO this will loop forever if charbudget is too low
def summarize(results, params):
    """the baseline algorithm"""
    sentences = prepare_sentences(results, params["q"], params["f"])
    return summarize_helper(results, sentences, params, params["char_budget"])
