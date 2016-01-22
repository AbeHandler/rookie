#!/bin/bash
# This script builds all of the indexes rookie needs: whoosh, the meta data file and the db
dropdb 'rookie' --if-exists
createdb -O rookie rookie
python webapp/classes.py
python whooshy/loader.py
python webapp/builddb.py
python facets/build_matrix.py
python webapp/builddb.py