from fabric.api import local

def s3():
    local("aws s3 cp webapp/static/js/bundle.js s3://rookie2/js/bundle.js --acl public-read-write")