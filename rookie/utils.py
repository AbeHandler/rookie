from elasticsearch import Elasticsearch

def query_elasticsearch(lucene_query):
    ec = Elasticsearch(sniff_on_start=True)
    results = ec.search(index="lens", q=lucene_query)['hits']['hits']
    return results

class Link(object):

    def __init__(self, link):
        '''Initialize with a result'''

        self.link_text = link[0]
        self.link_num = link[1]


class Result(object):

    '''An elastic search result'''

    def __init__(self, result):
        '''Initialize with a result'''

        self.headline = result['_source']['headline'].encode('ascii','ignore')
        self.timestamp = result['_source']['timestamp'].encode('ascii','ignore')
        self.fulltext = result['_source']['full_text'].encode('ascii','ignore')
        self.url = result['_source']['url'].encode('ascii','ignore')
        self.nid = result['_id'].encode('ascii','ignore')
        self.docid = self.nid.split("-")[0]
        self.links = result['_source']['links']