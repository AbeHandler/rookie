'''assume input is paste'd output from column store w/ .txt extension'''
import sys
import re
import os

try:
    os.remove(sys.argv[1].replace(".txt", ".tweet"))
except OSError:
    pass

try:
    os.remove(sys.argv[1].replace(".txt", ".dates"))
except OSError:
    pass

with open(sys.argv[1], "r") as inf:
    for ln in inf:
        ln = ln.replace('\n', "")
        dt = re.match('^[^:]+:', ln).group(0)
        ln = ln.replace(dt, "")
        if "/2016-" in dt:
            with open(sys.argv[1].replace(".txt", ".dates"), "a") as outf:
                outf.write(dt + "\n")
            with open(sys.argv[1].replace(".txt", ".tweet"), "a") as outf:
                outf.write(ln + "\n")
