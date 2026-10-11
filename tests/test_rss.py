"""Offline tests: RSS and Atom parse without making external network calls."""
import unittest
from connectors.rss import parse_feed, fetch_xml, iso_timestamp

RSS=b"""<?xml version="1.0"?><rss version="2.0"><channel>
<item><title>Interest rate announcement</title>
<guid>press-100</guid><link>https://www.example.org/releases/100</link>
<pubDate>Tue, 06 Oct 2026 14:30:00 GMT</pubDate></item>
</channel></rss>"""
ATOM=b"""<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom">
<entry><id>news-200</id><title>Policy remarks</title>
<link rel="alternate" href="https://www.example.org/news/200"/>
<updated>2026-10-07T12:15:00Z</updated></entry>
</feed>"""


class FeedTests(unittest.TestCase):
    def test_rss_provenance(self):
        items=parse_feed(RSS)
        self.assertEqual(len(items),1)
        self.assertEqual(items[0]["external_id"],"press-100")
        self.assertEqual(items[0]["timestamp"],"2026-10-06T14:30:00+00:00")

    def test_atom_source_link(self):
        item=parse_feed(ATOM)[0]
        self.assertEqual(item["url"],"https://www.example.org/news/200")
        self.assertEqual(item["timestamp"],"2026-10-07T12:15:00+00:00")

    def test_unknown_timezone_uses_first_seen(self):
        seen="2026-10-07T12:00:00+00:00"
        self.assertEqual(iso_timestamp("2026-10-07T11:30:00",seen),seen)

    def test_refuses_insecure_feed_url(self):
        with self.assertRaises(ValueError):
            fetch_xml("http://invalid.example.com/rss.xml")


if __name__=="__main__":
    unittest.main()
