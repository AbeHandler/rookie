import pdb
import json

from itertools import tee, izip, islice, chain


class IncomingFile(object):
    """
    Mention of a ner or ngram
    Each mention is associated with coccurances
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
        except UnicodeEncodeError:
            pass
        except TypeError:
            pass
        except ValueError:
            pass


def propagate_first_mentions(document):
    '''
    This is more trouble than it is worth for now
    '''
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


class NPEPair(object):

    def __init__(self, one, two):
        self.word1 = one
        self.word2 = two

    def __eq__(self, other):
        if repr(self.word1) == repr(other.word1) and \
                repr(self.word2) == repr(other.word2):
            return True
        elif repr(self.word1) == repr(other.word2) and \
                repr(self.word2) == repr(other.word1):
            return True
        else:
            return False

    def __hash__(self):
        tmp = repr(self.word1) + repr(self.word2)
        hasss = tmp.__hash__()
        return hasss

    def __repr__(self):
        return self.word1 + " " + self.word2


class Window(object):

    @staticmethod
    def get_window(sentence_tokens, npe_tokens, window_size=10):
        '''
        Returns the token around an npe in a sentence. An npe
        is either an entity or an ngram -- a (n)oun (p)hrase or (e)ntity
        '''
        tokens = sentence_tokens
        start_ner = [i.raw for i in tokens].index(npe_tokens[0].raw)
        end_ner = start_ner + len(npe_tokens)
        start = start_ner - window_size
        end = end_ner + window_size
        # if start of window is before start of tokens, set to zero
        if start < 0:
            start = 0

        # if end of window is after end of tokens, set to len(tokens)
        if end > len(tokens):
            end = len(tokens)

        output = tokens[start: end]

        return output


class N_Grammer(object):

    '''
    Takes a line of output from python-Stanford wraper
    and finds the syntactically valid ngrams
    '''
    # https://stackoverflow.com/questions/21883108/fast-optimize-n-gram-implementations-in-python

    # valid_two_grams = ["NN", "AN"]
    # valid_three_grams = ["AAN", "NNN", "ANN"]

    # A = any adjective (PTB tag starts with JJ)
    # N = any noun (PTB tag starts with NN)

    def pairwise(self, iterable, n=2):
        return izip(*(islice(it, pos, None) for pos, it
                      in enumerate(tee(iterable, n))))

    def get_ngrams(self, words, n=2):
        return self.pairwise(words, n)

    def is_syntactically_valid(self, ngram):
        valid_two_grams = ["NN", "AN"]
        valid_three_grams = ["AAN", "NNN", "ANN"]
        pattern = "".join([(j.abreviated_pos()) for j in ngram])
        if pattern in valid_two_grams and len(pattern) == 2:
            return True
        if pattern in valid_three_grams and len(pattern) == 3:
            return True

    def get_syntactic_ngrams(self, words):
        '''
        :param words: a list of word tokens
        :type words: Token
        '''
        bigrams = [i for i in self.get_ngrams(words, 2) if
                   self.is_syntactically_valid(i)]
        trigrams = [i for i in self.get_ngrams(words, 3) if
                    self.is_syntactically_valid(i)]
        return (bigrams, trigrams)


class Link(object):

    def __init__(self, link):
        '''Initialize with a result'''

        self.link_text = link[0]
        self.link_num = link[1]


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
        for i in range(0, len(sentences_json)):
            sentence = Sentence(sentences_json[i], i)
            sentences.append(sentence)
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
        ng = N_Grammer()
        grams = ng.get_syntactic_ngrams(self.tokens)
 #       two_grams = []
 #       threegrams = grams[1]
 #       for twogram in grams[0]:  # TODO refactorr!!
 #           add = True
 #           for threegram in threegrams:
 #               if twogram in threegram:
 #                   add = False
 #           if add:
 #               two_grams.append(twogram)
        return grams[0] + grams[1]

    def __init__(self, json_sentence, sentence_no):
        '''
        Initialize w/ the json output
        '''
        self.WIN_SIZE = 10
        self.sentence_no = sentence_no
        tokens = json_sentence['tokens']
        lemmas = json_sentence['lemmas']
        poses = json_sentence['pos']
        ner = json_sentence['ner']
        self.deps = json_sentence['deps_basic']
        assert(len(tokens) == len(lemmas))
        assert(len(poses) == len(lemmas))
        assert(len(tokens) == len(poses))
        sentence_tokens = []
        for i in range(0, len(tokens)):
            t = Token(tokens[i], poses[i], lemmas[i], i, sentence_no, ner[i])
            sentence_tokens.append(t)
        self.tokens = sentence_tokens
        self.ner = self.get_ner(json_sentence, self.tokens)


class Token(object):

    def __init__(self, raw_token, pos, lemma_form, token_no, sentence_no, ner):
        '''
        Initialize w/ the json output
        '''
        self.raw = raw_token
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


class Coreferences(object):

    def __init__(self, data):
        try:
            entity_groups = data['entities']
            self.groups = []  # start with no coref groups
            for e in entity_groups:
                if not e['mentions'] is None:
                    group = []
                    for m in e['mentions']:
                        group.append(Mention(m))
                    self.groups.append(group)
        except KeyError:
            self.groups = []
        except TypeError:
            self.groups = []


class Mention(object):

    def __init__(self, json_input):
        self.sentence = json_input['sentence']
        self.tokspan = json_input['tokspan_in_sentence']
        self.span_start = self.tokspan[0]
        self.span_end = self.tokspan[1]


class Gramner(object):
    '''
    An Gramner is a set of tokens that match syntactically valid
    pattern or represent a named entity
    '''
    def __init__(self, tokens, window):
        self.tokens = tokens
        self.window = " ".join([i.raw for i in window])

    def __repr__(self):
        return " ".join([i.raw for i in self.tokens]).upper()
