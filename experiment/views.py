import pdb
from experiment.models import get_metadata_file
from flask import render_template

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


    def get_start_page(self):
        '''
        Returns the first view of the application
        '''
        response = render_template(
            'index.html',
            lens_css=self.lens_css,
            banner_css=self.banner_css,
            IP=self.ip,
            ROOKIE_JS=self.js
        )

        return response


    def get_doc_list(self, results, params, status):
        '''
        Returns the first view of the application
        '''
        response = render_template(
            'doclist.html',
             results=results,
             page=params.page,
             status=status
        )

        return response


    def get_big_viz(self, params, labels, facets, datas):
        response = render_template(
            'bigviz.html',
            query=params.q,
            page=params.page,
            data=datas,
            lens_css=self.lens_css,
            keys=labels,
            labels=labels,
            IP = self.ip,
            facets=facets,
            ROOKIE_JS = self.js,
            ROOKIE_CSS = self.rookie_css,
            BANNER_CSS = self.banner_css
        )

        return response

    def get_q_response(self, params, results, q_and_t, keys, datas, status, len_results):
        '''
        '''
        q_and_t = [[i[0].replace(" ", "_")] + i[1:] for i in q_and_t]
        response = render_template(
            'results5.html',
            query=params.q,
            page=params.page,
            terms=q_and_t,
            lens_css=self.lens_css,
            keys=keys,
            datas=datas,
            doc_list=results,
            banner_css=self.banner_css,
            status=status,
            len_results=len_results,
            IP = self.ip,
            ROOKIE_JS = self.js,
            ROOKIE_CSS = self.rookie_css
        )

        return response


    def get_q_response_med(self, params, results, q_and_t, keys, datas, status, len_results, labels):
        '''
        '''
        q_and_t = [[i[0].replace(" ", "_")] + i[1:] for i in q_and_t]
        response = render_template(
            'medviz.html',
            query=params.q,
            page=params.page,
            terms=q_and_t,
            lens_css=self.lens_css,
            keys=keys,
            data=datas,
            doc_list=results,
            banner_css=self.banner_css,
            status=status,
            labels=labels,
            len_results=len_results,
            IP = self.ip,
            ROOKIE_JS = self.js,
            ROOKIE_CSS = self.rookie_css
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