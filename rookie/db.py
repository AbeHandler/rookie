
"""
NOT USED RIGHT NOW BUT WILL NEED THIS I THINK
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from rookie import CONNECTION_STRING

Base = declarative_base()


class GramNER(Base):
    """
    A gram type or a NER type
    """

    __tablename__ = 'gramner'

    id = Column(Integer, primary_key=True)
    string = Column(String, unique=True)

    def __init__(self,
                 string, index=True):
        self.string = string


class Link(Base):
    """
    A gram type or a NER type
    """

    __tablename__ = 'links'

    id = Column(Integer, primary_key=True)
    gramner1 = Column(Integer, index=True)
    gramner2 = Column(Integer, index=True)
    pubdate = Column(Date, index=True)
    url = Column(String)

    def __init__(self,
                 g1,
                 g2,
                 pubdate,
                 url):
        self.gramner1 = g1
        self.gramner2 = g2
        self.pubdate = pubdate
        self.url = url


def remake_db():
    '''
    Creates the database via SQLAlchemy (?).
    '''

    engine = create_engine(CONNECTION_STRING)
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    remake_db()
