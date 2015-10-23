import pdb
import pickle
import threading
from dateutil.parser import parse
from flask import Flask
from flask import render_template
from flask import request
from experiment import log
from experiment.views import Views
from collections import defaultdict
from experiment.models import Models, Parameters
from snippets.prelim import DocFetcher, get_snippet
from rookie import page_size
from experiment import LENS_CSS, BANNER_CSS
from rookie import (
    log
)

app = Flask(__name__)


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
        print index
        get_snippet(q_item[0][0], q_item[1], documents_to_sentences(q_item[2]), q_item[3].q)
    return snippets_dict


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
    return "heeeeer"


@app.route('/testing', methods=['GET'])
def testing():

    log.debug('/search/ data:')

    p = Models.get_parameters(request)

    snippets_dict = defaultdict(str)

    # df = DocFetcher()
    # tops, docs = df.search_for_documents(p)

    # pickle.dump(tops, open("tops", "w"))
    # pickle.dump(docs, open("docs", "w"))
    tops = pickle.load(open("tops", "r"))
    docs = pickle.load(open("docs", "r"))

    q_and_t = []
    queue = []
    for termtype in tops:
        for term in tops[termtype]:
            subset = [d for d in docs['docs'] if termtype in d.keys() and term[0] in d[termtype]]
            queue.append((term, termtype, subset, p,))
            q_and_t.append((term, termtype))
    t = threading.Thread(target=worker, args=(queue, snippets_dict))
    t.start()
    
    print "here so fast"

    view = Views().get_results_page_relational_overview(p.q, q_and_t, LENS_CSS, BANNER_CSS)

    # view = Views().get_results_page_relational(p.q, q_and_t, LENS_CSS, BANNER_CSS)

    return view

if __name__ == '__main__':
    app.run(debug=True)
