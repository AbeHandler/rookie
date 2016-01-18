import ipdb
from experiment.models import get_metadata_file
from flask import render_template
from nltk.tokenize import word_tokenize

class Views(object):

    def __init__(self, lens_css, banner_css, IP, ROOKIE_JS, ROOKIE_CSS):
        '''
        Initalize the views
        '''
        self.lens_css = lens_css
        self.banner_css = banner_css
        self.ip = IP
        self.js = ROOKIE_JS
        self.rookie_css = ROOKIE_CSS
        self.banner_css = banner_css


    def get_doc_list(self, results, params, status):
        '''
        Returns the first view of the application
        '''

        response = render_template(
            'doclist.html',
             query_toks=word_tokenize(params.q),
             results=results,
             page=params.page,
             status=status
        )

        return response


    def get_q_response_med(self, params, results, q_and_t, keys, q_datas, len_results, binsize, binned_facets, g_facets):
        '''
        return medviz view
        '''
        response = render_template(
            'medviz.html',
            query=params.q,
            f_counts=q_and_t,
            chart_bins=keys,
            q_datas=q_datas,
            g_facets=g_facets,
            doc_list=results,
            len_results=len_results,
            detail=binsize,
            len_keys=len(keys),
            binned_facets=binned_facets,
            IP = self.ip,
            ROOKIE_JS = self.js,
            ROOKIE_CSS = self.rookie_css
        )

        return response
