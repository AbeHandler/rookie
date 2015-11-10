import pdb
import json
from pylru import lrudecorator
from dateutil.parser import parse


# TODO: merge two methods below

@lrudecorator(100)
def get_metadata_file():
    with open("data/meta_data.json") as inf:
        metadata = json.load(inf)
    return metadata


@lrudecorator(100)
def get_date_tracker_file():
    with open("data/date_instances.json") as inf:
        metadata = json.load(inf)
    return metadata



class Parameters(object):

    def __init__(self):
        self.q = None
        self.term = None
        self.termtype = None
        self.current_page = None
        self.startdate = None
        self.enddate = None
        self.docid = None
        self.page = None


class Models(object):

    '''Handles logic for the experiment app'''

    @staticmethod
    def get_tokens(docid):
        with open('articles/' + docid) as data_file:    
            data = json.load(data_file)
        return data

    @staticmethod
    def get_headline(docid):
        dt = get_metadata_file()
        return dt[docid]['headline']

    @staticmethod
    def get_pub_date(docid):
        dt = get_metadata_file()
        return dt[docid]['pubdate']

    @staticmethod
    def get_parameters(request):
        '''get parameters'''
        output = Parameters()

        output.q = request.args.get('q')

        output.term = request.args.get('term')

        output.termtype = request.args.get('termtype')

        output.current_page = request.args.get('page')

        try:
            output.current_page = int(output.current_page)
        except:
            output.current_page = 1

        try:
            output.startdate = parse(request.args.get('startdate'))
            if len(output.startdate) == 0:
                output.startdate = None
        except:
            output.startdate = None
        try:
            output.enddate = parse(request.args.get('enddate'))
            if len(output.enddate) == 0:
                output.enddate = None
        except:
            output.enddate = None

        try:
            output.docid = request.args.get('docid')
        except:
            output.docid = None

        output.page = 1

        return output
