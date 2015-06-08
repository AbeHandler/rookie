import ner
tagger = ner.SocketNER(host='localhost', port=8080)
print tagger.get_entities("University of California \
    is located in California, United States")
print tagger.json_entities("Alice went to the Museum of Natural History.")
