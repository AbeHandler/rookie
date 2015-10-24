import pdb
from flask import render_template
from rookie import page_size


class Views(object):

    '''Render views.'''
    @staticmethod
    def get_results2_page(query, results, tops, len_results, message, pages, lens_css, banner_css):
        '''
        '''

        organizations = [p[0] for p in tops['organizations']]
        people = [(p[0], p[2]) for p in tops['people']]
        terms = [p[0] for p in tops['terms']]
        n_results = [r for r in results]
        response = render_template(
                'results2.html',
                query=query,
                people=people,
                organizations=organizations,
                terms=terms,
                n_results=n_results,
                pages=pages,
                message=message,
                number_of_documents=len_results,
                lens_css=lens_css,
                banner_css=banner_css
        )

        return response


    @staticmethod
    def get_results_page_relational(query, q_and_t, lens_css, banner_css):
        '''
        '''

        response = render_template(
                'results3.html',
                query=query,
                terms=q_and_t,
                lens_css=lens_css,
                banner_css=banner_css
        )

        return response

    @staticmethod
    def get_results_page_relational_overview(query, q_and_t, lens_css, banner_css):
        '''
        '''

        response = render_template(
                'results4.html',
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
                snippet=snippet
        )

        return response