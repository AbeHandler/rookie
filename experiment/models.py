import pdb
import math
from pylru import lrudecorator
from experiment.cloud_searcher import query_cloud_search
from experiment.cloud_searcher import get_overview
from dateutil.parser import parse


class Models(object):

    '''Handles logic for the experiment app'''

    @staticmethod
    @lrudecorator(1000)
    def search(query, term=None, termtype=None, startdate=None, enddate=None):
        '''search elastic search and return results'''
        results = [r for r in query_cloud_search(query)]
        if term is not None and termtype is not None:
            results = [r for r in results if termtype in r['fields'] and term in r['fields'][termtype]]
        try:
            startdate = parse(startdate)
        except:
            startdate = None
        try:
            enddate = parse(enddate)
        except:
            enddate = None
        if startdate and enddate:
            results = [r for r in results if (parse(r['fields']['pubdate']) >= startdate) and (parse(r['fields']['pubdate']) <= enddate)]
        results = tuple(results)
        tops = get_overview(results, query)  # handle the cloudsearch results
        return results, tops

    @staticmethod
    def translate_page(page):
        try:
            page = int(page) - 1
        except:
            page = 0

        if page < 0:
            page = 0

        return page

    @staticmethod
    def get_message(page, pages, total_results):
        '''search elastic search and return results'''
        total_results = str(total_results)
        if int(page) == 1:
            return "Found " + total_results + " results"
        else:
            return "Found {} results. Showing page {} of {}".format(total_results, page, max(pages))

    @staticmethod
    def get_pages(total_results, page_size):
        '''search elastic search and return results'''
        return range(1, int(math.ceil(float(total_results)/float(page_size))))
