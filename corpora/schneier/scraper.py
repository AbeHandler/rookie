
'''
AH: Sep 1, 2018

This is a one-off script to scrape the Schneier on Security blog

The script runs python 3! The rest of rookie is python 2.

'''


import requests
import re
import time
import pickle

from tqdm import tqdm_notebook as tqdm
from bs4 import BeautifulSoup
from urllib3.exceptions import ProxyError
from collections import defaultdict

issues = []
for year in tqdm(range(1998, 2018)):
    r = requests.get("https://www.schneier.com/crypto-gram/{}/".format(year))
    time.sleep(5)
    for _ in re.findall("/crypto-gram/archives/" + str(year) + "/[0-9]{4}.html", r.text):
        issues.append(_)

issues = set(issues)


all_issues = defaultdict(str)

for issue in tqdm(issues, total=len(issues)):
    try:
        issue_text = requests.get("https://www.schneier.com" +  issue).text
        time.sleep(5)
        all_issues[issue] = issue_text
    except ProxyError as e:
        print(e)

with open("schneier.com", "wb") as of:
    pickle.dump(all_issues, of)