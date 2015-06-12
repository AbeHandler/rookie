from stanford_corenlp_pywrapper import sockwrap

nlp_location = "/Volumes/USB/stanford-corenlp-full-2015-04-20/*"
proc = sockwrap.SockWrap("ner", corenlp_jars=[nlp_location])

output = proc.parse_doc("James took the telescope. He wanted it for his collection")

print output
