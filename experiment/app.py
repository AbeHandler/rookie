import datetime
import threading
import pylru
import json
import time
import redis
import ujson
import datetime as dt
import ipdb
from dateutil.parser import parse
from experiment.models import make_dataframe
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

MT = get_metadata_file()

PI = get_pubdate_index()

alias_table = defaultdict(lambda : defaultdict(list))

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

@app.route("/get_doc_list", methods=['POST'])
def get_doc_list():

    params = Models.get_parameters(request)

    results = Models.get_results(params)

    if params.detail == params.q:
        # the user wants date detail for Q
        results = Models.date_filter(results, params)
        status = "Documents containing {} from {} to {}".format(params.q, params.startdate.year, params.enddate.year)
    else:
        results = Models.date_filter(results, params)
        results = Models.f_occurs_filter(results, params, alias_table[params.q][params.detail])
        status = "Documents containing {} and {} from {} to {}".format(params.q, params.detail, params.startdate.year, params.enddate.year)
    doc_list = Models.get_doclist(results, params, PAGE_LENGTH)
    return views.get_doc_list(doc_list, params, status)


@app.route('/facets', methods=['GET'])
def testing():

    log.debug('facets')

    global alias_table

    params = Models.get_parameters(request)

    results = Models.get_results(params)

    log.debug('got results')

    facets, aliases = Models.get_facets(params, results, 9)

    for f in facets:
        alias_table[params.q][f] = aliases[f]

    log.debug('got bins and facets')

    doc_list = Models.get_doclist(results, params, PAGE_LENGTH)

    status = Models.get_message(len(results), params, len(doc_list), PAGE_LENGTH)

    metadata = [MT[r] for r in results]

    q_pubdates = [parse(h["pubdate"]) for h in metadata]
    print "parsed dates"

    df = make_dataframe(params, facets, results, q_pubdates, aliases)
    df = df.groupby([df['pd'].map(lambda x: x.year)]).sum().unstack(0).fillna(0)
    
    facet_datas = []
    for f in facets:
        facet_datas.append([str(f).replace("_", " ")] + list(df[f]))

    datas = [str(params.q)] + list(df[params.q])
    keys = ["x"] + [str(i) + "-01-01" for i in df[params.q].axes[0]]

    view = views.get_q_response(params, doc_list, facet_datas, keys, datas, status, len(results))

    return view

@app.route('/bigviz', methods=['GET'])
def bigviz():

    log.debug('facets')

    global alias_table

    params = Models.get_parameters(request)

    start_time = time.time()
    results = Models.get_results(params)
    print "getting results took {}".format(start_time - time.time())
    print "got results"

    start_time = time.time()
    facets, aliases = Models.get_facets(params, results, 3)
    print "getting facets took {}".format(start_time - time.time())
    print "got facets"

    for f in facets:
        alias_table[params.q][f] = aliases[f]

    print "got metadata"
    metadata = [MT[r] for r in results]

    q_pubdates = [parse(h["pubdate"]) for h in metadata]
    print "parsed dates"
    # df = make_dataframe(params, facets, results, q_pubdates, aliases)

    df = make_dataframe(params, facets, results, q_pubdates, aliases)
    df = df.groupby([df['pd'].map(lambda x: x.year)]).sum().unstack(0).fillna(0)
    
    facet_datas = []
    for f in facets:
        facet_datas.append([str(f)] + list(df[f]))

    datas = [str(params.q)] + list(df[params.q])
    labels = ["x"] + [str(i) + "-01-01" for i in df[params.q].axes[0]]

    view = views.get_big_viz(params, labels, facet_datas, datas)

    return view

if __name__ == '__main__':
    app.run(debug=True)
