'''
Classes used in the webapp
'''
from __future__ import division
import pdb
from collections import defaultdict
from experiment.models import Models
from dateutil.parser import parse
from datetime import datetime
from datetime import timedelta

def days_between(d1, d2):
    return abs((d2 - d1).days)

def months_between(d1, d2):
    return abs((d2 - d1).months)

def years_between(d1, d2):
    '''
    Apparently this is bad b/c leap years but whatever
    '''
    return int(abs((d2 - d1).days / 365))


def bin_dates(results, facets):
    dates = [parse(Models.get_pub_date(o)) for o in results]
    dates.sort()
    interval = days_between(min(dates), max(dates))
    delta = timedelta(days=1)
    bins = []
    start = min(dates)
    end_date = max(dates)
    bins = defaultdict(list)
    key = None
    d = start
    results_counter = 0
    while d <= end_date:
        if interval < 60:
            key = d.strftime('%y-%m-%d')
        if interval < (365 * 2):
            if key is None or d.day == 1:
                key = d.strftime('%y-%m')
        if interval >= (365 * 2):
            if key is None or d.day == 1 and d.month == 1:
                key = d.strftime('%y')
        while dates[results_counter] < d:
            bins[key]["count"].append(d)
            results_counter += 1
        d += delta
    return bins   


