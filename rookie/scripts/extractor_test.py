import csv
import itertools

all_things = []

with open('graph.csv', 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=',',
                        quotechar='"')
    for row in reader:
        all_things.append(row)
        if len(all_things) % 10000 == 0:
            print len(all_things)

corpus_length = len(all_things)

terms = list(set([i[0] for i in all_things]))

print len(terms)

for term in terms:
    with open('counts.csv', 'a') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter='\t',quotechar='"')
        spamwriter.writerow([term,len([i for i in all_things if i[0] == term])])


