"""
Application logic for the web application.
"""

from rookie import log


class Models(object):

    '''Handles logic for the Flask app'''

    def search(self, request, pmis):
        '''search elastic search and return results'''

        output = []

        log.debug(len(output))

        if request.args.get('term') is None:
            log.debug("no parameters")
            results = []
            return results  # TODO leap before look

        term = request.args.get('term')

        try:
            results = pmis[term]
        except KeyError:
            results = []

        return results

    def home(self):
        log.debug("home model")
        return ""
