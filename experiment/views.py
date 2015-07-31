import pdb


class Views(object):

    '''Render views.'''

    @staticmethod
    def get_results_page(results, tops):
        '''
        Renders the homepage (/contracts/).
        :param data: Data for the homepage.
        :type data: dict
        :returns: HTML. Rendered and ready for display to the user.
        '''

        pdb.set_trace()
        return "hi there"

        response = make_response(
            render_template(
                'index.html',
                people=tops['people'],
                organizations=tops['organizations'],
                terms=tops['terms'],
                n_results=results,
                number_of_documents=number_of_documents
            )
        )

        return response
