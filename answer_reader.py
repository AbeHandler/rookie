import json
from pprint import pprint
with open('answers.json') as data_file:    
    for line in data_file:
        answer_string = line.replace("\n", "")
        data = json.loads(answer_string)
        print data["name"]