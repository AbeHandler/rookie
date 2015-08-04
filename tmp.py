import pickle
import glob
from collections import defaultdict
from rookie.classes import IncomingFile

all_mentions = defaultdict(list)

to_run = glob.glob("data/lens_processed/*")

pronouns = ["WP", "WP$", "PRP", "PRP$"]

for f in to_run:
    infile = IncomingFile(f)
    try:
        groups = infile.doc.coreferences.groups
    except:
        groups = []
    for group in groups:
        mentions = []
        for mention in group:
            mention_pos = set([i.pos for i in mention.tokens])
            if not all(pos in pronouns for pos in mention_pos):
                mentions.append(repr(mention))
        if len(mentions) > 1:
            all_mentions[repr(mentions[0])].append(mentions)

pickle.dump(all_mentions, open("pickled/all_mentions.p", "w"))
