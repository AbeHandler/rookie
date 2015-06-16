import datetime


class Link(object):

    def __init__(self, link):
        '''Initialize with a result'''

        self.link_text = link[0]
        self.link_num = link[1]


class EntityCount(object):

    def __init__(self, tup):
        '''A named entity, and how many times it shows up in query'''

        self.name = tup[0]
        self.count = tup[1]


class QueryResult(object):

    def __init__(self, words, persons, organizations,
                 locations, money, dates, results):
        '''Output from an elastic search query'''

        self.words = words
        self.persons = persons
        self.organizations = organizations
        self.locations = locations
        self.money = money
        self.dates = dates
        self.results = results


class Result(object):

    '''An elastic search result'''

    def __init__(self, result):
        '''Initialize with a result'''
        self.headline = result['_source']['headline'].encode('ascii', 'ignore')
        timestamp = result['_source']['timestamp'].encode('ascii', 'ignore')
        timestamp = timestamp.split(" ")[0]
        year, month, day = timestamp.split("-")
        pubdate = datetime.date(int(year), int(month), int(day))
        self.timestamp = pubdate
        fulltext = result['_source']['full_text'].encode('ascii', 'ignore')
        self.fulltext = fulltext
        self.url = result['_source']['url'].encode('ascii', 'ignore')
        self.nid = result['_id'].encode('ascii', 'ignore')
        self.docid = self.nid
        self.links = result['_source']['links']
        self.score = result['_score']
        self.entities = result['_source']['entities']
        self.link_degree = None

    def as_dictionary(self):
        output = {}
        output['headline'] = self.headline
        output['timestamp'] = self.timestamp
        output['fulltext'] = self.fulltext
        output['url'] = self.url
        output['sentence_id'] = self.sentence_id
        output['link_degree'] = self.link_degree
        output['score'] = self.score
        output['entities'] = self.entities
        return output
