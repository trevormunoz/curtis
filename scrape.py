# import os
import json
import re
import urlparse
import lxml.html
import cssselect
import time
import logging
import requests
import requests_cache

logging.basicConfig(level=logging.INFO)

SEED_URLS = [ \
"http://curtis.library.northwestern.edu/curtis/ocrtext.cgi?\
vol={0}#nai.01.book.00000003" \
.format(n) for n in range(1, 21)]


def make_download_throttle(timeout=1.0):

    """
    Returns a response hook function which sleeps for ``timeout`` seconds if response is not cached
    """
    def hook(response):

        """
        Response hook function
        """
        if not hasattr(response, 'from_cache'):
            logging.info(\
                "{0} not in cache. Sleeping {1} seconds"\
                .format(response.url, timeout) \
                )
            time.sleep(timeout)
        else:
            logging.info("{0} already seen. In cache".format(response.url))
            return response
    return hook


def get_response_body(datastore):

    """
    Returns a dictionary containing the response body from each request
    """
    volumes = {}
    for url in SEED_URLS:
        resp = requests_cache.backends.sqlite.DbCache.\
        get_response_and_time(datastore, url)[0]

        volumes[resp.url] = resp.content
    return volumes


def get_page_links(urldict):

    """
    Parses a list of cached html pages. Returns a dictionary of page image links
    """
    target_pages = {}
    query_pattern = re.compile(r'book')

    for k in urldict.keys():
        root = lxml.html.fromstring(urldict[k])
        for element in root.cssselect("div.ocrtext a"):
            try:
                img_link = element.attrib["href"]
                parsed = urlparse.urlparse(img_link)
                if re.search(query_pattern, parsed.query) is not None:
                    img_query_string = re.split('&', img_link)
                    img_id = re.split('id=', img_query_string[0])[1]
                    page = urlparse.urljoin(\
                        'http://curtis.library.northwestern.edu/curtis/', \
                        re.sub('size=2', 'size=3', img_link))
                    target_pages[img_id] = page
            except KeyError:
                pass
    return target_pages

if __name__ == '__main__':
    requests_cache.configure("nai")

    SESSION = requests.Session(hooks={'response': make_download_throttle()})
    CACHE = requests_cache.get_cache()

    DATASET = get_response_body(CACHE)
    VIEW = get_page_links(DATASET)
    logging.info(VIEW.keys())
