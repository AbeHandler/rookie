import urllib2
import nltk.data

from datetime import datetime
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from rookie import log

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


def process_story_url(url):
    try:
        log.info(url)
        html = get_page(url)
        soup = BeautifulSoup(html)
        full_text = soup.select(".entry-content")[0]
        time = soup.select("time")[0]
        time = time.attrs["datetime"].split("T")[0]
        json_text = {}
        year, month, day = [int(y) for y in time.split("-")]
        pubdate = str(datetime(year, month, day))
        json_text['timestamp'] = pubdate
        json_text['url'] = url
        json_text['headline'] = soup.select(".entry-title")[0].text
        json_text['full_text'] = full_text.text.encode('ascii', 'ignore')
        links = get_links(full_text)
        json_text['links'] = links
        logst = 'Adding to elastic search| {}, {}'.format(url, get_id(url))
        log.info(logst)
        did = str(get_id(url))
        res = elasticsearch.index(index="lens",
                                  doc_type='news_story',
                                  id=did,
                                  body=json_text)

    except ValueError:
        log.info('ValueError | {}, {}'.format(url, get_id(url)))
    except KeyError:
        log.info('KeyError | {}, {}'.format(url, get_id(url)))
    except IndexError:
        log.info('IndexError | {}, {}'.format(url, get_id(url)))

for i in range(1, 435):
    summary = get_html_summary(i)
    for html in summary:
        urls = get_urls_from_summary(html)
        for url in urls:
            process_story_url(url)
