"""Trading Dashboard research MVP. Run: python app.py (Python 3.11+)."""
import json, math, os, random, sqlite3
from datetime import datetime, timedelta, timezone
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path

DB=os.environ.get("TRADING_DB_PATH","data/trading.sqlite3")
TOKEN=os.environ.get("TRADING_INGEST_TOKEN","")
ASSETS={"EURUSD":1.1738,"GBPUSD":1.3421,"USDJPY":149.68,"XAUUSD":3992.5,"BTCUSD":112850,"ETHUSD":4395}
HORIZONS={"short":("Short-term","2–3 trading days",7,1.3),"mid":("Mid-term","2–6 weeks",45,0.8),"long":("Long-term","1–6 months",180,0.45)}
def now(): return datetime.now(timezone.utc).isoformat()
def connect():
    Path(DB).parent.mkdir(parents=True,exist_ok=True)
    c=sqlite3.connect(DB);c.row_factory=sqlite3.Row
    c.executescript("""
    CREATE TABLE IF NOT EXISTS bars(symbol TEXT, ts TEXT, close REAL, source TEXT, demo INTEGER, UNIQUE(symbol,ts,source));
    CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY, source TEXT, external_id TEXT, title TEXT, body TEXT, event_key TEXT, kind TEXT, ts TEXT, raw TEXT, rights TEXT, demo INTEGER, UNIQUE(source,external_id));
    CREATE TABLE IF NOT EXISTS evidence(event_id INTEGER,symbol TEXT,category TEXT,direction REAL,impact REAL,event_key TEXT,ts TEXT,demo INTEGER);
    CREATE TABLE IF NOT EXISTS signals(id INTEGER PRIMARY KEY,symbol TEXT,horizon TEXT,ts TEXT,score INTEGER,category TEXT,direction TEXT,duration TEXT,support REAL,resistance REAL,invalidation TEXT,drivers TEXT,evidence_count INTEGER,model_version TEXT,demo INTEGER);
    CREATE TABLE IF NOT EXISTS ideas(id INTEGER PRIMARY KEY,symbol TEXT,horizon TEXT,direction TEXT,title TEXT,thesis TEXT,entry REAL,stop REAL,target REAL,ts TEXT);
    CREATE TABLE IF NOT EXISTS alerts(id INTEGER PRIMARY KEY,symbol TEXT,comparison TEXT,price REAL,ts TEXT,active INTEGER DEFAULT 1);
    """);return c
def seed(c):
    if c.execute("SELECT COUNT(*) FROM bars").fetchone()[0]:return
    random.seed(20261010)
    t=datetime.now(timezone.utc)
    for symbol,base in ASSETS.items():
        price=base*0.96
        for i in range(210):
            at=t-timedelta(days=210-i)
            if symbol not in ("BTCUSD","ETHUSD") and at.weekday()>4:continue
            price*=1+random.uniform(-.007,.007)
            c.execute("INSERT INTO bars VALUES(?,?,?,?,?)",(symbol,at.isoformat(),price,"synthetic",1))
    categories=["macro","fundamental","social","market","positioning","crypto"]
    for i in range(100):
        at=t-timedelta(days=i*2.2)
        cat=categories[i%6]
        key=f"scenario-{i}"
        cur=c.execute("INSERT INTO events(source,external_id,title,body,event_key,kind,ts,raw,rights,demo) VALUES(?,?,?,?,?,?,?,?,?,1)",
            ("demo",key,["Policy expectations shift","Social commentary sparks debate","Macro outlook updates","Volatility regime changes","Market positioning shifts","Digital asset flow analysis"][i%6],"Synthetic example: illustrates market relevance but is not an actual report.",key,cat,at.isoformat(),json.dumps({"synthetic":True}),"local-demo"))
        for j,sym in enumerate(ASSETS):
            sign=math.sin(i*.53+j*1.13)
            c.execute("INSERT INTO evidence VALUES(?,?,?,?,?,?,?,1)",(cur.lastrowid,sym,cat,sign,0.75,key,at.isoformat()))
    c.commit()
def category(score):
    return "Strong Sell" if score<=19 else "Sell" if score<=39 else "Neutral" if score<=60 else "Buy" if score<=80 else "Strong Buy"
def calculate(c,sym,h):
    name,duration,days,factor=HORIZONS[h]; t=datetime.now(timezone.utc);start=(t-timedelta(days=days)).isoformat()
    rows=c.execute("SELECT * FROM evidence WHERE symbol=? AND ts>=? ORDER BY ts DESC",(sym,start)).fetchall()
    seen=set(); grouped={};score_sum=0;weight_sum=0
    for r in rows:
        key=(r["event_key"],r["category"])
        if key in seen:continue
        seen.add(key)
        age=(t-datetime.fromisoformat(r["ts"])).total_seconds()/86400
        decay=math.exp(-age/max(1,days*.6));weight=r["impact"]*decay*(factor if r["category"]=="social" else 1)
        signed=weight*r["direction"];score_sum+=signed;weight_sum+=weight
        grouped[r["category"]]=grouped.get(r["category"],0)+signed
    adequate=len(seen)>=3 and weight_sum>=.5
    score=max(0,min(100,round(50+42*score_sum/weight_sum))) if adequate else 50
    label=category(score);direction="Bullish" if score>=61 else "Bearish" if score<=39 else "Neutral"
    bars=c.execute("SELECT close FROM bars WHERE symbol=? ORDER BY ts DESC LIMIT ?",(sym,{"short":12,"mid":50,"long":180}[h])).fetchall()
    prices=[x["close"] for x in bars];last=prices[0] if prices else ASSETS[sym]
    support=min(prices) if prices else last;resistance=max(prices) if prices else last
    inv=f"Below {support:.5f}" if direction=="Bullish" else f"Above {resistance:.5f}" if direction=="Bearish" else "Reassess after breakout"
    return dict(symbol=sym,horizon=h,label=name,duration=duration,score=score,category=label,direction=direction,
        support=round(support,5),resistance=round(resistance,5),invalidation=inv,
        drivers={k:round(v/max(weight_sum,.00001)*42,1) for k,v in grouped.items()},
        evidence_count=len(seen),model_version="research-baseline-0.1",demo=True,
        status="UNCALIBRATED · SYNTHETIC DATA",timestamp=now())
def store(c,s):
    c.execute("INSERT INTO signals(symbol,horizon,ts,score,category,direction,duration,support,resistance,invalidation,drivers,evidence_count,model_version,demo) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,1)",
    (s["symbol"],s["horizon"],s["timestamp"],s["score"],s["category"],s["direction"],s["duration"],s["support"],s["resistance"],s["invalidation"],json.dumps(s["drivers"]),s["evidence_count"],s["model_version"]))
    c.commit()
def latest(c,sym,h):
    r=c.execute("SELECT * FROM signals WHERE symbol=? AND horizon=? ORDER BY id DESC LIMIT 1",(sym,h)).fetchone()
    if not r:
        s=calculate(c,sym,h);store(c,s);return s
    return dict(symbol=sym,horizon=h,label=HORIZONS[h][0],duration=r["duration"],score=r["score"],category=r["category"],direction=r["direction"],
      support=r["support"],resistance=r["resistance"],invalidation=r["invalidation"],drivers=json.loads(r["drivers"]),
      evidence_count=r["evidence_count"],model_version=r["model_version"],demo=True,status="UNCALIBRATED · SYNTHETIC DATA",timestamp=r["ts"])
def dashboard(c,sym,h):
    if sym not in ASSETS or h not in HORIZONS:raise ValueError("Unsupported instrument/horizon")
    prices={s:[r["close"] for r in c.execute("SELECT close FROM bars WHERE symbol=? ORDER BY ts DESC LIMIT 45",(s,))][::-1] for s in ASSETS}
    signals={name:latest(c,sym,name) for name in HORIZONS}
    feed=[dict(r) for r in c.execute("SELECT title,body,source,ts,kind FROM events ORDER BY ts DESC LIMIT 15")]
    hist=[dict(r) for r in c.execute("SELECT ts,score,category FROM signals WHERE symbol=? AND horizon=? ORDER BY id DESC LIMIT 40",(sym,h))][::-1]
    return dict(symbol=sym,horizon=h,signal=signals[h],signals=signals,prices=prices,feed=feed,history=hist,
        instruments=list(ASSETS),alerts=[dict(r) for r in c.execute("SELECT * FROM alerts WHERE active=1 ORDER BY id DESC")],
        ideas=[dict(r) for r in c.execute("SELECT * FROM ideas ORDER BY id DESC LIMIT 100")],mode="SYNTHETIC DEMO · RESEARCH ONLY")
class Handler(BaseHTTPRequestHandler):
    def sendjson(self,obj,status=200):
        body=json.dumps(obj,default=str).encode();self.send_response(status)
        self.send_header("Content-Type","application/json");self.send_header("Cache-Control","no-store")
        self.send_header("Content-Length",str(len(body)));self.end_headers();self.wfile.write(body)
    def do_GET(self):
        path=urlparse(self.path).path;query=parse_qs(urlparse(self.path).query)
        if path in ("/","/app.js","/styles.css"):
            name="index.html" if path=="/" else path[1:]
            body=(Path(__file__).resolve().parent/"web"/name).read_bytes()
            self.send_response(200);self.send_header("Content-Type", "text/html" if path=="/" else "application/javascript" if path.endswith(".js") else "text/css")
            self.send_header("Content-Length",str(len(body)));self.end_headers();self.wfile.write(body);return
        if path!="/api/dashboard":return self.sendjson({"error":"Not found"},404)
        with connect() as c:self.sendjson(dashboard(c,query.get("symbol",["EURUSD"])[0],query.get("horizon",["short"])[0]))
    def do_POST(self):
        path=urlparse(self.path).path
        if path not in ("/api/ideas","/api/alerts","/api/ingest"):return self.sendjson({"error":"Not found"},404)
        if path=="/api/ingest" and (not TOKEN or self.headers.get("X-Ingest-Token")!=TOKEN):return self.sendjson({"error":"Admin token required"},403)
        try:
            n=int(self.headers.get("Content-Length","0"))
            if not 1<=n<=100000:raise ValueError("Invalid request size")
            d=json.loads(self.rfile.read(n))
            with connect() as c:
                if path=="/api/ideas":
                    if d.get("symbol") not in ASSETS or d.get("horizon") not in HORIZONS or d.get("direction") not in ("Buy","Sell","Neutral"):raise ValueError("Invalid trade idea")
                    if not str(d.get("title","")).strip() or not str(d.get("thesis","")).strip():raise ValueError("Title and thesis required")
                    c.execute("INSERT INTO ideas(symbol,horizon,direction,title,thesis,entry,stop,target,ts) VALUES(?,?,?,?,?,?,?,?,?)",
                    (d["symbol"],d["horizon"],d["direction"],str(d["title"])[:100],str(d["thesis"])[:2000],d.get("entry"),d.get("stop"),d.get("target"),now()))
                elif path=="/api/alerts":
                    if d.get("symbol") not in ASSETS or d.get("comparison") not in ("above","below") or float(d.get("price",0))<=0:raise ValueError("Invalid price alert")
                    c.execute("INSERT INTO alerts(symbol,comparison,price,ts) VALUES(?,?,?,?)",(d["symbol"],d["comparison"],float(d["price"]),now()))
                else:
                    if d.get("rights") not in ("licensed","authorized","public-domain","metadata-only"):raise ValueError("Explicit data rights required")
                    if not d.get("source") or not d.get("external_id") or not d.get("title"):raise ValueError("Source, ID and title required")
                    impacts=d.get("impacts",{})
                    if not isinstance(impacts,dict) or any(k not in ASSETS or not isinstance(v,(float,int)) or not -1<=v<=1 for k,v in impacts.items()):raise ValueError("Invalid impacts")
                    key=str(d.get("event_key",d["external_id"]))[:120];stamp=str(d.get("timestamp",now()))
                    raw={k:d.get(k) for k in ("source","external_id","title","rights")} if d["rights"]=="metadata-only" else d
                    row=c.execute("SELECT id FROM events WHERE source=? AND external_id=?",(d["source"],d["external_id"])).fetchone()
                    if row:return self.sendjson({"duplicate":True,"id":row["id"]})
                    cur=c.execute("INSERT INTO events(source,external_id,title,body,event_key,kind,ts,raw,rights,demo) VALUES(?,?,?,?,?,?,?,?,?,0)",
                    (d["source"],d["external_id"],str(d["title"])[:240],str(d.get("body",""))[:12000] if d["rights"]!="metadata-only" else "",key,str(d.get("category","social"))[:40],stamp,json.dumps(raw),d["rights"]))
                    for sym,val in impacts.items():c.execute("INSERT INTO evidence VALUES(?,?,?,?,?,?,?,0)",(cur.lastrowid,sym,d.get("category","social"),float(val),.8,key,stamp))
                c.commit()
                if path=="/api/ingest":
                    for sym in impacts:
                        for h in HORIZONS:store(c,calculate(c,sym,h))
            self.sendjson({"ok":True},201)
        except (ValueError,KeyError,TypeError,sqlite3.Error) as e:self.sendjson({"error":str(e)},400)
def main():
    with connect() as c:seed(c)
    host=os.environ.get("HOST","127.0.0.1");port=int(os.environ.get("PORT","8765"))
    print(f"Trading Dashboard research demo: http://{host}:{port}",flush=True)
    ThreadingHTTPServer((host,port),Handler).serve_forever()
if __name__=="__main__":main()
