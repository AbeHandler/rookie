rm *html
rm files/*
rm out.txt
touch out.txt

#curl for each summary page
for i in {1..413}
do
   curl -o "$i"".html" "http://thelensnola.org/page/$i/?s="
done

#get the urls from the summaries
python summaries_extractor.py

k=1
while read line; do
    fn=$(echo $line | cut -d "/" -f 4,5,6,7 | tr "/" "_")
    curl $line -o "files/""$fn"".html"
done < out.txt

rm files/corrections_.txt

rm files/argolinkroundups* #we dont want these

python preprocessor.py