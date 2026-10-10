import os, tempfile, unittest
from unittest.mock import patch
import app
class TradingDashboardSmokeTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory()
  self.old=app.DB
  app.DB=os.path.join(self.tmp.name,"test.db")
  self.conn=app.connect()
  app.seed(self.conn)
 def tearDown(self):
  self.conn.close();app.DB=self.old;self.tmp.cleanup()
 def test_market_instruments(self):
  self.assertEqual(set(app.ASSETS),{"EURUSD","GBPUSD","USDJPY","XAUUSD","BTCUSD","ETHUSD"})
 def test_three_horizon_models(self):
  scores=[]
  for name in app.HORIZONS:
   s=app.calculate(self.conn,"EURUSD",name)
   self.assertGreaterEqual(s["score"],0)
   self.assertLessEqual(s["score"],100)
   self.assertTrue(s["duration"])
   self.assertTrue(s["invalidation"])
   scores.append(s["score"])
  self.assertGreaterEqual(len(set(scores)),2)
 def test_signals_are_append_only(self):
  s=app.calculate(self.conn,"BTCUSD","short")
  app.store(self.conn,s)
  app.store(self.conn,s)
  self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM signals WHERE symbol='BTCUSD' AND horizon='short'").fetchone()[0],2)
 def test_snapshot_api(self):
  data=app.dashboard(self.conn,"XAUUSD","mid")
  self.assertEqual(len(data["signals"]),3)
  self.assertTrue(data["feed"])
  self.assertTrue(data["prices"]["XAUUSD"])
  self.assertIn("SYNTHETIC",data["mode"])
 def test_seed_not_duplicated(self):
  before=self.conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
  app.seed(self.conn)
  self.assertEqual(before,self.conn.execute("SELECT COUNT(*) FROM events").fetchone()[0])
if __name__=="__main__":unittest.main()
