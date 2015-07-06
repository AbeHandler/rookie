"""
Renders the screens for the web app
"""

from flask import render_template, make_response


from rookie import (
    log,
    LENS_CSS,
    BANNER_CSS,
    CONTRACTS_CSS,
    SEARCH_JS,
    CLOUD_JS,
    CLOUD_LAYOUT_JS
)


class Views(object):

    '''Render views.'''

    @staticmethod
    def get_home(results):
        '''Render home page.'''

        response = make_response(
            render_template(
                'index.html',
                search_js=SEARCH_JS,
                lens_css=LENS_CSS,
                banner_css=BANNER_CSS,
                contracts_css=CONTRACTS_CSS
            )
        )

        return response

    @staticmethod
    def get_results(results):
        '''Render home page.'''

        response = make_response(
            render_template(
                'results.html',
                results=results,
                search_js=SEARCH_JS,
                cloud_js=CLOUD_JS,
                cloud_layout_js=CLOUD_LAYOUT_JS,
                lens_css=LENS_CSS,
                banner_css=BANNER_CSS,
                contracts_css=CONTRACTS_CSS
            )
        )

        return response
