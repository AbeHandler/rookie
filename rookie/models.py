"""
Application logic for the web application.
"""

import pdb

from rookie import log
from rookie.merger import Merger
from rookie.utils import get_window, Result


class Models(object):

    '''Handles logic for the Flask app'''

    def search(self, request, pmis):
        '''search elastic search and return results'''

        output = []

        log.debug('start')

        if request.args.get('term') is None:
            log.debug("no parameters")
            results = []
            return results  # TODO leap before look

        term = request.args.get('term')

        try:
            results = pmis[term]
        except KeyError:
            results = []

        log.debug('merge lists start')
        # TODO see github issue on merge
        results = Merger.merge_lists(results)
        results = Merger.merge_lists(results)

        out = []

        log.debug('get window start')
        for results in results:
            window = get_window(results[0])
            out.append(Result(results[0], results[1], window))

        log.debug('end')
        return out

    def home(self):
        log.debug("home model")
        return ""
