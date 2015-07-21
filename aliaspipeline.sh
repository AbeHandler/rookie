py tmp2.py > allpairs
echo "" > app.log
cat allpairs | parallel -j20 --eta 'python tmp.py {}'