import glob
import json
from bs4 import BeautifulSoup

files = glob.glob("files/*.html")

domainlimiter = "thelensnola.org"


def get_links(element):
    output = []
    for i in full_text.findChildren('a'):
        if domainlimiter in i.attrs['href']:
            output.append([i.text, i.attrs['href']])
    return output


for f in files:
    try:
        json_text = {}
        text = "".join(open(f, "r"))
        soup = BeautifulSoup(text)
        full_text = soup.select(".entry-content")[0]
        time = soup.select("time")[0]
        time = time.attrs["datetime"].split("T")[0]
        json_text['time'] = time
        json_text['headline'] = soup.select(".entry-title")[0].text
        json_text['full_text'] = full_text.text.encode('ascii', 'ignore')
        newfile = f.replace(".html", '') + ".json"
        links = get_links(full_text)
        json_text['links'] = links
        with open(newfile, "w") as outfile:
            json.dump(json_text, outfile)
    except ValueError:
        print "{} value error".format(f)
    except KeyError:
        print "{} key error".format(f)
    except IndexError:
        print "{} index error".format(f)
