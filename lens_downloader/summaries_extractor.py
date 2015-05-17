import glob
import urllib2
import logging

from bs4 import BeautifulSoup
from datetime import datetime
from elasticsearch import Elasticsearch

logging.basicConfig(filename='lens.log', level=logging.DEBUG)

htmls = glob.glob("*html")

urls = []

domainlimiter = "thelensnola.org"

ids = {}

counter = 1

elasticsearch = Elasticsearch(sniff_on_start=True)

elasticsearch.indices.delete(index='*')  # clear out everything


def get_page(url):
    req = urllib2.Request(url, headers={'User-Agent': "Abe Handler: urllib2"})
    con = urllib2.urlopen(req)
    return con.read()


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


for h in htmls:
    html = "".join(tuple(open(h, 'r')))
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


for url in urls:
    html = get_page(url)
    try:
        soup = BeautifulSoup(html)
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
        res = elasticsearch.index(index="lens",
                                  doc_type='news_story',
                                  id=get_id(url),
                                  body=json_text)
    except ValueError:
        print "{} value error".format(url)
    except KeyError:
        print "{} key error".format(url)
    except IndexError:
        print "{} index error".format(url)
