'''
The Rookie engine
'''
import json
import os
import time
from pylru import lrudecorator
from whoosh.index import open_dir
from whoosh.qparser import QueryParser


@lrudecorator(100)
def get_metadata_file():
    with open("rookieindex/meta_data.json") as inf:
        metadata = json.load(inf)
    return metadata



