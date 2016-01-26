aws s3 cp ~/research/rookie/webapp/static/js/bundle.js s3://rookie2/js/bundle.js --acl public-read-write
aws s3 sync ~/research/rookie/webapp/static/css/ s3://rookie2/css/ --acl public-read-write