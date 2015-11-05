import pdb
import datetime
import threading
import pylru
from flask import Flask
from flask import request
from experiment.views import Views
from collections import defaultdict
from experiment.models import Models, Parameters
from snippets.prelim import get_snippet
from experiment import LENS_CSS, BANNER_CSS
from experiment import (
     log
)
from whooshy.reader import query_whoosh
from whooshy.reader import query_subset

app = Flask(__name__)

cache = pylru.lrucache(100)


def tokens_to_sentence(sentence_tokens):
    sentence = ""
    for token in sentence_tokens:
        sentence = sentence + " " + sentence_tokens[token]['word']
    return sentence.strip(" ")


def worker(queue, snippets_dict):
    print len(queue)
    for index, q_item in enumerate(queue):       
        key = q_item[0][0] + "-" +  q_item[1]
        sentences = []
        for item in q_item[2]:
            pubd = item[1]['pubdate']
            for sentence in item[1]['sentences']:
                sentences.append((sentence, pubd, item[0]))
        cache[key] = get_snippet(q_item[0][0], q_item[1], sentences, q_item[3].q)
        print get_snippet(q_item[0][0], q_item[1], sentences, q_item[3].q)


@app.route('/', methods=['GET'])
def index():
    log.info("index routing")
    return Views().get_start_page(LENS_CSS, BANNER_CSS)


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
    
    view = Views().get_results_page_relational_overview(p.q, q_and_t, LENS_CSS, BANNER_CSS)

    return view


if __name__ == '__main__':
    app.run(debug=True)
