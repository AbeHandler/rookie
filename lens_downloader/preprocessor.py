import glob
import json
from bs4 import BeautifulSoup
from utils import standarizeurl
files = glob.glob("files/*.txt")


def get_links(element):
    output = []
    for i in full_text.findChildren('a'):
        output.append([i.text, standarizeurl(i.attrs['href'])])
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
        newfile = f.replace(".txt", '') + ".json"
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
