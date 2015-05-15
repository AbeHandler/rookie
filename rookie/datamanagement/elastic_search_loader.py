#! /usr/bin/python

import glob
import os
import json

from datetime import datetime
from elasticsearch import Elasticsearch

class Corpus:

    location = None

    def __init__(self, location):
        self.location = location.rstrip("/")
        assert os.path.isdir(self.location)
        return None

    def get_files(self, extension):
    	globstring = self.location + "/*" + extension
        return glob.glob(self.location + "/*" + extension)


#Need a decorator for interface here
class LensStory: 
    '''How do you do an interface in python?'''
    def __init__(self, location):
        filename, file_extension = os.path.splitext(location)
        assert file_extension == ".json"
        self.location = location
        with (open (location)) as jsonfile:
            json_data = json.load(jsonfile)
            # sample timestamp: 2010-10-10T10:10:10
            datestring = json_data['time'].split("T")[0]
            year, month, day = [int(y) for y in datestring.split("-")]
            self.date = str(datetime(year, month, day))
            self.text = json_data['full_text']
    
    def jsonify(self):
        json_output = {}
        json_output['text'] = self.text
        json_output['timestamp'] = self.date
        return json.dumps(json_output)


es = Elasticsearch(sniff_on_start=True)

es.indices.delete(index='*') # clear out everything from elastic search

corpus = Corpus("/backups/lens_corpus/")

counter = 1
for story_file in corpus.get_files("*json"):
    story = LensStory(story_file)
    res = es.index(index="lens", doc_type='news_story', id=counter, body=story.jsonify())
    counter = counter + 1

# to do: add headline
res = es.search(index="lens", body={"query": {"match_all": {"OPSB"}}})
print("Got %d Hits:" % res['hits']['total'])