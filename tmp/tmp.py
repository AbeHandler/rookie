from snippets.utils import flip
from collections import Counter

winners = []

for i in range(0, 1000):
    winners.append(flip(.2,.2,.2))

print Counter(winners)