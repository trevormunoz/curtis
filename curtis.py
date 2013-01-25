import re
import lxml.html
import cssselect
import time
import dateutil.parser as parser
import logging
import urlparse
from collections import OrderedDict
import json
import requests
import requests_cache

logging.basicConfig(filename="curtis.log", level=logging.INFO)

NAI_DATA = {}

class NULCurtis(object):

    """
    A class for encapsulating interactions with
    Northwestern University's Edward S. Curtis North American Indian site
    """
    def __init__(self):
        self.seed_urls = [\
        "http://curtis.library.northwestern.edu/curtis/ocrtext.cgi?vol={0}"\
        .format(n) for n in range(1, 21)]

        # Setup a session with at least a 1.0 second throttle on requests
        self.session = requests.Session(\
            hooks={'response': make_download_throttle()}\
            )

        # Setup a `requests_cache.backends.sqlite` object and fetch seed urls.
        # Querying the cache object will return tuple containing a
        # `requests.models.Response` object and a datetime for the request
        requests_cache.configure("nai")
        for url in self.seed_urls:
            self.session.get(url)
        self.cache = requests_cache.get_cache()

    def get_response(self, url):

        """
        Takes a url and returns a tuple containing the cached response
        and a timestamp for the response
        """
        response_tuple = self.cache.get_response_and_time(url)
        # tree = lxml.html.fromstring(response_tuple[0].content)
        return response_tuple


def make_download_throttle(timeout=1.0):

    """
    Returns a response hook function which sleeps
    for ``timeout`` seconds if response is not cached
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


def grab_volume_data(response_tuple):

    """
    Creates a dictionary representing metadata about a volume
    of Edward Curtis's North American Indian
    """
    def clean_up_strings(strarg):

        """
        Strip out whitespace padding in OCR output
        """
        stage1 = strarg.lstrip().rstrip()
        stage2 = re.sub('\t', ' ', stage1)
        stage3 = re.sub('\n', ' ', stage2)
        stage4 = ' '.join(re.split('\W+', stage3, flags=re.UNICODE)).rstrip()
        return stage4

    root = lxml.html.fromstring(response_tuple[0].content)

    # Create a volume identifier from `name` attribute on links
    name_link = re.match(r'[a-z\.0-9]*(book|port)(?=\.)', \
            root.cssselect("div.ocrtext a[name]")[0].attrib['name'])
    volume_id = name_link.group(0)

    # Parse volume-level metadata from html page into a dictionary
    html_metatags = root.cssselect("meta[name]")
    html_metadata_dict = {e.attrib['name']: e.attrib['content'] \
        for e in html_metatags}

    # Grab ocr text output
    text_div = root.cssselect("div.ocrtext")
    text = text_div[0].text_content()
    ocr_blobs = re.split(r'\{view\s.*\}?', text)
    volume_title = clean_up_strings(ocr_blobs[0])
    page_ocr = [clean_up_strings(p) for p in ocr_blobs[1:]]

    # Grab links to page images
    rel_links = text_div[0].cssselect("a[href]")
    absolute_links = [\
    urlparse.urljoin('http://curtis.library.northwestern.edu/curtis/',\
     re.sub('size=2', 'size=3', l.attrib['href']))\
    for l in rel_links]
    img_links = []
    cache_instance = NULCurtis()
    for ahref in absolute_links:
        img_page = lxml.html.fromstring(cache_instance.get_response(ahref)[0]\
            .content)
        for img in img_page.cssselect("td > img"):
            if re.search(r'NAI|iencurt', img.attrib['src']) is not None:
                img_links.append(img.attrib['src'])

    page_data = OrderedDict(zip(img_links, page_ocr))

    NAI_DATA[volume_id] = {\
        'url': response_tuple[0].url,\
        'dc.title': volume_title,\
        'dc.description': html_metadata_dict['dc.description'],\
        # 'dc.subject': html_metadata_dict['dc.subject'],\
        'dc.publisher': html_metadata_dict['dc.publisher'],\
        'dc.date.modified': parser.parse(\
            html_metadata_dict['dc.date.modified'])\
        .isoformat(),\
        'dc.date.retrieved': response_tuple[1].isoformat(),\
        'dc.language': html_metadata_dict['dc.language'],\
        'pages': page_data
        }

if __name__ == '__main__':
    nul = NULCurtis()
    for u in nul.seed_urls:
        grab_volume_data(nul.get_response(u))

        for k in NAI_DATA.keys():
            logging.info("Saving data for file: {0}".format(k))
            data_json = json.dumps(NAI_DATA[k], indent=4)
            fname = k + ".json"
            with open(fname, 'w') as outfile:
                outfile.write(data_json)
