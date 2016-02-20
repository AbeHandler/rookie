import glob
import os
import csv

try:
    os.remove("/Users/ahandler/research/rookie/corpora/iphone/raw/all.extract")
except:
    pass

for f in glob.glob("/Users/ahandler/research/rookie/corpora/iphone/raw/*txt"):
    with open (f) as inf:
        for l in inf:
            dt = l.replace("\n", "").split("\t")[2]
            txt = l.replace("\n", "").split("\t")[3]
            headline = txt
            c1 = ""
            with (open("/Users/ahandler/research/rookie/corpora/iphone/raw/all.extract", "a")) as csvfile:
                spamwriter = csv.writer(csvfile, delimiter='\t')
                spamwriter.writerow([c1, dt, dt, txt, txt, txt, txt])