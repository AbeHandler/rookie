import ner
tagger = ner.SocketNER(host='localhost', port=8080)
print tagger.get_entities("University of California \
    is located in California, United States")
print tagger.json_entities("Tuitiion at UC Berkeley can run upwards of $40,000 a year")
