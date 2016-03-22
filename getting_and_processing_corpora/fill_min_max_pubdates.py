'''
Load to a db
'''
from webapp import CONNECTION_STRING
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dateutil import parser as dp
import argparse
import dateutil.parser


def main():
    '''
    main
    '''
    parser = argparse.ArgumentParser()

    parser.add_argument('--corpus',
                        help='the thing in the middle of corpus/{}/raw',
                        required=True)

    parser.add_argument('--min',
                        required=False)
    parser.add_argument('--max',
                        required=False)
    args = parser.parse_args()

    engine = create_engine(CONNECTION_STRING)
    ession = sessionmaker(bind=engine)
    session = ession()
    if args.min is None or args.max is None: 
        txt = "select * from doc_metadata"
        mind = min([dp.parse(i[1]["pubdate"]) for i in session.execute(txt)])
        maxd = max([dp.parse(i[1]["pubdate"]) for i in session.execute(txt)])
    else:
        mind = dateutil.parser.parse(args.min)
        maxd = dateutil.parser.parse(args.max)
    strg = "update corpora set first_story ='" + mind.strftime("%Y-%m-%d") + "' where corpusname='" + args.corpus + "'"
    session.execute(strg)
    strg2 = "update corpora set last_story ='" + maxd.strftime("%Y-%m-%d") + "' where corpusname='" + args.corpus + "'"
    session.execute(strg2)
    session.commit()
main()
