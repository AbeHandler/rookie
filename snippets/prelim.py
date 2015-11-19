from __future__ import division
import pdb
import pickle
import os
import json
import numpy as np
from dateutil import parser
import pdb
from pylru import lrudecorator
from collections import Counter
from collections import defaultdict
from experiment.models import Models, Parameters
from snippets.utils import flip
from snippets import log
from whoosh.index import create_in
from whoosh.qparser import QueryParser
from whoosh.fields import *
from whoosh import writing

def get_snippet(term, termtype, sentences, original_query):
    return "s"