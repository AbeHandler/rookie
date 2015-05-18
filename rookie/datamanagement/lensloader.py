import glob
import urllib2
import logging
import nltk.data

from bs4 import BeautifulSoup
from datetime import datetime
from elasticsearch import Elasticsearch

logging.basicConfig(filename='lens.log', level=logging.DEBUG)

htmls = []

urls = []

TOKENIZEER = nltk.data.load('tokenizers/punkt/english.pickle')

domainlimiter = "thelensnola.org"

ids = {}

counter = 1

elasticsearch = Elasticsearch(sniff_on_start=True)

elasticsearch.indices.delete(index='*')  # clear out everything


def get_page(url):
    req = urllib2.Request(url, headers={'User-Agent': "Abe Handler: urllib2"})
    con = urllib2.urlopen(req)
    return con.read()


def get_html_summaries():
    htmls = []
    for i in range(1, 423):
        i = str(i)
        url = "http://thelensnola.org/page/" + i + "/?s="
        htmls.append(get_page(url))
        logging.info('Downloading summary | {}'.format(i))
    return htmls


def get_id(url):
    global counter
    if url not in ids.keys():
        ids[url] = counter
        logging.info('Assign id | {} | {}'.format(url, counter))
        counter = counter + 1
    return ids[url]


def get_links(element):
    output = []
    for i in full_text.findChildren('a'):
        linkurl = i.attrs['href']
        if domainlimiter in linkurl:
            if "support-us" in linkurl or "about-us" in linkurl:
                pass
            else:
                output.append([i.text, get_id(i.attrs['href'])])
    return output


summaries = get_html_summaries()


for html in summaries:
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

logging.info('Total urls | {}'.format(len(urls)))

for url in urls:
    try:
        html = get_page(url)
        soup = BeautifulSoup(html)
        if len(soup.select(".opinion-label")) == 0:
            full_text = soup.select(".entry-content")[0]
            time = soup.select("time")[0]
            time = time.attrs["datetime"].split("T")[0]
            json_text = {}
            year, month, day = [int(y) for y in time.split("-")]
            pubdate = str(datetime(year, month, day))
            json_text['timestamp'] = pubdate
            json_text['id'] = get_id(url)
            json_text['headline'] = soup.select(".entry-title")[0].text
            json_text['full_text'] = full_text.text.encode('ascii', 'ignore')
            links = get_links(full_text)
            json_text['links'] = links
            sentences = TOKENIZEER.tokenize(json_text['full_text'])
            logst = 'Adding to elastic search| {}, {}'.format(url, get_id(url))
            logging.info(logst)
            sentence_counter = 1
            for sentence in sentences:
                did = str(get_id(url)) + "-" + str(sentence_counter)
                json_text['full_text'] = sentence
                res = elasticsearch.index(index="lens",
                                          doc_type='news_story',
                                          id=did,
                                          body=json_text)
                sentence_counter = sentence_counter + 1

    except ValueError:
        logging.info('ValueError | {}, {}'.format(url, get_id(url)))
    except KeyError:
        logging.info('KeyError | {}, {}'.format(url, get_id(url)))
    except IndexError:
        logging.info('IndexError | {}, {}'.format(url, get_id(url)))
