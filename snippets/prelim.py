'''
This module creates snippets for a doc list
'''
from experiment.models import get_metadata_file
from rookie.classes import IncomingFile

def get_snippet(docid, q, f=None):
    '''
    Return a document snippet
    '''
    md = get_metadata_file()
    doc_meta_data = md[docid]
    facet_index = doc_meta_data['facet_index']
    sentence_with_q = facet_index[q]
    print sentence_with_q
