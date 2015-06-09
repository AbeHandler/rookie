import urllib2
import nltk.data
import ner
import json
import pdb

from datetime import datetime
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from rookie import log
from rookie.utils import POS_tag
from rookie.utils import penn_to_wordnet
from nltk.stem.wordnet import WordNetLemmatizer

# Valid parts of speech in wordnet
WORDNET_TAGS = ['n', 'v', 'a', 's', 'r']

ENTITY_KEYS = ["TIME", "LOCATION", "ORGANIZATION",
               "PERSON", "MONEY", "PERCENT", "DATE"]

domainlimiter = "thelensnola.org"

ids = {}

counter = 1

elasticsearch = Elasticsearch(sniff_on_start=True)

elasticsearch.indices.delete(index='*')  # clear out everything
wnl = WordNetLemmatizer()


def standardize(tag):
    '''
    Takes a tagged word from Stanford POS tagger and
    returns a lemmaed word from NLTK's Wordnet Lemmatizer

    Sample input: (u'are', u'VBP')
    '''
    pdb.set_trace()
    word = tag[0]
    pdb.set_trace()
    tag = tag[1]
    tag = penn_to_wordnet(tag)
    pdb.set_trace()
    if tag in WORDNET_TAGS:
        word = wnl.lemmatize(word, tag)
    else:
        # if no pos given, wn will assume is a noun
        word = wnl.lemmatize(word)
    word = word.lower()
    return word


def get_page(url):
    req = urllib2.Request(url, headers={'User-Agent': "Abe Handler: urllib2"})
    con = urllib2.urlopen(req)
    return con.read()


def get_html_summary(i):
    htmls = []
    i = str(i)
    url = "http://thelensnola.org/page/" + i + "/?s="
    htmls.append(get_page(url))
    log.info('Downloading summary | {}'.format(i))
    return htmls


def get_id(url):
    global counter
    if url not in ids.keys():
        ids[url] = counter
        log.info('Assign id | {} | {}'.format(url, counter))
        counter = counter + 1
    return ids[url]


def get_links(full_text):
    output = []
    for i in full_text.findChildren('a'):
        linkurl = i.attrs['href']
        if domainlimiter in linkurl:
            if "support-us" in linkurl or "about-us" in linkurl:
                pass
            else:
                output.append([i.text, get_id(i.attrs['href'])])
    return output


def get_urls_from_summary(html):
    urls = []
    soup = BeautifulSoup(html)
    h3 = soup.find_all('h3')
    for i in h3:
        try:
            if "Permalink" in i.contents[0].attrs['title']:
                url = i.contents[0].attrs['href']
                urls.append(url.strip("/"))
        except AttributeError:  # can skip elements that don't have hrefs
            pass
        except KeyError:  # not a link. does not have a title
            pass
    return urls


def get_pub_date(soup):
    time = soup.select("time")[0]
    time = time.attrs["datetime"].split("T")[0]
    json_text = {}
    year, month, day = [int(y) for y in time.split("-")]
    pubdate = str(datetime(year, month, day))
    return pubdate


def get_article_full_text(sentences):
    article_full_text = ""
    for sentence in sentences:
        tags = POS_tag(sentence)
        dummy = []
        pdb.set_trace()
        if type(tags) == type(dummy):
            tags = tags[0]
        words = [standardize(t) for t in tags]
        sentence_full_text = " ".join([word for word in words])
        article_full_text = article_full_text + " " + sentence_full_text
    return article_full_text


def extract_article_entities(sentences):
    article_entities = {}
    sentence_entities = []
    # Python interface to the StanfordNER
    TAGGER = ner.SocketNER(host='localhost', port=8080)
    for sentence in sentences:
        entnites = json.loads(TAGGER.json_entities(sentence))
        sentence_entities.append(entnites)
    return sentence_entities


def merge_sentence_entities(sentence_entities):
    ENTITY_KEYS = ["TIME", "LOCATION", "ORGANIZATION",
                   "PERSON", "MONEY", "PERCENT", "DATE"]
    article_entities = {}
    for key in ENTITY_KEYS:
        entity_kind_total = []
        for sentence in sentence_entities:
            try:
                entity_kind_total.extend(sentence[key])
            except KeyError:
                pass  # no hits for type $key in this sentence
        article_entities[key] = entity_kind_total
    return article_entities


def process_story_url(url):
    try:
        SENTENCE_TOKENIZER = nltk.data.load('tokenizers/punkt/english.pickle')
        json_text = {}
        log.info(url)
        html = get_page(url)
        soup = BeautifulSoup(html)
        full_text = soup.select(".entry-content")[0]
        json_text['timestamp'] = get_pub_date(soup)
        json_text['url'] = url
        json_text['headline'] = soup.select(".entry-title")[0].text
        links = get_links(full_text)
        full_text = full_text.text.encode('ascii', 'ignore')
        sentences = SENTENCE_TOKENIZER.tokenize(full_text)
        print "about to get article full text"
        article_full_text = get_article_full_text(sentences)
        print "about to get entities"
        sentence_entities = extract_article_entities(sentences)
        article_entities = merge_sentence_entities(sentence_entities)
        article_full_text = get_article_full_text(sentences)
        json_text['full_text'] = article_full_text
        json_text['entities'] = article_entities
        json_text['links'] = links
        logst = 'Adding to elastic search| {}, {}'.format(url, get_id(url))
        log.info(logst)
        did = str(get_id(url))
        res = elasticsearch.index(index="lens",
                                  doc_type='news_story',
                                  id=did,
                                  body=json_text)
        print res

    except ValueError:
        log.info('ValueError| {}, {}'.format(url, get_id(url)))
    except KeyError:
        log.info('KeyError| {}, {}'.format(url, get_id(url)))
#    except IndexError:
#        log.info('IndexError| {}, {}'.format(url, get_id(url)))
    except OSError:
        log.info('OSError| {} {} {}'.format(url, get_id(url), "out of memory"))

if __name__ == '__main__':
    for i in range(1, 435):
        summary = get_html_summary(i)
        for html in summary:
            urls = get_urls_from_summary(html)
            for url in urls:
                process_story_url(url)
