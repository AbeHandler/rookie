import csv

all_things = []

with open('graph.csv', 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=',',
                        quotechar='"')
    for row in reader:
        all_things.append(row)
        if len(all_things) % 10000 == 0:
            print len(all_things)

corpus_length = len(all_things)

total_one = [i[0] for i in all_things]
total_two = [i[1] for i in all_things]

print len(total_two)
print len(total_one)
