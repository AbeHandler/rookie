"""
Renders the screens for the web app
"""

from flask import render_template, make_response


class Views(object):

    '''Render views.'''

    @staticmethod
    def get_response(results):
        '''Render home page.'''

        response = make_response(
            render_template(
                'index.html',
                results
            )
        )

        return response
