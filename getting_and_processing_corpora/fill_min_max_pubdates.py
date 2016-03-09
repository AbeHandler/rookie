'''
Load to a db
'''
from webapp import CONNECTION_STRING
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dateutil import parser as dp
import argparse


def main():
    '''
    main
    '''
    parser = argparse.ArgumentParser()

    parser.add_argument('--corpus',
                        help='the thing in the middle of corpus/{}/raw',
                        required=True)
    parser.parse_args()

    engine = create_engine(CONNECTION_STRING)
    ession = sessionmaker(bind=engine)
    session = ession()
    txt = "select * from doc_metadata"
    print [dp.parse(i[1]["pubdate"]) for i in session.execute(txt)]

main()
