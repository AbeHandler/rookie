import pdb
from experiment.models import get_metadata_file
from flask import render_template

class Views(object):

    def __init__(self, lens_css, banner_css, IP):
        '''
        Initalize the views
        '''
        self.lens_css = lens_css
        self.banner_css = banner_css
        self.ip = IP


    def get_start_page(self):
        '''
        Returns the first view of the application
        '''
        response = render_template(
                'index.html',
                lens_css=self.lens_css,
                banner_css=self.banner_css,
                IP = self.ip
        )

        return response


    def get_detail_page(self, query, q_and_t, headline, dateline, tokens):
        '''
        '''
        response = render_template(
                'detail.html',
                query=query,
                headline=headline,
                dateline=dateline,
                tokens=tokens,
                terms=q_and_t,
                lens_css=self.lens_css,
                banner_css=self.banner_css,
                IP = self.ip
        )

        return response


    def get_q_response(self, query, results, q_and_t, keys, data, status):
        '''
        '''

        response = render_template(
                'results5.html',
                query=query,
                terms=q_and_t,
                lens_css=self.lens_css,
                keys=keys,
                data=data,
                doc_list=results,
                banner_css=self.banner_css,
                status=status,
                IP = self.ip
        )

        return response


    def print_snippet(self, snippet):
        '''
        '''
        response = render_template(
                'snippet.html',
                snippet=snippet #TODO: sort out tokenization
        )

        return response