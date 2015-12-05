import ipdb
import datetime
import threading
import pylru
import json
import time
import datetime as dt
import itertools
from dateutil.parser import parse
from experiment.models import make_dataframe
from experiment.models import get_breakdown
from flask import Flask
from rookie.rookie import Rookie
from flask import request
from experiment.views import Views
from collections import defaultdict
from experiment.models import Models, Parameters
from snippets.prelim import get_snippet
from experiment import LENS_CSS, BANNER_CSS, IP, ROOKIE_JS, ROOKIE_CSS
from experiment import log
from experiment import PAGE_LENGTH
from whooshy.reader import query_whoosh
from whooshy.reader import query_subset
from collections import OrderedDict
from experiment.models import get_metadata_file, get_pubdate_index

app = Flask(__name__)

cache = pylru.lrucache(100)

views = Views(LENS_CSS, BANNER_CSS, IP, ROOKIE_JS, ROOKIE_CSS)

'''

def tokens_to_sentence(sentence_tokens):
    sentence = ""
    for token in sentence_tokens:
        sentence = sentence + " " + sentence_tokens[token]['word']
    return sentence.strip(" ")


def worker(queue, snippets_dict):
    for index, q_item in enumerate(queue):
        key = q_item[0][0] + "-" +  q_item[1]
        sentences = []
        for item in q_item[2]:
            pubd = item[1]['pubdate']
            docid = item[0]
            for sentence in item[1]['sentences']:
                sentences.append((sentence, pubd, item[0], docid))
         
        # snippet returns:
        # tokens, datetime, article_id, ?, qtokenindex, ftokenindex)
        cache[key] = get_snippet(q_item[0][0], q_item[1], sentences, q_item[3].q)
        print "got snippet {}|{}|{}".format(q_item[0][0], q_item[1], q_item[3].q)

'''

@app.route('/', methods=['GET'])
def index():
    log.info("index routing")
    return views.get_start_page()

'''
@app.route('/get_snippet_post', methods=['POST'])
def get_snippet_post():
    term = request.args.get('term')
    termtype = request.args.get('termtype')
    query = request.args.get('q')
    key = term + "-" + termtype
    try:
        snippet = cache.peek(key) # TODO: handle cache failures
        snippet = list([list(i) for i in snippet])
        snippet_json = []
        for s in snippet:
            s[0] = list(s[0])
        for s_index, sentence in enumerate(snippet):
            tokens = [i for i in sentence[0] if i != ","]  #TODO this is only one sentence
            qtoks = set(query.split(" ")).intersection(set(tokens))
            ftoks = set(term.split(" ")).intersection(set(tokens))
            qftoks = qtoks.union(ftoks)
            left = []
            box_l = []
            center = []
            box_r = []
            right = []
            slots = [left, box_l, center, box_r, right]
            slots_index = 0
            place_keeper = 0
            i = 0
            looking_for_qf = False
            while tokens[i] not in qftoks and i < len(tokens) - 1:
                slots[slots_index].append(str(tokens[i]))
                i +=1
            slots_index += 1
            while tokens[i] in qftoks and i < len(tokens) - 1:
                slots[slots_index].append(str(tokens[i]))
                i += 1
            slots_index += 1
            while tokens[i] not in qftoks and i < len(tokens) - 1:
                slots[slots_index].append(str(tokens[i]))
                i +=1
            slots_index += 1
            while tokens[i] in qftoks and i < len(tokens) - 1:
                slots[slots_index].append(str(tokens[i]))
                i +=1
            slots_index += 1
            while tokens[i] not in qftoks and i < len(tokens) - 1:
                slots[slots_index].append(str(tokens[i]))
                i +=1
            
            sentence_json = {}
            sentence_json['time'] = snippet[s_index][1].strftime("%b %d<br>%Y").replace(' 0', ' ')
            sentence_json['l'] = slots[0]
            sentence_json['col_l'] = slots[1]
            sentence_json['c'] = slots[2]
            sentence_json['col_r'] = slots[3]
            sentence_json['r'] = slots[4]
            snippet_json.append(sentence_json)



    except KeyError: # TODO FIX
        snippet = "waiting for cache fix TODO"
    
    return json.dumps(snippet_json)


@app.route('/detail', methods=['GET'])
def detail():

    p = Models.get_parameters(request)

    snippets_dict = defaultdict(str)

    query_back = query_whoosh(p.q)

    docid = p.docid

    q_and_t = []

    # TODO: this logic should go in query_whoosh
    for termtype in query_back[1].keys():
        for term in query_back[1][termtype]:
            q_and_t.append((term[0], termtype))

    dt = Models.get_tokens(docid)

    dt = OrderedDict(sorted(dt.items(), key=lambda t: int(t[0])))

    tokens = [dt[i] for i in dt.keys()]

    headline = Models.get_headline(docid)

    pubdate = Models.get_pub_date(docid)

    view = Views().get_detail_page(p.q, q_and_t, headline, pubdate, tokens, LENS_CSS, BANNER_CSS)

    return view

@app.route('/testing', methods=['GET'])
def testing():

    p = Models.get_parameters(request)

    snippets_dict = defaultdict(str)

    query_back = query_whoosh(p.q)

    q_and_t = []
    queue = []
    for termtype in query_back[1].keys():
        for term in query_back[1][termtype]:
            if len(set(p.q.split(" ")).intersection(set(term[0].split(" ")))) == 0:
                subset = query_subset(query_back[0], term, termtype)
                queue.append((term, termtype, subset, p,))
                q_and_t.append((term[0], termtype))
    t = threading.Thread(target=worker, args=(queue, snippets_dict))
    t.start()

    view = Views().get_results_page_relational_overview(p.q, q_and_t, LENS_CSS, BANNER_CSS)

    return view


@app.route('/testing', methods=['GET'])
def testing():

    p = Models.get_parameters(request)

    snippets_dict = defaultdict(str)

    query_back = query_whoosh(p.q)

    q_and_t = []
    queue = []
    for termtype in query_back[1].keys():
        for term in query_back[1][termtype]:
            if len(set(p.q.split(" ")).intersection(set(term[0].split(" ")))) == 0:
                subset = query_subset(query_back[0], term, termtype)
                queue.append((term, termtype, subset, p,))
                q_and_t.append((term[0], termtype))
    t = threading.Thread(target=worker, args=(queue, snippets_dict))
    t.start()

    view = Views().get_results_page_relational_overview(p.q, q_and_t, LENS_CSS, BANNER_CSS)

    return view
'''

@app.route('/facets', methods=['GET'])
def testing():

    log.debug('facets')

    params = Models.get_parameters(request)

    #TODO pagination
    results = Models.get_results(params)

    log.debug('got results')

    dates_bins, facets = Models.get_facets(params, results, 3)

    log.debug('got bins and facets')

    doc_list = Models.get_doclist(results, params, PAGE_LENGTH)

    status = Models.get_message(len(results), params, len(doc_list), PAGE_LENGTH)

    keys = dates_bins[dates_bins.keys()[0]].keys()

    datas = {}
    for f in facets:
        datas[f] = ["count"] + [dates_bins[f][o] for o in dates_bins[f].keys()]

    view = views.get_q_response(params, doc_list, facets, keys, datas, status, len(results))

    return view

@app.route('/bigviz', methods=['GET'])
def bigviz():

    log.debug('facets')

    params = Models.get_parameters(request)

    results = Models.get_results(params)
    print "got results"

    facets, aliases = Models.get_facets(params, results, 3)
    print "got facets"

    mt = get_metadata_file()

    print "got metadata"
    metadata = [mt[r] for r in results]

    q_pubdates = [parse(h["pubdate"]) for h in metadata]
    print "parsed dates"
    # df = make_dataframe(params, facets, results, q_pubdates, aliases)

    bins = {}
    for f in facets:
        print "making df"
        df = make_dataframe(params, facets, results, q_pubdates, aliases)
        print "processing df"
        bins[f] = get_breakdown(df, f)

    #datas = ["count"] + [len(bins[b]) for b in bins]
    #labels = ["labels"] + [b for b in bins]
    datas = []
    labels = []
    all_keys = [parse(o) for o in set(itertools.chain(*[json.loads(bins[f]).keys() for f in facets]))]
    all_keys.sort()

    items = [json.loads(p) for p in [bins[k] for k in bins]]

    labels = ["x"] + [k.strftime("%Y-%m-%d") for k in all_keys]
    
    all_keys = [o.strftime("%Y") for o in all_keys]
    
    facets = []
    for key in bins.keys():
        facet_data = []
        bin_json = json.loads(bins[key])
        for date_key in all_keys:
            try:
                facet_data.append(bin_json[date_key]['1'])
            except KeyError:
                pass
        facet_data = [str(key)] + facet_data
        facets.append(facet_data)

    view = views.get_big_viz(params, datas, labels, facets)

    return view

if __name__ == '__main__':
    app.run(debug=True)
