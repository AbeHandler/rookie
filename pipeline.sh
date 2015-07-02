rm graph.csv
dropdb rookie
createdb rookie
python rookie/db.py
python rookie/scripts/extractor.py
python rookie/scripts/extractor2.py