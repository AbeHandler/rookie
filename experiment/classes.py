'''
Classes used in the webapp
'''
class Parameters(object):

    def __init__(self):
        '''
        An object that holds params from request
        '''
        self.q = None
        self.term = None
        self.termtype = None
        self.startdate = None
        self.enddate = None
        self.docid = None
        self.page = None