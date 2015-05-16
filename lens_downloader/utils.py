def standarizeurl(url):
    url = url.replace("http://thelensnola.org/", "")
    url.strip("/")
    url.replace("/", "_")
    return url
