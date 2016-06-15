import sys, os
from twokenize import tokenize


def lines(fname):
    '''how many lines in the file?'''
    print fname
    with open(fname, "r") as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def prelims():
    dates = lines(sys.argv[1])
    pos = lines(sys.argv[1].replace(".dates", ".pos"))
    tweet = lines(sys.argv[1].replace(".tweet", ".pos"))
    assert tweet == pos == dates

try:
    os.remove(sys.argv[1].replace(".dates", ".anno_plus"))
except OSError:
    pass


with open(sys.argv[1], "r") as inf:
    assert sys.argv[1][-6:] == ".dates"
    for i in range(lines(sys.argv[1])):
        if i % 100000 == 0:
            sys.stderr.write("{}\t".format(i))
        out = {}
        with open(sys.argv[1], "r") as dts:
            with open(sys.argv[1].replace(".dates", ".pos"), "r") as poss:
                with open(sys.argv[1].replace(".dates", ".tweet"), "r") as tweets:
                    dt = dts.next().replace('/tweets/all_parcol/', '')[0:10]
                    pos = poss.next()
                    tw = tweets.next()
                    toks = tokenize(tw)
                    tags = pos.split('\t')[1].split()
