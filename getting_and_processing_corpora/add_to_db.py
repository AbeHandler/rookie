import argparse
from webapp import CONNECTION_STRING
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

parser = argparse.ArgumentParser()
parser.add_argument('--corpus', help='the thing in the middle of corpus/{}/raw', required=True)
args = parser.parse_args()


engine = create_engine(CONNECTION_STRING)
Session = sessionmaker(bind=engine)
session = Session()


rows = session.connection().execute("select * from corpora")

all_corpora = []
for r in rows:
    all_corpora.append(r[1].strip())

rows = session.connection().execute("select * from corpora")

allids = []
for r in rows:
    allids.append(r[0])

newmax = max(allids) + 1

if args.corpus not in all_corpora:
    session.connection().execute("INSERT into corpora (corpusid, corpusname) VALUES ('{}', '{}');".format(newmax, args.corpus))
    print "added to db"

session.commit()