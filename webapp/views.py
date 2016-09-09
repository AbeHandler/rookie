from flask import render_template
import json

class Views(object):
    '''
    The views for Rookie
    '''

    def __init__(self, IP, ROOKIE_JS, ROOKIE_CSS, BASE_URL):
        '''
        Initalize the views
        '''
        self.ip = IP
        self.js = ROOKIE_JS
        self.rookie_css = ROOKIE_CSS
        self.base_url = BASE_URL

    def handle_query(self, stuff_ui_needs):
        '''
        return main view
        '''
        if self.ip == "localhost":
            baseurl = "http://localhost:5000/"
        else:
            baseurl = "" #TODO: why this should be blank for an IP address?
        response = render_template(
            'medviz.html',
            stuff_ui_needs=stuff_ui_needs,
            IP=self.ip,
            base_url=self.base_url,
            ROOKIE_JS=self.js,
            ROOKIE_CSS=self.rookie_css
        )

        return response


    def basic_search(self, results, page, tot_pages, corpus):
        '''
        return IR view
        '''
        response = render_template(
            'search.html',
            results=json.dumps(results),
            corpus=corpus,
            page=page,
            tot_pages=tot_pages
        )

        return response


    def intro(self):
        '''
        return intro (for Rodrigo's class)
        '''
        response = render_template(
            'intro.html',
            ROOKIE_CSS=self.rookie_css
        )

        return response


    def basic_search_results(self, results, corpus, q):
        '''
        return results list
        '''
        response = render_template(
            'search_results.html',
            results=results,
            corpus=corpus,
            q=q
        )

        return response

    def quiz(self):
        '''
        return results list
        '''
        response = render_template(
            'quiz_l.html'
        )

        return response