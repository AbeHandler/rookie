import datetime
from experiment.classes import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc
from experiment.classes import CONNECTION_STRING

engine = create_engine(CONNECTION_STRING)
Session = sessionmaker(bind=engine)
session = Session()

def get_snippet(docid, q, f):
    sentences = session.query(Sentence).filter_by(articleid=docid).filter(Sentence.text.ilike("%" + q + "%")).order_by(Sentence.amount.desc()).all()
    print [s.text for s in sentences]

get_snippet(2, "Lens", "")