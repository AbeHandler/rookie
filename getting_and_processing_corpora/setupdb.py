'''build connection to db'''
import ipdb
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from webapp import CONNECTION_STRING
engine = create_engine(CONNECTION_STRING)
Session = sessionmaker(bind=engine)
session = Session()
go = lambda *args: session.connection().execute(*args)


go("create table sentences_preproc (corpusid integer, docid integer, delmited_sentences TEXT)")
go("create table ngram_pubdates (ngram text, pubdates jsonb, corpusid integer)")
go("create table doc_metadata (docid integer, data jsonb, corpusid integer)")
go("create table corpora (corpusid integer not null primary key, corpusname character(100), first_story date, last_story date)")
go("create table count_vectors (docid integer, corpusid integer not null, data jsonb)")

import glob


for c_ix, corpus in enumerate(glob.glob("corpora/*")):
    cp = corpus.split("/").pop()
    go("insert into corpora values ({}, '{}')".format(c_ix, cp))

go("CREATE index on doc_metadata (docid)") # i think these are all the important indexes. added them manually
go("CREATE index on doc_metadata (corpusid)")
go("CREATE index on count_vectors (docid)")
go("CREATE index on count_vectors (corpusid)")
go("CREATE index on sentences_preproc (corpusid)")
go("CREATE index on sentences_preproc (docid)")

session.commit()