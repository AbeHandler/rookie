import datetime
from experiment.classes import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc
from experiment.classes import CONNECTION_STRING

engine = create_engine(CONNECTION_STRING)
Session = sessionmaker(bind=engine)
session = Session()


def get_q_and_f(docid, q, f):
    return session.query(Sentence).filter_by(articleid=docid).filter(Sentence.text.ilike("%" + q + "%")).order_by(Sentence.sentence_no.desc()).limit(2).all()


def get_q_or_f(docid, q, f):
    return session.query(Sentence).filter_by(articleid=docid).filter(Sentence.text.ilike("%" + q + "%") or Sentence.text.ilike("%" + f + "%")).order_by(Sentence.sentence_no.desc()).limit(1).all()


def get_q(docid, q):
    return session.query(Sentence).filter_by(articleid=docid).filter(Sentence.text.ilike("%" + q + "%")).order_by(Sentence.sentence_no.desc()).limit(2).all()
    
    
def get_anything(docid):
    return session.query(Sentence).filter_by(articleid=docid).order_by(Sentence.sentence_no.desc()).limit(2).all()
    

def find_sentences_q(docid, q):
    sentences = get_q(docid, q) # try to get 2 sentences containg q
    if len(sentences) == 2:
        return sentences
    if len(sentences) == 2:
        return sentences
    sentences = sentences + get_anything(docid)
    return sentences[0:2]


def get_snippet_pg(docid, q, f=None):
    if f is not None:
        sentences = find_sentences_f(docid, q, f)
    if f is None:
        sentences = find_sentences_f(docid, q, f)
    assert len(sentences) == 2
    # sentences = comress_sentences(sentences)
    return sentences