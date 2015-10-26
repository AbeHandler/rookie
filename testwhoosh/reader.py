from whoosh.index import open_dir
from whoosh.qparser import QueryParser

ix = open_dir('indexdir')
qp = QueryParser("content", schema=ix.schema)
q = qp.parse(u"Marlin Gusman")


with ix.searcher() as s:
    results = s.search(q)
    for i in results:
        print i