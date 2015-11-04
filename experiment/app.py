import pdb
import pickle
import datetime
import threading
import pylru
from dateutil.parser import parse
from flask import Flask
from flask import render_template
from flask import request
from experiment import log
from experiment.views import Views
from collections import defaultdict
from experiment.models import Models, Parameters
from snippets.prelim import get_snippet
from rookie import page_size
from experiment import LENS_CSS, BANNER_CSS
from rookie import (
    log
)
from whooshy.reader import query_whoosh
from whooshy.reader import query_subset
from snippets.prelim import get_snippet

app = Flask(__name__)

cache = pylru.lrucache(100)


def tokens_to_sentence(sentence_tokens):
    sentence = ""
    for token in sentence_tokens:
        sentence = sentence + " " + sentence_tokens[token]['word']
    return sentence.strip(" ")


def documents_to_sentences(subset):
    output = []
    for docno, doc in enumerate(subset):
        pubdate = doc['pubdate']
        for sentenceno in doc['sentences']:
            sentence = tokens_to_sentence(doc['sentences'][sentenceno]['tokens'])
            output.append((unicode(sentence), pubdate, unicode(str(docno) + "-"+ str(sentenceno))))
    return tuple(output)


def worker(queue, snippets_dict):
    print len(queue)
    for index, q_item in enumerate(queue):       
        key = q_item[0][0] + "-" +  q_item[1]
        sentences = []
        for item in q_item[2]:
            for sentence in item[1]['sentences']:
                sentences.append(sentence)
        pdb.set_trace()
        cache[key] = get_snippet(q_item[0][0], q_item[1], sentences, q_item[3].q)


@app.route('/')
def index():
    log.info("index routing")
    return render_template('index.html',
                           lens_css=LENS_CSS,
                           banner_css=BANNER_CSS)


@app.route('/old/results', methods=['GET'])
def results_old():

    log.debug('/search/ data:')

    params = Models.get_parameters(request)

    log.debug('got params')

    results, tops = Models().search(params)

    log.debug('got results and tops')

    results = [r for r in results]

    pages = Models.get_pages(len(results), page_size)

    log.debug('got pages')

    message = Models().get_message(params, pages, len(results))

    log.debug('got message')

    # page_results = results[params.page * 10:params.page * 10+10]

    page_results = results
    results.sort(key=lambda x: parse(x['fields']['pubdate']))
    view = Views().get_results2_page(params.q, page_results, tops, len(results), message, pages, LENS_CSS, BANNER_CSS)

    return view


@app.route('/results', methods=['GET'])
def results():

    log.debug('/search/ data:')

    params = Models.get_parameters(request)

    log.debug('got params')

    results, tops = Models().search(params, snippets=True)

    log.debug('got results and tops')

    # turn into a mutable list. was tuples for for caching
    results = [r for r in results]
    tops = [o for o in tops]
    view = Views().get_results_page_relational(params.q, tops, LENS_CSS, BANNER_CSS)

    return view



@app.route('/get_snippet_post', methods=['POST'])
def get_snippet_post():
    term = request.args.get('term')
    termtype = request.args.get('termtype')
    key = term + "-" + termtype
    snippet = cache.peek(key) # TODO: handle cache failures

    return Views().print_snippet(snippet)


@app.route('/testing', methods=['GET'])
def testing():

    log.debug('/search/ data:')

    p = Models.get_parameters(request)

    snippets_dict = defaultdict(str)

    before = datetime.datetime.now()

    query_back = query_whoosh(p.q)

    after = datetime.datetime.now()

    log.debug('fetching documents took {}'.format((after - before).seconds))

    q_and_t = []
    queue = []
    for termtype in query_back[1].keys():
        for term in query_back[1][termtype]:
            subset = query_subset(query_back[0], term, termtype)
            queue.append((term, termtype, subset, p,))
            q_and_t.append((term[0], termtype))
    t = threading.Thread(target=worker, args=(queue, snippets_dict))
    t.start()
    
    #print "here so fast"
    
    view = Views().get_results_page_relational_overview(p.q, q_and_t, LENS_CSS, BANNER_CSS)

    # view = Views().get_results_page_relational(p.q, q_and_t, LENS_CSS, BANNER_CSS)

    return view

if __name__ == '__main__':
    app.run(debug=True)
