import pdb
import json
import ipdb
import pandas as pd
import itertools
from pylru import lrudecorator
from collections import defaultdict
from dateutil.parser import parse
from rookie.classes import IncomingFile
from rookie.rookie import Rookie
from experiment import log, CORPUS_LOC

@lrudecorator(100)
def get_pubdate_index():
    print "loading pubdate index"
    with open("rookieindex/string_to_pubdate.json") as inf:
        metadata = json.load(inf)
    output = {}
    for key in metadata:
        output[key] = set([parse(p) for p in metadata[key]])
    print "built index"
    return output

@lrudecorator(100)
def get_metadata_file():
    with open("rookieindex/meta_data.json") as inf:
        metadata = json.load(inf)
    return metadata


class Parameters(object):

    def __init__(self):
        '''
        An object that holds params from request
        '''
        self.q = None
        self.term = None
        self.termtype = None
        self.startdate = None
        self.enddate = None
        self.docid = None
        self.page = None


def ovelaps_with_query(facet, query_tokens):
    if len(set(facet.split(" ")).intersection(query_tokens)) == 0:
        return False
    else:
        return True



def overlaps_with_output(facet, output):
    '''
    Is this facet already in the list?
    '''
    for i in output:
        if len(set(facet.split(" ")).intersection(i.split(" "))) > 0:
            return True
    return False


def make_dataframe(p, facets, results, q_pubdates, aliases):
    '''
    Checks if given username and password match correct credentials.
    :param p: params
    :type username: Parameters
    :param facets: facets
    :type: unicode
    :returns: pandas df. Columns get 1 if facet appears in pubdate
    '''
    df = pd.DataFrame()
    df['id'] = results
    df['pd'] = q_pubdates
    df[p.q] = [1 for i in q_pubdates]
    pub_index = get_pubdate_index()
    for facet in facets:
        alias = [pub_index[a] for a in aliases[facet]]
        facet_dates = set([i for i in set([i for i in itertools.chain(*alias)]).union(pub_index[facet])])
        gus = [int(p) for p in [p in facet_dates for p in q_pubdates]]
        df[facet] = gus
    return df


def get_breakdown(df, facet):
    '''
    Gets a per-year breakdown of facet
    :param facet: the facet that needs to be broken down by date
    :type facet: unicode?
    :param df: dataframe, facet cols get 1 if facet appears
    :type: panadas df
    :returns: json holding count per date bin for facet
    '''
    tmp = df
    tmp = tmp.groupby([tmp['pd'].map(lambda x: x.year), tmp[facet]]).sum()
    tmp = tmp[tmp[facet] != 0][facet].unstack(0).fillna(0)
    return tmp.to_json()


def passes_one_word_heuristic(on_deck):
    '''
    Short check for meaningless 1-grams like "commission"
    '''
    if len(on_deck.split(" ")) < 2 and sum(1 for l in on_deck if l.isupper()) < 2:
        return False
    return True


class Models(object):

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
    def get_message(l_results, params, len_doc_list, PAGE_LENGTH):
        if params.page < 1:
            params.page == 1
        start = params.page * PAGE_LENGTH
        end = params.page * PAGE_LENGTH + PAGE_LENGTH
        output = "{} total results for {}. Showing {} thru {}".format(l_results, params.q, start, end)
        return output

    @staticmethod
    def get_parameters(request):
        '''get parameters'''
        output = Parameters()

        output.q = request.args.get('q')

        output.term = request.args.get('term')

        output.termtype = request.args.get('termtype')

        output.page = request.args.get('page')

        try:
            output.page = int(output.page)
        except:
            output.page = 1

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
    def get_doclist(results, params, PAGE_LENGTH):
        mt = get_metadata_file()
        output = []
        if params.page < 1:
            params.page == 1
        # chop off to only relevant results
        results = results[params.page * PAGE_LENGTH:(params.page * PAGE_LENGTH + PAGE_LENGTH)]
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
        return output, all_aliases
