import pdb
import math
from rookie import log
from pylru import lrudecorator
from experiment.cloud_searcher import query_cloud_search
from experiment.cloud_searcher import get_overview
from dateutil.parser import parse


class Parameters(object):

    def __init__(self):
        self.q = None
        self.term = None
        self.termtype = None
        self.current_page = None
        self.startdate = None
        self.enddate = None
        self.page = None


class Models(object):

    '''Handles logic for the experiment app'''

    @staticmethod
    @lrudecorator(1000)
    def get_snippet():
        snip = '''Lorem ipsum dolor sit amet, in enim ancillae his, an vis nostrum facilisi, vis intellegam definitionem in. Et intellegat reprimique sit, ne vix vitae recteque. Rebum fuisset adolescens ad usu, tempor aliquando te nec, nonumes antiopam democritum cu vel. Adhuc dolor ridens his an, duo aliquid expetendis definiebas cu. No his regione eripuit qualisque, ei molestie percipitur cum. Saepe accusata concludaturque te eam, nam ne brute novum deterruisset.
               Odio reprehendunt eam te, justo dicta ex ius. Est id doming gubergren efficiendi, ut prima eleifend mei. Eos utinam delenit consequat no. Te ubique legendos voluptatibus mel, quo ei congue scripta inciderint. An vitae recusabo eos, eu sed cibo scripta commune.
               Pro suscipit maiestatis id, vel ne lucilius delicata, lorem tritani indoctum mea ex. Pro et integre blandit temporibus. Qui omnis accusata pericula at, nam cu clita laboramus voluptaria. Reque exerci theophrastus no nam.'''
        return snip.replace("\n", "...")

    @staticmethod
    @lrudecorator(1000)
    def search(params, overview=True, snippets=False):
        '''search elastic search and return results'''
        results = [r for r in query_cloud_search(params.q)]
        if params.term is not None and params.termtype is not None:
            log.debug("filtering by term {}".format(params.term))
            results = [r for r in results if params.termtype in r['fields'] and params.term in r['fields'][params.termtype]]
        if params.startdate and params.enddate:
            results = [r for r in results if (parse(r['fields']['pubdate']) >= params.startdate) and (parse(r['fields']['pubdate']) <= params.enddate)]
        results = tuple(results)
        pdb.set_trace()
        if not overview:
            return results
        log.debug("processed results")
        if not snippets:
            tops = get_overview(results, params.q, 3)  # handle the cloudsearch results
            return results, tops
        else:
            tops = get_overview(results, params.q, 3)
            output = []
            for ent_type in tops:
                for ent in tops[ent_type]:
                    output.append((ent[0], Models.get_snippet()))
            return results, tuple(output)


    @staticmethod
    def get_limited(results, term, termtype):
        return [r for r in results if termtype in r['fields'] and term in r['fields'][termtype]]

    @staticmethod
    def translate_page(page):
        try:
            page = int(page) - 1
        except:
            page = 0

        if int(page) < 0:
            page = 0

        return page

    @staticmethod
    def get_message(params, pages, total_results):
        page = params.current_page
        q = params.q

        if params.term and params.termtype:
            q = q + " and " + params.term

        '''search elastic search and return results'''
        total_results = str(total_results)
        if int(page) == 1:
            return "Found " + total_results + " results for " + q
        else:
            return "Found {} results for {}. Showing page {} of {}".format(total_results, q, page, max(pages))

    @staticmethod
    def get_pages(total_results, page_size):
        '''search elastic search and return results'''
        return range(1, int(math.ceil(float(total_results)/float(page_size))))

    @staticmethod
    def get_parameters(request):
        '''get parameters'''
        output = Parameters()

        output.q = request.args.get('q')

        output.term = request.args.get('term')

        output.termtype = request.args.get('termtype')

        output.current_page = request.args.get('page')

        try:
            output.current_page = int(output.current_page)
        except:
            output.current_page = 1

        try:
            output.startdate = parse(request.args.get('startdate'))
            if len(output.startdate) == 0:
                output.startdate = None
        except:
            output.startdate = None
        try:
            output.enddate = parse(request.args.get('enddate'))
            if len(output.enddate) == 0:
                output.enddate = None
        except:
            output.enddate = None

        output.page = Models().translate_page(output.current_page)

        return output
