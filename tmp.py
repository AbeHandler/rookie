import ipdb
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from webapp import CONNECTION_STRING
engine = create_engine(CONNECTION_STRING)
Session = sessionmaker(bind=engine)
session = Session()
go = lambda *args: session.connection().execute(*args)
row = session.connection().execute("select * from doc_metadata")
ipdb.set_trace()
print row
