'''
Classes used in the webapp
'''
import datetime
import json
import ipdb
from webapp import PG_HOST, ROOKIE_PW
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine


CONNECTION_STRING = 'postgresql://%s:%s@%s:5432/%s' % (
    'rookie', # user
    ROOKIE_PW, # pw
    PG_HOST,
    'rookie', # db
)

import socket
if 'btop2' in socket.gethostname():
    CONNECTION_STRING = "postgresql://rookie:rookie@192.168.99.100:32770/rookie"


class IncomingFile(object):
    """
    An incoming file wraps a Document + metadata
    It hides all dealings with the file system
    """
    def __init__(self, filename):
        try:
            with (open(filename, "r")) as infile:
                ipdb.set_trace()
                self.doc = None
                json_in = json.loads(infile.read())
                self.url = json_in['url']
                self.headline = json_in['headline']
                self.pubdate = json_in['timestamp'].split(" ")[0]
                data = json_in['lines']
                self.doc = Document(data)
                self.doc.coreferences = None # not being used right now
                self.filename = filename
        except UnicodeEncodeError:
            pass

Base = declarative_base()


class Document(object):

    '''
    This is an abstraction over output from proc.document_parse()
    running in "pos" mode from the python NLP wrapper
    '''

    def __init__(self, json_output, coreferences=None):
        '''
        Initialize w/ the json output.
        Coreferences are optional
        '''
        try:
            sentences_json = json_output['sentences']
        except KeyError:
            sentences_json = []
        sentences = []
        people = []
        organizations = []
        ngrams = []
        for i in range(0, len(sentences_json)):
            sentence = Sentence(sentences_json[i], i)
            sentences.append(sentence)
            ngrams = ngrams + sentence.ngrams
        self.ngrams = ngrams
        self.sentences = sentences
        text = ""
        for sentence in self.sentences:
            text = text + " ".join([w.raw for w in sentence.tokens])
        self.full_text = text
        sentence_tokens = [s.tokens for s in self.sentences]
        self.tokens = list(chain(*sentence_tokens))


class Sentence(object):

    def get_ner(self, json_sentence, tokens):
        ner = json_sentence['ner']
        counter = 0
        output = []
        while counter < len(ner):
            ne_type = ner[counter]
            if ne_type != "O":
                ner_to_add = [tokens[counter]]
                try:
                    while ner[counter + 1] == ne_type:
                        ne_type = ner[counter + 1]
                        counter = counter + 1
                        next_token = tokens[counter]
                        ner_to_add.append(next_token)
                except IndexError:  # reached the end of the ner
                    pass
                output.append(NER(ner_to_add, ne_type, self.sentence_no))
            counter = counter + 1
        return output

    def get_ngrams(self):
        '''
        :param words: a list of all word tokens in a document
        :type words: Token
        '''
        ngrams = N_Grammer()
        grams = []
        # ngrams 1 thru 4
        for i in range(1, 5):
            grams = grams + ngrams.get_syntactic_ngrams(self.tokens, i)
        return grams

    def __init__(self, json_sentence, sentence_no):
        '''
        Initialize w/ the json output
        '''
        self.sentence_no = sentence_no
        tokens = json_sentence['tokens']
        lemmas = json_sentence['lemmas']
        poses = json_sentence['pos']
        ner = json_sentence['ner']
        self.deps = json_sentence['deps_basic']
        assert len(tokens) == len(lemmas)
        assert len(poses) == len(lemmas)
        assert len(tokens) == len(poses)
        sentence_tokens = []
        for i in range(0, len(tokens)):
            t = Token(tokens[i], poses[i], lemmas[i], i, sentence_no, ner[i])
            sentence_tokens.append(t)
        self.tokens = sentence_tokens
        self.ngrams = self.get_ngrams()
        self.ner = self.get_ner(json_sentence, self.tokens)

    def __repr__(self):
        return " ".join([i.raw for i in self.tokens])

class Token(object):

    def __init__(self, raw_token, pos, lemma_form, token_no, sentence_no, ner):
        '''
        Initialize w/ the json output
        '''
        # Store tokens as unicode, but remove non standard chars for now #TODO
        self.raw = raw_token.encode("ascii", "ignore").decode()
        self.pos = pos
        self.ner_tag = ner
        self.lemma_form = lemma_form
        self.token_no = token_no
        self.sentence_no = sentence_no

    def abreviated_pos(self):
        if self.is_adjective():
            return "A"
        elif self.is_noun():
            return "N"
        elif self.is_preposition():
            return "P"
        elif self.is_verb():
            return "V"
        elif self.is_to():
            return "T"
        else:
            return "O"

    def is_adjective(self):
        if self.pos[0:2] == "JJ":
            return True
        else:
            return False

    def is_noun(self):
        if self.pos[0:2] == "NN":
            return True
        else:
            return False

    def is_preposition(self):
        if self.pos[0:2] == "IN":
            return True
        else:
            return False

    def is_verb(self):
        if self.pos[0:1] == "V":
            return True
        else:
            return False

    def is_to(self):
        if self.pos[0:2] == "TO":
            return True
        else:
            return False


class Document(Base):
    '''
    An article
    '''
    __tablename__ = 'docs'

    id = Column(Integer, primary_key=True)
    pubdate = Column(Date, nullable=False)
    headline = Column(String, nullable=False)
    full_text = Column(String, nullable=False)

    def __init__(self, pubdate, headline, docid, full_text):
        self.pubdate = pubdate
        self.headline = headline
        self.id = docid
        self.full_text = full_text

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
