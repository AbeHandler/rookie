'''
Merge the aliases found from counter3
'''
import pickle
import pdb
from rookie import log
import json
from rookie import files_location

keys = [o.replace("\n", "") for o in open("keys.csv", "r")]

al = pickle.load(open(files_location + "aliases.p"))


for key in al.keys():
    try:
        with (open("data/pmis/" + key + ".json", "r")) as infile:
            key_pmis = json.load(infile)
        key_aliases = al[key]
        for alias in key_aliases:
            with (open("data/pmis/" + alias + ".json", "r")) as infile:
                alias_pmis = json.load(infile)
                key_pmis = key_pmis + alias_pmis
            try:
                keys.remove(alias)
            except ValueError:
                log.error("cant remove {}".format(alias))
        with (open("data/pmis/" + key + ".json", "w")) as outfile:
            json.dump(key_pmis, outfile)
    except IOError:
        log.info(key)
    except ValueError:
        log.info(key)
    # deal with instances.

with (open("keys_reduced.csv", "w")) as outfile:
    for key in keys:
        outfile.write(key + "\n")
