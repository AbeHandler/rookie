'''
Load to a db
'''
from webapp import CONNECTION_STRING
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dateutil import parser as dp
from tqdm import tqdm
import argparse
import json
import dateutil.parser
import datetime



parser = argparse.ArgumentParser()

parser.add_argument('--corpus',
                    help='the thing in the middle of corpus/{}/raw',
                    required=True)

args = parser.parse_args()

with open("db/{}.doc_metadata.json".format(args.corpus), "r") as inf:
    dt = json.load(inf)

pds = []
for d in tqdm(dt):
    pd = json.loads(dt[d])["pubdate"]
    y, m, d = pd.split("-")
    x = datetime.datetime(int(y), int(m), int(d))
    pds.append(x)

with open("db/{}.pubdates.json".format(args.corpus), "w") as of:
    json.dump({"min": min(pds).strftime("%Y-%m-%d"), "max": max(pds).strftime("%Y-%m-%d")}, of)

    
