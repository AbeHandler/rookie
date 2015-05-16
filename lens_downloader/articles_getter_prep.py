import glob
import pdb
from bs4 import BeautifulSoup
from utils import standarizeurl

htmls = glob.glob("*html")

urls = []


for h in htmls:
    html = "".join(tuple(open(h, 'r')))
    soup = BeautifulSoup(html)
    h3 = soup.find_all('h3')
    for i in h3:
        try:
            if "Permalink" in i.contents[0].attrs['title']:
                url = i.contents[0].attrs['href']
                urls.append(url)
        except AttributeError:  # can skip elements that don't have hrefs
            pass
        except KeyError:  # not a link. does not have a title
            pass

with open("out.txt", "a") as f:
    for item in urls:
        f.write("%s\n" % item)
