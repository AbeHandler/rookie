workon rookie
rm keys.csv.gz
rm data/windows/*
rm data/windows/.*gz
rm data/pmis/*
rm data/pmis/.*gz
python rookie/scripts/counter.py
gzip keys.csv
find data/pmis -name '*json'  -exec gzip "{}" \;
find data/windows -name '*json'  -exec gzip "{}" \;
./deployapp.sh
