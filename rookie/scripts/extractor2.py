import csv
import pdb
import datetime

from rookie.db import GramNER
from rookie.db import Link
from rookie import CONNECTION_STRING
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

all_things = []

engine = create_engine(CONNECTION_STRING)
Session = sessionmaker(bind=engine)
session = Session()


def add_if_new(string):
    indb = session.query(GramNER).filter(GramNER.string == string).count()
    if indb == 0:
        gramner = GramNER(string)
        session.add(gramner)
        session.commit()
        return
    if indb == 1:
        return


def add_link(row):
    id1 = session.query(GramNER).filter(GramNER.string == row[0]).first().id
    id2 = session.query(GramNER).filter(GramNER.string == row[1]).first().id
    pubdate = row[3]
    url = row[2]
    yr, mo, dy = pubdate.split(" ")[0].split("-")
    pubdate = datetime.date(int(yr), int(mo), int(dy))
    link = Link(id1, id2, pubdate, url)
    session.add(link)
    session.commit()
    return


with open('graph.csv', 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=',',
                        quotechar='"')
    for row in reader:
        all_things.append(row)
        if len(all_things) % 10000 == 0:
            print len(all_things)


for i in set([i[0] for i in all_things]):
    add_if_new(i)

for j in all_things:
    try:
        add_link(j)
    except KeyError:
        print j
