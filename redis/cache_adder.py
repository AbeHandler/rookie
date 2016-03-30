import argparse
import redis
import ujson as json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from webapp.models import getcorpusid
from webapp.models import get_doc_metadata
from webapp import CONNECTION_STRING

r = redis.StrictRedis(host='localhost', port=6379, db=0)

parser = argparse.ArgumentParser()
parser.add_argument('--ids', nargs='+', type=unicode)

args = parser.parse_args()

corpus = args.ids[0]
docids = args.ids[1:]


ENGINE = create_engine(CONNECTION_STRING)
SESS = sessionmaker(bind=ENGINE)
SESSION = SESS()


for docid in docids:
    try:
        corpusid = getcorpusid(corpus)
        row = SESSION.connection().execute("select data from doc_metadata where docid=%s and corpusid=%s", docid, corpusid).fetchone()
        md = row[0]
        sentences_big = "###$$$###".join([sent["as_string"] for sent in md["sentences"]])
        r.set("{}-{}".format(docid, corpus), sentences_big)
    except TypeError:
        print "could not find doc number {} for corpus {}".format(docid, corpus)

