import pdb
from experiment.models import get_metadata_file
from flask import render_template

class Views(object):

    @staticmethod
    def get_start_page(lens_css, banner_css):
        '''
        Returns the first view of the application
        '''
        response = render_template(
                'index.html',
                lens_css=lens_css,
                banner_css=banner_css
        )

        return response

    @staticmethod
    def get_detail_page(query, q_and_t, headline, dateline, tokens, lens_css, banner_css):
        '''
        '''
        response = render_template(
                'detail.html',
                query=query,
                headline=headline,
                dateline=dateline,
                tokens=tokens,
                terms=q_and_t,
                lens_css=lens_css,
                banner_css=banner_css
        )

        return response

    @staticmethod
    def get_q_response(query, results, q_and_t,lens_css, banner_css):
        '''
        '''

        response = render_template(
                'results5.html',
                query=query,
                terms=q_and_t,
                lens_css=lens_css,
                banner_css=banner_css
        )

        return response


    @staticmethod
    def print_snippet(snippet):
        '''
        '''
        response = render_template(
                'snippet.html',
                snippet=snippet #TODO: sort out tokenization
        )

        return response