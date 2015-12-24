import datetime
import ipdb
import itertools
import time
from experiment.classes import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc
from experiment.classes import CONNECTION_STRING

start_time = time.time()
engine = create_engine(CONNECTION_STRING)
Session = sessionmaker(bind=engine)
session = Session()
print "[*] building the session took {}".format(start_time - time.time())

def get_q_and_f(docid, q, f):
    #return session.query(Sentence).filter_by(articleid=docid).order_by(Sentence.sentence_no.desc()).limit(2).all()
    return session.query(Sentence).filter_by(articleid=docid).filter(Sentence.text.ilike("%" + q + "%")).filter(Sentence.text.ilike("%" + f + "%")).order_by(Sentence.sentence_no.desc()).limit(2).all()


def get_q_or_f(docid, q, f):
    #return session.query(Sentence).filter_by(articleid=docid).order_by(Sentence.sentence_no.desc()).limit(1).all()
    return session.query(Sentence).filter_by(articleid=docid).filter(Sentence.text.ilike("%" + q + "%") | Sentence.text.ilike("%" + f + "%")).order_by(Sentence.sentence_no.desc()).limit(1).all()


def get_q(docid, q):
    #return session.query(Sentence).filter_by(articleid=docid).order_by(Sentence.sentence_no.desc()).limit(2).all()
    return session.query(Sentence).filter_by(articleid=docid).filter(Sentence.text.ilike("%" + q + "%")).order_by(Sentence.sentence_no.desc()).limit(2).all()
    
    
def get_anything(docid):
    #return session.query(Sentence).filter_by(articleid=docid).order_by(Sentence.sentence_no.desc()).limit(2).all()
    return session.query(Sentence).filter_by(articleid=docid).order_by(Sentence.sentence_no.desc()).limit(2).all()
    

def find_sentences_q(docid, q):
    sentences = []
    sentences = sentences + get_q(docid, q) # try to get 2 sentences containg q
    if len(sentences) == 2:
        return sentences
    if len(sentences) == 2:
        return sentences
    sentences = sentences + get_anything(docid)
    return sentences[0:2]

def find_sentences_q_and_f(docid, q, f):
    sentences = []
    sentences = sentences + get_q_and_f(docid, q, f) # try to get 2 sentences containg q
    if len(sentences) == 2:
        return sentences
    sentences = sentences + get_q_or_f(docid, q, f) # try to get 2 sentences containg q
    if len(sentences) == 2:
        return sentences
    sentences = sentences + get_anything(docid)
    return sentences[0:2]


def get_snippet_pg(docid, q, f=None):
    if f is not None:
        sentences = find_sentences_q_and_f(docid, q, f)
    if f is None:
        sentences = find_sentences_q(docid, q)
    assert len(sentences) == 2
    # sentences = comress_sentences(sentences)
    # sentences.sort(key=lambda x:x.sentence_no)
    sentences.sort(key=lambda x:x.sentence_no)
    return sentences