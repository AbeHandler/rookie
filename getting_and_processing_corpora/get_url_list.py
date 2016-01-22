from rookie.datamanagement.lensdownloader import get_all_urls

if __name__ == '__main__':
    urls = get_all_urls()
    for url in urls:
        print url
