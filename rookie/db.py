
"""
NOT USED RIGHT NOW BUT WILL NEED THIS I THINK
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from rookie import CONNECTION_STRING

Base = declarative_base()


class Window(Base):
    """
    A gram type or a NER type
    """

    __tablename__ = 'windows'

    id = Column(Integer, primary_key=True)
    key = Column(String, index=True)
    window = Column(String)

    def __init__(self,
                 key,
                 window):
        self.key = key
        self.window = window


def remake_db():
    '''
    Creates the database via SQLAlchemy (?).
    '''

    engine = create_engine(CONNECTION_STRING)
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    remake_db()
