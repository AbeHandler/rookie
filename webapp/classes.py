'''
Classes used in the webapp
'''
import datetime
from experiment import PG_HOST
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

CONNECTION_STRING = 'postgresql://%s:%s@%s:5432/%s' % (
    'rookie', # user
    'rookie', # pw
    PG_HOST,
    'rookie', # db
)

import socket
if 'btop2' in socket.gethostname():
    CONNECTION_STRING = "postgresql://rookie:rookie@192.168.99.100:32770/rookie"


Base = declarative_base()


class Document(Base):
    '''
    An article
    '''
    __tablename__ = 'docs'

    id = Column(Integer, primary_key=True)
    pubdate = Column(Date, nullable=False)
    headline = Column(String, nullable=False)

    def __init__(self, pubdate, headline, docid):
        self.pubdate = pubdate
        self.headline = headline
        self.id = docid

    def __repr__(self):
        return "<Doc (id='%s', date=%s>, headline=%s>" % (
            self.id, self.pubdate, self.headline)


class Facet(Base):
    '''
    Any facet
    '''
    __tablename__ = 'facets'

    id = Column(Integer, primary_key=True)
    text = Column(String, nullable=False)

    def __init__(self, text, facetid):
        self.text = text
        self.id = facetid

    def __repr__(self):
        return "<facet (id='%s', text=%s>" % (
            self.id, self.text)


class DocumentFacet(Base):
    '''
    Link table: docs to facets
    '''
    __tablename__ = 'docs_facets'

    id = Column(Integer, primary_key=True)
    docid = Column(Integer, ForeignKey("docs.id"))
    facetid = Column(Integer, ForeignKey("facets.id"))

    def __init__(self, docid, facetid):
        self.docid = docid
        self.facetid = facetid

    def __repr__(self):
        return "<DocFacet (doc='%s', facet=%s>" % (
            self.docid, self.facetid)


class Sentence(Base):
    '''
    A sentence in an article
    '''
    __tablename__ = 'sentences'

    id = Column(Integer, primary_key=True)
    text = Column(String, nullable=False)
    articleid = Column(Integer, ForeignKey("docs.id"))
    sentence_no = Column(Integer, nullable=False)

    def __init__(self, text, articleid, sentence_no):
        self.text = text
        self.articleid = articleid
        self.sentence_no = sentence_no

    def __repr__(self):
        return "<sentence (id='%s', text=%s>" % (
            self.id, self.text
        )



def remake_db():
    '''
    Creates the database via SQLAlchemy.
    '''

    engine = create_engine(CONNECTION_STRING)
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    remake_db()
