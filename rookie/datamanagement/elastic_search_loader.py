#! /usr/bin/python
'''Loads a corpus into elastic search'''
import glob
import os
import json

from datetime import datetime
from elasticsearch import Elasticsearch


class Corpus(object):
    '''A corpus of documents in a file system'''
    location = None

    def __init__(self, location):
        self.location = location.rstrip("/")
        assert os.path.isdir(self.location)
        return None

    def get_files(self, extension):
        globstring = self.location + "/*" + extension
        return glob.glob(globstring)


# Need a decorator for interface here
class LensStory(object):
    '''How do you do an interface in python?'''
    def __init__(self, location):
        filename, file_extension = os.path.splitext(location)
        assert file_extension == ".json"
        self.location = location
        with (open(location)) as jsonfile:
            json_data = json.load(jsonfile)
            # sample timestamp: 2010-10-10T10:10:10
            datestring = json_data['time'].split("T")[0]
            year, month, day = [int(y) for y in datestring.split("-")]
            self.date = str(datetime(year, month, day))
            self.text = json_data['full_text']
            self.headline = json_data['headline']

    def jsonify(self):
        '''Dump out json'''
        json_output = {}
        json_output['text'] = self.text
        json_output['timestamp'] = self.date
#        json_output['headline'] = self.headline
        return json.dumps(json_output)


elasticsearch = Elasticsearch(sniff_on_start=True)

elasticsearch.indices.delete(index='*')  # clear out everything

corpus = Corpus("/Users/abramhandler/research/rookie/lens_downloader/files/")

counter = 1
for story_file in corpus.get_files("*json"):
    story = LensStory(story_file)
    res = elasticsearch.index(index="lens",
                              doc_type='news_story',
                              id=counter,
                              body=story.jsonify())
    counter = counter + 1


results = elasticsearch.search(index="lens", q="OPSB")

print "Got %d Hits:" % results['hits']['total']
