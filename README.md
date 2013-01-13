### curtis

A script to scrape the [Edward S. Curtis's The North American Indian](http://curtis.library.northwestern.edu/) site at Northwestern University. For research purposes.

Based largely on Ed Summer's [bell](https://github.com/edsu/bell)

### License

<p xmlns:dct="http://purl.org/dc/terms/" xmlns:vcard="http://www.w3.org/2001/vcard-rdf/3.0#">
  <a rel="license"
     href="http://creativecommons.org/publicdomain/zero/1.0/">
    <img src="http://i.creativecommons.org/p/zero/1.0/88x31.png" style="border-style: none;" alt="CC0" />
  </a>
  <br />
  To the extent possible under law,
  <a rel="dct:publisher"
     href="http://www.trevormunoz.com/">
    <span property="dct:title">Trevor Munoz</span></a>
  has waived all copyright and related or neighboring rights to
  <span property="dct:title">curtis</span>.
This work is published from:
<span property="vcard:Country" datatype="dct:ISO3166"
      content="US" about="http://www.trevormunoz.com/">
  United States</span>.
</p>

### URL Patterns in NU's Edward S. Curtis's The North American Indian
Basic URL patterns:

Base URL—
http://curtis.library.northwestern.edu/curtis/

OCR display for each volume— 
http://curtis.library.northwestern.edu/curtis/ocrtext.cgi?vol=1#nai.01.book.00000003
Grab the "ocrtext" div

Contains links to image display of the form—
viewPage?id=nai.01.book.00000001&size=2&showp=1&volume=1
Lots of metadata in the page headers

Which can be translated to direct image links of the form—
http://digital.library.northwestern.edu/curtis/images/NAIv01/00000001AH.gif (for large size)