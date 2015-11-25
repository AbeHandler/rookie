import pdb
import json
import itertools
from rookie.rookie import Rookie
from pylru import lrudecorator
from collections import defaultdict
from dateutil.parser import parse
from rookie.classes import IncomingFile
from experiment import log, CORPUS_LOC

@lrudecorator(100)
def get_metadata_file():
    with open("rookieindex/meta_data.json") as inf:
        metadata = json.load(inf)
    return metadata


class Parameters(object):

    def __init__(self):
        self.q = None
        self.term = None
        self.termtype = None
        self.current_page = None
        self.startdate = None
        self.enddate = None
        self.docid = None
        self.page = None


def ovelaps_with_query(facet, query_tokens):
    if len(set(facet.split(" ")).intersection(query_tokens)) == 0:
        return False
    else:
        return True


def bin_dates(dates, interval=12):
    '''
    Put the dates in bins. Default interval is 12 months
    '''
    output = defaultdict(lambda : defaultdict(int))
    if interval == 12:
        for term in dates.keys():
            for dt in dates[term]:
                output[term][int(dt[0:4])] += 1
    all_bins = set([i for i in itertools.chain(*[output[o].keys() for o in output])])
    for bin in all_bins:
        for key in output:
            if bin not in output[key].keys():
                output[key][bin] = 0
    return output



def overlaps_with_output(facet, output):
    '''
    Is this facet already in the list?
    '''
    for i in output:
        if len(set(facet.split(" ")).intersection(i.split(" "))) > 0:
            return True
    return False


def passes_one_word_heuristic(on_deck):
    '''
    Short check for meaningless 1-grams like "commission"
    '''
    if len(on_deck.split(" ")) < 2 and sum(1 for l in on_deck if l.isupper()) < 2:
        return False
    return True


def facet_occurs(metadata, facet, aliases):
    '''
    Does the facet or any of its aliases show up
    in the metadata for one document?
    '''
    all_names = [unicode(facet)] + aliases
    output = []
    for key in [u'people', u'ngram', u'org']:
        for name in all_names:
            if name in metadata[key]:
                output.append(metadata['pubdate'])
    return output

class Models(object):

    '''Handles logic for the experiment app'''

    @staticmethod
    def get_tokens(docid):
        with open('articles/' + docid) as data_file:    
            data = json.load(data_file)
        return data

    @staticmethod
    def get_headline(docid):
        dt = get_metadata_file()
        return dt[docid]['headline']

    @staticmethod
    def get_pub_date(docid):
        dt = get_metadata_file()
        return dt[docid]['pubdate']

    @staticmethod
    def get_message(l_results, params):
        output = "Showing {} results for {}".format(l_results, params.q)
        return output

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

        try:
            output.docid = request.args.get('docid')
        except:
            output.docid = None

        output.page = 1

        return output

    @staticmethod
    def get_results(params):

        '''
        Just query whoosh
        '''

        rookie = Rookie("rookieindex")

        results = rookie.query(params.q)

        return results

    @staticmethod
    def get_doclist(results, params):
        mt = get_metadata_file()
        output = []
        for r in results:
            output.append((mt[r]['pubdate'], mt[r]['headline'], mt[r]['url'], Models.get_snippet(r, params.q, 200)))
        return output

    @staticmethod
    def get_snippet(r, q, nchar):
        #TODO: add aliasing. remove set sorting
        mt = get_metadata_file()
        try: #TODO not a list
            queue = list(set(mt[r]['facet_index'][q]))
        except KeyError:
            queue = []
        infile = IncomingFile(CORPUS_LOC + mt[r]['raw'])
        # build a queue of sentences to include
        for i in range(len(infile.doc.sentences)):
            if i not in queue:
                queue.append(i)
        output = ""
        for i in queue:
            if len(output) > nchar:
                return output
            sentence = str(infile.doc.sentences[i])
            try:
                l = max(sentence.index(q)-25, 0)
                r = max(sentence.index(q)+25, len(sentence))
            except ValueError:
                l = 0
                r = 50
            if output == "": # Google always starts snippet with a sentence
                l = 0
            output += sentence[l:r] + "..."
        return output

    @staticmethod
    def get_facets(params, results, n_facets=9):

        '''
        Note this method has to kinds of counters.
        counter % 3 loops over facet types in cycle.
        facet_counters progresses lineararly down each facet list
        '''
        
        rookie = Rookie("rookieindex")

        all_facets = {}

        facet_types = ["people", "org", "ngram"]
         
        # there are 3 facets so counter mod 3 switches
        counter = 0

        stop_facets = set(["THE LENS", "LENS"])

        query_tokens = set(params.q.split(" "))

        facet_counters = {} # a pointer to which facet to include
        
        all_aliases = {}

        # Get each of the facets
        for f_type in facet_types:
            tmpfacets, newaliases = rookie.facets(results, f_type)
            all_facets[counter] = tmpfacets
            all_aliases.update(newaliases)
            facet_counters[counter] = 0
            counter += 1

        output = []

        log.debug('got facets. time to filter')
        # Figure out which facets to include in the UI
        while len(output) < n_facets:
            try:
                on_deck = all_facets[counter % 3][facet_counters[counter % 3]][0]
                if not ovelaps_with_query(on_deck, query_tokens) and not overlaps_with_output(on_deck, output) and passes_one_word_heuristic(on_deck):
                    output.append(all_facets[counter % 3][facet_counters[counter % 3]][0])
            except IndexError: # facet counter is too high? just end loop early
                break
            counter += 1
            facet_counters[counter % 3] += 1

        log.debug('get the pub dates')
        # Get the pub dates
        mt = get_metadata_file()
        dates = defaultdict(list)
        for r in results:
            for o in output:
                dates[o].extend(facet_occurs(mt[r], o, all_aliases[o]))
        dates_bin = bin_dates(dates)
        return dates_bin, output