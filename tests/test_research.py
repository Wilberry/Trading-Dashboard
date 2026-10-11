"""Regression tests: no demo/live contamination; no look-ahead in studies."""
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

import app
from research import event_study, parse_utc


class ResearchFoundationTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.previous_db = app.DB
        self.previous_mode = app.DATA_MODE
        app.DB = os.path.join(self.dir.name, "test.sqlite3")
        app.DATA_MODE = "demo"
        self.db = app.connect()
        app.seed(self.db)

    def tearDown(self):
        self.db.close()
        app.DB = self.previous_db
        app.DATA_MODE = self.previous_mode
        self.dir.cleanup()

    def test_historical_study_uses_completed_outcomes_only(self):
        result = event_study(self.db, "EURUSD", "short", demo=True)
        self.assertTrue(result["sufficient"])
        self.assertGreaterEqual(result["count"], 8)
        self.assertEqual(result["observations_forward"], 3)
        self.assertLessEqual(result["positive_fraction"], 1)

    def test_event_study_as_of_excludes_future_data(self):
        cutoff = datetime.now(timezone.utc) - timedelta(days=210)
        result = event_study(self.db, "BTCUSD", "short", demo=True, as_of=cutoff.isoformat())
        self.assertFalse(result["sufficient"])
        self.assertEqual(result["count"], 0)

    def test_event_study_deduplicates_canonical_events(self):
        old = event_study(self.db, "EURUSD", "short", demo=True)["count"]
        first = self.db.execute("SELECT event_key,ts FROM events WHERE demo=1 ORDER BY ts LIMIT 1").fetchone()
        self.db.execute("INSERT INTO events(source,external_id,title,body,event_key,kind,ts,raw,rights,demo) VALUES(?,?,?,?,?,?,?,?,?,1)",
            ("duplicate-reporter", "dup-1", "Second reporter", "", first["event_key"], "macro", first["ts"], "{}", "local-demo"))
        eid = self.db.execute("SELECT id FROM events WHERE source='duplicate-reporter'").fetchone()[0]
        self.db.execute("INSERT INTO evidence VALUES(?,?,?,?,?,?,?,1)",
            (eid,"EURUSD","macro",1.0,.8,first["event_key"],first["ts"]))
        self.db.commit()
        new = event_study(self.db, "EURUSD", "short", demo=True)["count"]
        self.assertEqual(old, new)

    def test_live_mode_never_reads_seeded_demo_data(self):
        app.DATA_MODE = "live"
        snapshot = app.dashboard(self.db,"EURUSD","short")
        self.assertEqual(snapshot["prices"]["EURUSD"],[])
        self.assertEqual(snapshot["feed"],[])
        self.assertIsNone(snapshot["signal"]["score"])
        self.assertEqual(snapshot["signal"]["category"],"Unavailable")
        self.assertEqual(snapshot["signal"]["duration"],"Not estimated")
        self.assertEqual(snapshot["study"]["short"]["count"],0)

    def test_live_mode_accepts_only_real_flagged_evidence(self):
        app.DATA_MODE = "live"
        stamp = datetime.now(timezone.utc)
        for i in range(5):
            at=(stamp-timedelta(days=i*.35)).isoformat()
            k=f"source-{i}"
            cur=self.db.execute(
              "INSERT INTO events(source,external_id,title,body,event_key,kind,ts,raw,rights,demo) VALUES(?,?,?,?,?,?,?,?,?,0)",
              ("authorized",k,"Verified scenario","",k,"macro",at,"{}","licensed"))
            self.db.execute("INSERT INTO evidence VALUES(?,?,?,?,?,?,?,0)",
                (cur.lastrowid,"EURUSD","macro",.7,.9,k,at))
        for i in range(8):
            at=(stamp-timedelta(days=i)).isoformat()
            self.db.execute("INSERT INTO bars VALUES(?,?,?,?,0)",("EURUSD",at,1.1+i*.001,"licensed"))
        self.db.commit()
        real=app.calculate(self.db,"EURUSD","short")
        self.assertIsNotNone(real["score"])
        self.assertFalse(real["demo"])
        self.assertGreater(real["score"],50)
        app.DATA_MODE="demo"
        demo=app.calculate(self.db,"EURUSD","short")
        self.assertTrue(demo["demo"])

    def test_refreshes_on_stale_snapshot_without_erasing_history(self):
        first=app.latest(self.db,"EURUSD","short")
        count=self.db.execute("SELECT count(*) FROM signals WHERE symbol='EURUSD' and horizon='short' and demo=1").fetchone()[0]
        second=app.latest(self.db,"EURUSD","short")
        self.assertEqual(first["timestamp"],second["timestamp"])
        self.assertEqual(count,self.db.execute("SELECT count(*) FROM signals WHERE symbol='EURUSD' and horizon='short' and demo=1").fetchone()[0])

    def test_explicit_utc_timestamp_required(self):
        with self.assertRaises(ValueError):
            parse_utc("2026-10-10T12:30:00")
        self.assertEqual(parse_utc("2026-10-10T14:30:00+02:00").hour,12)


if __name__ == "__main__":
    unittest.main()
