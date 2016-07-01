import sys, os
import ujson as json
from twokenize import tokenize
import fstphrases



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
    try:
        os.remove(sys.argv[1].replace(".dates", ".anno_plus"))
    except OSError:
        pass
    for i in range(lines(sys.argv[1])):
        if i % 100000 == 0:
            sys.stderr.write("{}\t".format(i))
        out = {}
        with open(sys.argv[1], "r") as dts:
            with open(sys.argv[1].replace(".dates", ".pos"), "r") as poss:
                with open(sys.argv[1].replace(".dates", ".tweet"), "r") as tweets:
                    ln = {}
                    dt = dts.next().replace('/tweets/all_parcol/', '')[0:10]
                    pos = poss.next()
                    tw = tweets.next()
                    toks = tokenize(tw)
                    tags = pos.split('\t')[1].split()
                    # TODO: probably need to get rid of standalone numbers in
                    # NP grammar, "2015"
                    # an expansion of NP-FST is removing domain specific stop
                    # patterns. "last Wednesday"
                    phrases = fstphrases.extract_from_poses(tags,
                                                            'NP',
                                                            tagset='ark')
                    phrases_deets = []
                    for phrase in phrases:
                        # phrase = [0,1,2] (token positions)
                        start = phrase[0]  # first token position
                        end = phrase[len(phrase) - 1]  # last token position
                        regular = toks[start: end + 1]  # to python slice
                        regular = " ".join([o for o in regular]).strip()
                        normalized = regular.lower()
                        phrases_deets.append({"positions": phrase,
                                              "regular": regular,
                                              "normalized": normalized})
                    ln["pubdate"] = dt
                    ln["os"] = tags
                    ln["tokens"] = toks
                    with open(sys.argv[1].replace(".dates", ".anno"), "a") as outf:
                        json_s = json.dumps(ln)
                        outf.write(json_s + "\n")
