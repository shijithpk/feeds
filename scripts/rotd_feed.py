"""Build public/rotd_uk.xml from the Record of the Day track archive.

The site blocks a second request for the page made right after the first, and
feed-me-up-scotty always loads a page twice, so this fetches it once instead.
Entry titles match what scotty produced ("<track title> <artist>").
"""
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

from bs4 import BeautifulSoup

URL = "https://www.recordoftheday.com/track-archive"
OUT = "public/rotd_uk.xml"
ATOM = "http://www.w3.org/2005/Atom"

request = urllib.request.Request(URL, headers={
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:139.0) Gecko/20100101 Firefox/139.0",
})
with urllib.request.urlopen(request, timeout=60) as response:
    soup = BeautifulSoup(response.read(), "html.parser")

now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
ET.register_namespace("", ATOM)
feed = ET.Element(f"{{{ATOM}}}feed")
ET.SubElement(feed, f"{{{ATOM}}}id").text = URL
ET.SubElement(feed, f"{{{ATOM}}}title").text = "Record Of The Day UK"
ET.SubElement(feed, f"{{{ATOM}}}updated").text = now
ET.SubElement(feed, f"{{{ATOM}}}link", href=URL)

count = 0
for box in soup.select("div.super-box"):
    title = box.select_one("h3.title")
    artist = box.select_one("p.artist")
    if title is None or artist is None:
        continue
    link = box.parent.select_one(":scope > a.link-box")
    href = link["href"] if link is not None and link.get("href") else URL
    entry = ET.SubElement(feed, f"{{{ATOM}}}entry")
    ET.SubElement(entry, f"{{{ATOM}}}title").text = f"{title.get_text().strip()} {artist.get_text().strip()}"
    ET.SubElement(entry, f"{{{ATOM}}}id").text = href
    ET.SubElement(entry, f"{{{ATOM}}}link", href=href)
    ET.SubElement(entry, f"{{{ATOM}}}updated").text = now
    count += 1

if count == 0:
    sys.exit(f"No Record of the Day entries found on {URL} (page title: {soup.title.string if soup.title else None!r})")

ET.indent(feed)
ET.ElementTree(feed).write(OUT, encoding="utf-8", xml_declaration=True)
print(f"Wrote {count} entries to {OUT}")
