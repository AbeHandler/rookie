import csv

all_things = []

with open('graph.csv', 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=',',
                        quotechar='"')
    for row in reader:
        all_things.append(row)
        print len(all_things)

all_types = set([i[0] for i in all_things])

print len(all_types)