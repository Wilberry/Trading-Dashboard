"""Optional authorized RSS/Atom source adapter.

Uses configured feed URLs only; neither fetches X nor circumvents feed paywalls.
Run: TRADING_INGEST_TOKEN=... python -m connectors.rss --config feeds.json
"""
import argparse
import json
import os
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET


ATOM = "{http://www.w3.org/2005/Atom}"
MAX_BYTES = 2_000_000


def iso_timestamp(value, observed_at):
    if not value:
        return observed_at
    try:
        date = parsedate_to_datetime(value)
    except (TypeError, ValueError, IndexError):
        date = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if date.tzinfo is None:
        # Unknown timezone => use observed time, not a guessed timezone.
        return observed_at
    return date.astimezone(timezone.utc).isoformat()


def parse_feed(xml_bytes, *, observed_at=None):
    """RSS 2 and Atom 1 entries; no user-generated directional scores."""
    observed_at = observed_at or datetime.now(timezone.utc).isoformat()
    root = ET.fromstring(xml_bytes)
    records = []
    if root.tag == ATOM + "feed":
        for entry in root.findall(ATOM + "entry"):
            title = entry.findtext(ATOM + "title", default="").strip()
            guid = entry.findtext(ATOM + "id", default="").strip()
            published = entry.findtext(ATOM + "published") or entry.findtext(ATOM + "updated")
            link = next((x.attrib.get("href","") for x in entry.findall(ATOM+"link") if x.attrib.get("rel","alternate")=="alternate"),"")
            if not link:
                link = next((x.attrib.get("href","") for x in entry.findall(ATOM+"link")), "")
            if title and (guid or link):
                records.append(dict(external_id=guid or link,title=title,url=link,timestamp=iso_timestamp(published,observed_at)))
    else:
        for entry in root.findall("./channel/item"):
            title=(entry.findtext("title") or "").strip()
            guid=(entry.findtext("guid") or entry.findtext("link") or "").strip()
            link=(entry.findtext("link") or "").strip()
            published=entry.findtext("pubDate")
            if title and guid:
                records.append(dict(external_id=guid,title=title,url=link,timestamp=iso_timestamp(published,observed_at)))
    return records


def fetch_xml(url):
    u=urlparse(url)
    if u.scheme!="https" or not u.hostname:
        raise ValueError("Only explicitly configured HTTPS feed URLs are supported")
    with urlopen(Request(url,headers={"User-Agent":"TradingDashboardResearch/0.2"}),timeout=15) as response:
        blob=response.read(MAX_BYTES+1)
    if len(blob)>MAX_BYTES:
        raise ValueError("RSS payload exceeds size limit")
    return blob


def post_event(api_url, token, payload):
    if not token:
        raise ValueError("TRADING_INGEST_TOKEN is required")
    if urlparse(api_url).scheme not in ("http","https"):
        raise ValueError("Invalid API URL")
    data=json.dumps(payload).encode()
    with urlopen(Request(api_url.rstrip("/")+"/api/ingest",data=data,headers={
        "Content-Type":"application/json","X-Ingest-Token":token
    },method="POST"),timeout=15) as response:
        return json.loads(response.read())


def ingest_feed(feed, *, api_url, token, dry_run=False):
    """Metadata-only ingest: no full syndicated article text is stored."""
    if feed.get("rights") not in ("licensed","authorized","public-domain","metadata-only"):
        raise ValueError("Every feed must declare permission/retention rights")
    if not feed.get("name") or not feed.get("url"):
        raise ValueError("Feed requires name and URL")
    entries=parse_feed(fetch_xml(feed["url"]))
    count=0
    for entry in entries[:30]:
        if entry["url"] and urlparse(entry["url"]).scheme not in ("https","http"):
            continue
        payload=dict(
            source=feed["name"],external_id=entry["external_id"],title=entry["title"],
            url=entry["url"],timestamp=entry["timestamp"],rights="metadata-only",
            category=feed.get("category","official"),event_key=entry["external_id"],
            impacts={},body=""
        )
        if dry_run:
            print(json.dumps(payload,ensure_ascii=False))
        else:
            post_event(api_url,token,payload)
        count+=1
    return count


def main():
    parser=argparse.ArgumentParser(description="Ingest permitted RSS/Atom metadata into authorized-data mode")
    parser.add_argument("--config",required=True,help="JSON config with a feeds list")
    parser.add_argument("--api-url",default="http://127.0.0.1:8765")
    parser.add_argument("--dry-run",action="store_true")
    args=parser.parse_args()
    with open(args.config,encoding="utf-8") as file: config=json.load(file)
    for feed in config["feeds"]:
        count=ingest_feed(feed,api_url=args.api_url,token=os.getenv("TRADING_INGEST_TOKEN",""),dry_run=args.dry_run)
        print(f"{feed['name']}: {count} feed entries processed")


if __name__=="__main__":
    main()
