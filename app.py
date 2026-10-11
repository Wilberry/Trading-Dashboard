"""Trading Dashboard research MVP. Run: python app.py (Python 3.11+)."""
import hmac, json, math, os, random, sqlite3
from research import event_study, parse_utc
from datetime import datetime, timedelta, timezone
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from contextlib import closing
from urllib.parse import urlparse, parse_qs
from pathlib import Path

DATA_MODE=os.environ.get("TRADING_DATA_MODE","demo").lower()
if DATA_MODE not in ("demo","live"):
    raise ValueError("TRADING_DATA_MODE must be demo or live")
DB=os.environ.get("TRADING_DB_PATH",f"data/trading_{DATA_MODE}.sqlite3")
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
    CREATE TABLE IF NOT EXISTS raw_market_data(id INTEGER PRIMARY KEY,symbol TEXT,ts TEXT,source TEXT,rights TEXT,payload TEXT,received_at TEXT,UNIQUE(symbol,ts,source));
    """);return c
def seed(c):
    if DATA_MODE!="demo":return
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
    flag=int(DATA_MODE=="demo")
    rows=c.execute("SELECT * FROM evidence WHERE symbol=? AND demo=? AND ts>=? AND ts<=? ORDER BY ts DESC",(sym,flag,start,t.isoformat())).fetchall()
    seen=set(); grouped={};score_sum=0;weight_sum=0
    for r in rows:
        key=r["event_key"]
        if key in seen:continue
        seen.add(key)
        age=(t-datetime.fromisoformat(r["ts"])).total_seconds()/86400
        decay=math.exp(-age/max(1,days*.6));weight=r["impact"]*decay*(factor if r["category"]=="social" else 1)
        signed=weight*r["direction"];score_sum+=signed;weight_sum+=weight
        grouped[r["category"]]=grouped.get(r["category"],0)+signed
    adequate=len(seen)>=3 and weight_sum>=.5
    score=max(0,min(100,round(50+42*score_sum/weight_sum))) if adequate else None
    label=category(score) if score is not None else "Unavailable"
    direction=("Bullish" if score>=61 else "Bearish" if score<=39 else "Neutral") if score is not None else "Insufficient data"
    bars=c.execute("SELECT close FROM bars WHERE symbol=? AND demo=? AND ts<=? ORDER BY ts DESC LIMIT ?",(sym,flag,t.isoformat(),{"short":12,"mid":50,"long":180}[h])).fetchall()
    prices=[x["close"] for x in bars]
    required_bars={"short":6,"mid":20,"long":60}[h]
    if len(prices)<required_bars or not adequate:
        score=None;label="Unavailable";direction="Insufficient data"
    if score is None:
        duration="Not estimated"
    support=min(prices) if score is not None else None
    resistance=max(prices) if score is not None else None
    inv=f"Below {support:.5f}" if support is not None and direction=="Bullish" else f"Above {resistance:.5f}" if resistance is not None and direction=="Bearish" else "Not estimated"
    return dict(symbol=sym,horizon=h,label=name,duration=duration,score=score,category=label,direction=direction,
        support=round(support,5) if support is not None else None,resistance=round(resistance,5) if resistance is not None else None,invalidation=inv,
        drivers={k:round(v/max(weight_sum,.00001)*42,1) for k,v in grouped.items()},
        evidence_count=len(seen),model_version="research-baseline-0.2",demo=bool(flag),
        status=("UNCALIBRATED · SYNTHETIC DATA" if flag else "UNCALIBRATED · AUTHORIZED DATA") if score is not None else "INSUFFICIENT DATA — NO SIGNAL",timestamp=now())
def store(c,s):
    c.execute("INSERT INTO signals(symbol,horizon,ts,score,category,direction,duration,support,resistance,invalidation,drivers,evidence_count,model_version,demo) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
    (s["symbol"],s["horizon"],s["timestamp"],s["score"],s["category"],s["direction"],s["duration"],s["support"],s["resistance"],s["invalidation"],json.dumps(s["drivers"]),s["evidence_count"],s["model_version"],int(s["demo"])))
    c.commit()
def latest(c,sym,h):
    flag=int(DATA_MODE=="demo")
    r=c.execute("SELECT * FROM signals WHERE symbol=? AND horizon=? AND demo=? ORDER BY id DESC LIMIT 1",(sym,h,flag)).fetchone()
    refresh={"short":300,"mid":3600,"long":21600}[h]
    stamp=now()
    newest_event=c.execute("SELECT MAX(ts) FROM evidence WHERE symbol=? AND demo=?",(sym,flag)).fetchone()[0]
    newest_bar=c.execute("SELECT MAX(ts) FROM bars WHERE symbol=? AND demo=?",(sym,flag)).fetchone()[0]
    should_update=not r or (parse_utc(stamp)-parse_utc(r["ts"])).total_seconds()>=refresh
    if r:
        should_update=should_update or any(
            date and parse_utc(date)>parse_utc(r["ts"])
            for date in (newest_event,newest_bar))
    if should_update:
        s=calculate(c,sym,h);store(c,s);return s
    adequate=(r["score"] is not None and r["support"] is not None)
    return dict(symbol=sym,horizon=h,label=HORIZONS[h][0],duration=r["duration"],score=r["score"],category=r["category"],direction=r["direction"],
      support=r["support"],resistance=r["resistance"],invalidation=r["invalidation"],drivers=json.loads(r["drivers"]),
      evidence_count=r["evidence_count"],model_version=r["model_version"],demo=bool(flag),
      status=("UNCALIBRATED · SYNTHETIC DATA" if flag else "UNCALIBRATED · AUTHORIZED DATA") if adequate else "INSUFFICIENT DATA — NO SIGNAL",timestamp=r["ts"])
def dashboard(c,sym,h):
    if sym not in ASSETS or h not in HORIZONS:raise ValueError("Unsupported instrument/horizon")
    flag=int(DATA_MODE=="demo")
    prices={s:[r["close"] for r in c.execute("SELECT close FROM bars WHERE symbol=? AND demo=? AND ts<=? ORDER BY ts DESC LIMIT 45",(s,flag,now()))][::-1] for s in ASSETS}
    signals={name:latest(c,sym,name) for name in HORIZONS}
    feed=[]
    canonical={}
    for r in c.execute("SELECT title,body,source,ts,kind,rights,event_key,demo,raw FROM events WHERE demo=? ORDER BY ts DESC LIMIT 150",(flag,)):
        record=dict(r)
        payload=json.loads(record.pop("raw") or "{}")
        record["url"]=payload.get("url","")
        key=record["event_key"]
        if key not in canonical:
            record["sources"]=[record["source"]]
            canonical[key]=record
            feed.append(record)
        elif record["source"] not in canonical[key]["sources"]:
            canonical[key]["sources"].append(record["source"])
    feed=feed[:15]
    hist=[dict(r) for r in c.execute("SELECT ts,score,category FROM signals WHERE symbol=? AND horizon=? AND demo=? AND score IS NOT NULL ORDER BY id DESC LIMIT 40",(sym,h,flag))][::-1]
    return dict(symbol=sym,horizon=h,signal=signals[h],signals=signals,prices=prices,feed=feed,history=hist,
        instruments=list(ASSETS),alerts=[dict(r) for r in c.execute("SELECT * FROM alerts WHERE active=1 ORDER BY id DESC")],
        ideas=[dict(r) for r in c.execute("SELECT * FROM ideas ORDER BY id DESC LIMIT 100")],
        study={h:event_study(c,sym,h,demo=bool(flag)) for h in HORIZONS},
        mode="SYNTHETIC DEMO · RESEARCH ONLY" if flag else "AUTHORIZED-DATA MODE · PROVIDERS NOT CONNECTED")
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
        if path not in ("/api/dashboard","/api/study"):return self.sendjson({"error":"Not found"},404)
        try:
            sym=query.get("symbol",["EURUSD"])[0]
            horizon=query.get("horizon",["short"])[0]
            if sym not in ASSETS or horizon not in HORIZONS:raise ValueError("Unsupported instrument/horizon")
            with closing(connect()) as c:
                result=dashboard(c,sym,horizon) if path=="/api/dashboard" else event_study(c,sym,horizon,demo=DATA_MODE=="demo")
            self.sendjson(result)
        except (ValueError,sqlite3.Error) as exc:self.sendjson({"error":str(exc)},400)
    def do_POST(self):
        path=urlparse(self.path).path
        if path not in ("/api/ideas","/api/alerts","/api/ingest","/api/bars"):return self.sendjson({"error":"Not found"},404)
        if path in ("/api/ingest","/api/bars"):
            if DATA_MODE!="live":return self.sendjson({"error":"Authorized imports require TRADING_DATA_MODE=live"},409)
            if not TOKEN or not hmac.compare_digest(self.headers.get("X-Ingest-Token",""),TOKEN):
                return self.sendjson({"error":"Admin token required"},403)
        elif DATA_MODE=="live":
            return self.sendjson({"error":"Personal writes disabled pending user authentication"},403)
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
                elif path=="/api/bars":
                    if d.get("rights") not in ("licensed","authorized","public-domain"):
                        raise ValueError("Explicit price data rights required")
                    sym=d.get("symbol")
                    if sym not in ASSETS:raise ValueError("Unsupported instrument")
                    if not str(d.get("source","")).strip():raise ValueError("Price provider source required")
                    price=float(d["close"])
                    if not math.isfinite(price) or price<=0:raise ValueError("Close must be a finite positive number")
                    stamp=parse_utc(d["timestamp"])
                    if stamp>datetime.now(timezone.utc)+timedelta(minutes=5):
                        raise ValueError("Future-dated price bar refused")
                    src=str(d["source"])[:100]
                    c.execute("INSERT OR IGNORE INTO bars(symbol,ts,close,source,demo) VALUES(?,?,?,?,0)",
                      (sym,stamp.isoformat(),price,src))
                    c.execute("INSERT OR IGNORE INTO raw_market_data(symbol,ts,source,rights,payload,received_at) VALUES(?,?,?,?,?,?)",
                      (sym,stamp.isoformat(),src,d["rights"],json.dumps(d,sort_keys=True),now()))
                else:
                    if d.get("rights") not in ("licensed","authorized","public-domain","metadata-only"):raise ValueError("Explicit data rights required")
                    if not d.get("source") or not d.get("external_id") or not d.get("title"):raise ValueError("Source, ID and title required")
                    impacts=d.get("impacts",{})
                    if not isinstance(impacts,dict) or any(k not in ASSETS or not isinstance(v,(float,int)) or not -1<=v<=1 for k,v in impacts.items()):raise ValueError("Invalid impacts")
                    key=str(d.get("event_key",d["external_id"]))[:120]
                    stamp=parse_utc(d.get("timestamp",now()))
                    if stamp>datetime.now(timezone.utc)+timedelta(minutes=5):
                        raise ValueError("Future-dated social/news event refused")
                    stamp=stamp.isoformat()
                    url=d.get("url","")
                    if url and urlparse(str(url)).scheme!="https":
                        raise ValueError("External source URL must be HTTPS")
                    raw={k:d.get(k) for k in ("source","external_id","title","rights","url","timestamp","event_key","category")} if d["rights"]=="metadata-only" else d
                    row=c.execute("SELECT id FROM events WHERE source=? AND external_id=?",(d["source"],d["external_id"])).fetchone()
                    if row:return self.sendjson({"duplicate":True,"id":row["id"]})
                    cur=c.execute("INSERT INTO events(source,external_id,title,body,event_key,kind,ts,raw,rights,demo) VALUES(?,?,?,?,?,?,?,?,?,0)",
                    (d["source"],d["external_id"],str(d["title"])[:240],str(d.get("body",""))[:12000] if d["rights"]!="metadata-only" else "",key,str(d.get("category","social"))[:40],stamp,json.dumps(raw),d["rights"]))
                    for sym,val in impacts.items():c.execute("INSERT INTO evidence VALUES(?,?,?,?,?,?,?,0)",(cur.lastrowid,sym,d.get("category","social"),float(val),.8,key,stamp))
                c.commit()
                if path in ("/api/ingest","/api/bars"):
                    changed_symbols=impacts if path=="/api/ingest" else [sym]
                    for instrument in changed_symbols:
                        for h in HORIZONS:store(c,calculate(c,instrument,h))
            self.sendjson({"ok":True},201)
        except (ValueError,KeyError,TypeError,sqlite3.Error) as e:self.sendjson({"error":str(e)},400)
def main():
    with closing(connect()) as c:seed(c)
    print(f"DATA MODE: {DATA_MODE.upper()} (separate database: {DB})",flush=True)
    host=os.environ.get("HOST","127.0.0.1");port=int(os.environ.get("PORT","8765"))
    print(f"Trading Dashboard research demo: http://{host}:{port}",flush=True)
    ThreadingHTTPServer((host,port),Handler).serve_forever()
if __name__=="__main__":main()
