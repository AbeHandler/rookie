import pdb
from flask import render_template
from rookie import page_size


class Views(object):

    '''Render views.'''
    @staticmethod
    def get_results_page(results, tops, current_page, query, len_results, message, pages):
        '''
        Renders the homepage (/contracts/).
        :param data: Data for the homepage.
        :type data: dict
        :returns: HTML. Rendered and ready for display to the user.
        '''

        organizations = [p[0] for p in tops['organizations']]
        people = [p[0] for p in tops['people']]
        terms = [p[0] for p in tops['terms']]
        n_results = [r for r in results]
        response = render_template(
                'results.html',
                people=people,
                organizations=organizations,
                current_page=current_page,
                terms=terms,
                n_results=n_results,
                pages=pages,
                message=message,
                number_of_documents=len_results
        )

        return response

    '''Render views.'''
    @staticmethod
    def get_results2_page(results, tops, start, query, len_results, message, pages, lens_css, banner_css):
        '''
        Renders the homepage (/contracts/).
        :param data: Data for the homepage.
        :type data: dict
        :returns: HTML. Rendered and ready for display to the user.
        '''

        organizations = [p[0] for p in tops['organizations']]
        people = [p[0] for p in tops['people']]
        terms = [p[0] for p in tops['terms']]
        n_results = [r for r in results]
        response = render_template(
                'results2.html',
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