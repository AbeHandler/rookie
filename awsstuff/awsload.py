import glob
import json
import pdb
from rookie import processed_location

files_to_check = glob.glob(processed_location + "/*")

chuunks = 15


def upload_doc(filename, counter):
    with (open(filename, "r")) as infile:
        indata = json.load(infile)
    upload = {}
    upload['type'] = 'add'
    upload['id'] = counter
    counter = counter + 1
    data = {}
    data['text'] = indata["lines"]
    data['headline'] = indata["headline"]
    data['url'] = indata["url"]
    upload['fields'] = data
    return upload


for counter in range(0, len(files_to_check)):
    try:
        upload_doc(files_to_check[counter], counter)
        print counter
    except ValueError:
        pass
