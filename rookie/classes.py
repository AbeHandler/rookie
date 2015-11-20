import pdb
import json

from pylru import lrudecorator
from itertools import tee, izip, islice, chain


@lrudecorator(100)
def get_stopwords():
    '''
    Gets the stopwords file
    '''
    stopwords = [i.replace("\n", "") for i in open("stopwords.txt")]
    return stopwords


def stop_word(word):
    '''
    Is word a stop word? Returns y/n
    '''
    stops = get_stopwords()
    if word in stops:
        return True
    return False


class IncomingFile(object):
    """
    An incoming file wraps a Document + metadata
    It hides all dealings with the file system
    """
    def __init__(self, filename):
        try:
            with (open(filename, "r")) as infile:
                self.doc = None
                json_in = json.loads(infile.read())
                self.url = json_in['url']
                self.headline = json_in['headline']
                self.pubdate = json_in['timestamp'].split(" ")[0]
                data = json_in['lines']
                self.doc = Document(data)
                self.doc.coreferences = None # not being used right now
                self.filename = filename
        except UnicodeEncodeError:
            pass
        except TypeError:
            pass
        except ValueError:
            pass

'''
Method below should take a first mention in text and replace 
later mentions w/ the original mention
"example: replace 'he', w/ Mitch Landrieu". 
This is more trouble than it is worth for now

def propagate_first_mentions(document):


    for group in document.coreferences.groups:
        first_mention = group[0]
        sentence = document.sentences[first_mention.sentence]
        start = first_mention.span_start
        end = first_mention.span_end
        first_mention_tokens = sentence.tokens[start:end]
        if all(t.ner_tag == "PERSON" or t.ner_tag == "ORGANIZATION" for
               t in first_mention_tokens):
            for mention in group[1:]:  # slice_off first token
                pass
                # expand it, theoretically
'''


class N_Grammer(object):

    '''
    Takes a line of output from python-Stanford wraper
    and finds the syntactically valid ngrams
    '''
    # https://stackoverflow.com/questions/21883108/fast-optimize-n-gram-implementations-in-python

    def pairwise(self, iterable, n=2):
        return izip(*(islice(it, pos, None) for pos, it
                      in enumerate(tee(iterable, n))))

    def get_ngrams(self, words, n=2):
        words = [i for i in words if not stop_word(i.raw.upper())]
        return self.pairwise(words, n)

    def is_syntactically_valid(self, ngram):
        valid_two_grams = ["NN", "AN"]  # , "NV", "VN"]
        valid_three_grams = ["AAN", "NNN", "ANN", "NPN"]  # , "ANV", "NNV", "NVV", "TVN", "VPN", "VNN", "VAN", "VDN"]
        valid_four_grams = ["ANPV", "NNNN", "ANNN"] # , "NNNV", "ANTV", "NNTV", "TVPN", "VANN", "VNNN", "VPNN"]

        pattern = "".join([(j.abreviated_pos()) for j in ngram])
        if pattern in valid_two_grams and len(pattern) == 2:
            return True
        if pattern in valid_three_grams and len(pattern) == 3:
            return True
        if pattern in valid_four_grams and len(pattern) == 4:
            return True

    def get_syntactic_ngrams(self, words, n):
        '''
        :param words: a list of word tokens
        :type words: Token
        '''
        return [i for i in self.get_ngrams(words, n) if
                self.is_syntactically_valid(i)]


class Document(object):

    '''
    This is an abstraction over output from proc.document_parse()
    running in "ner" mode from the python NLP wrapper
    '''

    def __init__(self, json_output, coreferences=None):
        '''
        Initialize w/ the json output.
        Coreferences are optional
        '''
        try:
            sentences_json = json_output['sentences']
        except KeyError:
            sentences_json = []
        sentences = []
        people = []
        organizations = []
        ngrams = []
        for i in range(0, len(sentences_json)):
            sentence = Sentence(sentences_json[i], i)
            sentences.append(sentence)
            people = people + [i for i in sentence.ner if i.type == "PERSON"]
            organizations = organizations + [i for i in sentence.ner if i.type == "ORGANIZATION"]
            ngrams = ngrams + sentence.ngrams
        self.ngrams = ngrams
        self.people = people
        self.organizations = organizations
        self.sentences = sentences
        text = ""
        for sentence in self.sentences:
            text = text + " ".join([w.raw for w in sentence.tokens])
        self.full_text = text
        self.coreferences = coreferences
        sentence_tokens = [s.tokens for s in self.sentences]
        self.tokens = list(chain(*sentence_tokens))


class Sentence(object):

    def get_ner(self, json_sentence, tokens):
        ner = json_sentence['ner']
        counter = 0
        output = []
        while counter < len(ner):
            ne_type = ner[counter]
            if ne_type != "O":
                ner_to_add = [tokens[counter]]
                try:
                    while ner[counter + 1] == ne_type:
                        ne_type = ner[counter + 1]
                        counter = counter + 1
                        next_token = tokens[counter]
                        ner_to_add.append(next_token)
                except IndexError:  # reached the end of the ner
                    pass
                output.append(NER(ner_to_add, ne_type, self.sentence_no))
            counter = counter + 1
        return output

    def get_ngrams(self):
        '''
        :param words: a list of all word tokens in a document
        :type words: Token
        '''
        ngrams = N_Grammer()
        grams = []
        # ngrams 1 thru 4
        for i in range(1, 5):
            grams = grams + ngrams.get_syntactic_ngrams(self.tokens, i)
        return grams

    def __init__(self, json_sentence, sentence_no):
        '''
        Initialize w/ the json output
        '''
        self.sentence_no = sentence_no
        tokens = json_sentence['tokens']
        lemmas = json_sentence['lemmas']
        poses = json_sentence['pos']
        ner = json_sentence['ner']
        self.deps = json_sentence['deps_basic']
        assert len(tokens) == len(lemmas)
        assert len(poses) == len(lemmas)
        assert len(tokens) == len(poses)
        sentence_tokens = []
        for i in range(0, len(tokens)):
            t = Token(tokens[i], poses[i], lemmas[i], i, sentence_no, ner[i])
            sentence_tokens.append(t)
        self.tokens = sentence_tokens
        self.ngrams = self.get_ngrams()
        self.ner = self.get_ner(json_sentence, self.tokens)


class Token(object):

    def __init__(self, raw_token, pos, lemma_form, token_no, sentence_no, ner):
        '''
        Initialize w/ the json output
        '''
        # Store tokens as unicode, but remove non standard chars for now #TODO
        self.raw = raw_token.encode("ascii", "ignore").decode()
        self.pos = pos
        self.ner_tag = ner
        self.lemma_form = lemma_form
        self.token_no = token_no
        self.sentence_no = sentence_no

    def abreviated_pos(self):
        if self.is_adjective():
            return "A"
        elif self.is_noun():
            return "N"
        elif self.is_preposition():
            return "P"
        elif self.is_verb():
            return "V"
        elif self.is_to():
            return "T"
        else:
            return "O"

    def is_adjective(self):
        if self.pos[0:2] == "JJ":
            return True
        else:
            return False

    def is_noun(self):
        if self.pos[0:2] == "NN":
            return True
        else:
            return False

    def is_preposition(self):
        if self.pos[0:2] == "IN":
            return True
        else:
            return False

    def is_verb(self):
        if self.pos[0:1] == "V":
            return True
        else:
            return False

    def is_to(self):
        if self.pos[0:2] == "TO":
            return True
        else:
            return False


class NER(object):

    def __init__(self, tokens, type_of_ner, sentence_no):
        '''
        Initialize w/ the json output
        '''
        self.tokens = tokens
        self.type = type_of_ner
        self.sentence_no = sentence_no

    def __repr__(self):
        return " ".join([i.raw for i in self.tokens])

'''
This code is not used right now. But is potentially useful later.

class Coreferences(object):

    def __init__(self, data, document):
        try:
            entity_groups = data['entities']
            self.groups = []  # start with no coref groups
            for e in entity_groups:
                if not e['mentions'] is None:
                    group = []
                    for m in e['mentions']:
                        group.append(Mention(m, document))
                    self.groups.append(group)
        except KeyError:
            self.groups = []
        except TypeError:
            self.groups = []



class Mention(object):

    def __init__(self, json_input, document):
        self.sentence = document.sentences[json_input['sentence']]
        self.tokspan = json_input['tokspan_in_sentence']
        self.span_start = self.tokspan[0]
        self.span_end = self.tokspan[1]
        self.tokens = self.sentence.tokens[self.span_start: self.span_end]

    def __repr__(self):
        string = [o.raw for o in self.tokens]
        return " ".join(string)
'''
