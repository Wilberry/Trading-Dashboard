"""Loopback API integration tests; all inputs are locally generated."""
import http.client
import json
import os
import tempfile
import threading
import unittest
from datetime import datetime, timedelta, timezone
from http.server import ThreadingHTTPServer

import app


class IngestionHttpTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.previous=(app.DB,app.DATA_MODE,app.TOKEN)
        app.DB=os.path.join(self.temp.name,"live.sqlite3")
        app.DATA_MODE="live"
        app.TOKEN="offline-test-token"
        with app.connect() as conn:
            pass
        self.server=ThreadingHTTPServer(("127.0.0.1",0),app.Handler)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)
        app.DB,app.DATA_MODE,app.TOKEN=self.previous
        self.temp.cleanup()

    def request(self,method,path,payload=None,auth=False):
        client=http.client.HTTPConnection("127.0.0.1",self.server.server_port,timeout=5)
        headers={"Content-Type":"application/json"}
        if auth:headers["X-Ingest-Token"]="offline-test-token"
        client.request(method,path,body=json.dumps(payload) if payload is not None else None,headers=headers)
        resp=client.getresponse()
        status=resp.status
        body=json.loads(resp.read())
        client.close()
        return status,body

    def test_live_mode_has_no_demo_events_or_prices(self):
        status,data=self.request("GET","/api/dashboard?symbol=EURUSD&horizon=short")
        self.assertEqual(status,200)
        self.assertEqual(data["feed"],[])
        self.assertEqual(data["prices"]["EURUSD"],[])
        self.assertIsNone(data["signal"]["score"])
        self.assertEqual(data["signal"]["category"],"Unavailable")

    def test_imports_require_token_and_rights(self):
        stamp=datetime.now(timezone.utc).isoformat()
        payload={"symbol":"BTCUSD","timestamp":stamp,"close":100.0,"source":"test","rights":"licensed"}
        self.assertEqual(self.request("POST","/api/bars",payload)[0],403)
        self.assertEqual(self.request("POST","/api/bars",{**payload,"rights":"unknown"},True)[0],400)
        self.assertEqual(self.request("POST","/api/bars",payload,True)[0],201)
        with app.connect() as c:
            self.assertEqual(c.execute("SELECT COUNT(*) FROM bars WHERE demo=0").fetchone()[0],1)
            self.assertEqual(c.execute("SELECT COUNT(*) FROM raw_market_data").fetchone()[0],1)

    def test_duplicated_reports_share_canonical_event(self):
        stamp=(datetime.now(timezone.utc)-timedelta(minutes=1)).isoformat()
        base={"timestamp":stamp,"event_key":"shared-announcement","title":"Official announcement",
              "url":"https://example.org/press/1","category":"official","rights":"metadata-only","impacts":{}}
        first={**base,"source":"central-bank","external_id":"press-1"}
        second={**base,"source":"press-agency","external_id":"report-22"}
        self.assertEqual(self.request("POST","/api/ingest",first,True)[0],201)
        self.assertEqual(self.request("POST","/api/ingest",second,True)[0],201)
        code,d=self.request("GET","/api/dashboard?symbol=EURUSD")
        self.assertEqual(code,200)
        self.assertEqual(len(d["feed"]),1)
        self.assertCountEqual(d["feed"][0]["sources"],["central-bank","press-agency"])
        self.assertEqual(d["feed"][0]["url"],"https://example.org/press/1")
        self.assertEqual(self.request("POST","/api/ingest",first,True)[1]["duplicate"],True)
        with app.connect() as c:
            self.assertEqual(c.execute("SELECT COUNT(*) FROM events WHERE demo=0").fetchone()[0],2)

    def test_cannot_ingest_future_event(self):
        future=(datetime.now(timezone.utc)+timedelta(days=3)).isoformat()
        doc={"timestamp":future,"event_key":"unseen","source":"x","external_id":"1","title":"Future news",
             "rights":"metadata-only","impacts":{}}
        status,_=self.request("POST","/api/ingest",doc,True)
        self.assertEqual(status,400)


if __name__=="__main__":
    unittest.main()
