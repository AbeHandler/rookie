import ner
import json

tagger = ner.SocketNER(host='localhost', port=8080)

types = tagger.json_entities("Tuitiion at UC Berkeley can run upwards of $40,000 a year")
types = json.loads(types)

print type(types)