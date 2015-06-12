from stanford_corenlp_pywrapper import sockwrap

nlp_location = "/Volumes/USB/stanford-corenlp-full-2015-04-20/*"
proc = sockwrap.SockWrap("ner", corenlp_jars=[nlp_location])

output = proc.parse_doc("Orleans Parish Communication District leaders said that may be impossible due to state law enabling public participation in governmental budgeting.")

print output['sentences'][0]
