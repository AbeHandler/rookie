'''
baseline summary algorithm
'''
from webapp.snippet_maker import hilite
from webapp.models import get_doc_metadata

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
        print result
        md = get_doc_metadata(result, CORPUS)
        for sentnum, toktext in enumerate(md['sentences']):
            hsent = hilite(toktext, query, facet, taginfo=TAGINFO)
            hsent["sentnum"] = sentnum
            output.append(hsent)
    return output
