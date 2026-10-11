'use strict';
const $=id=>document.getElementById(id);
const e=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const state={symbol:'EURUSD',horizon:'short',page:'overview',data:null};
const fmt=n=>n==null?'—':Number(n).toLocaleString('en-US',{maximumFractionDigits:5});
const cls=s=>/sell|bear/i.test(s)?'sell':/buy|bull/i.test(s)?'buy':'neutral';
const sourceLink=u=>typeof u==='string'&&/^https:\/\/[^\s"'<>]+$/i.test(u)?'<a href="'+e(u)+'" target="_blank" rel="noopener noreferrer">Read original ↗</a>':'';
const tm=s=>new Date(s).toLocaleString('en-GB',{timeZone:'UTC',month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'})+' UTC';
const request=async(url,opt)=>{const r=await fetch(url,opt),v=await r.json();if(!r.ok)throw Error(v.error||'Server error');return v};
function toast(msg){$('toast').textContent=msg;$('toast').classList.add('show');setTimeout(()=>$('toast').classList.remove('show'),3200)}
function graph(vals,col='#2ce0ac'){if(vals.length<2)return '<p class="note">History unavailable.</p>';
 let min=Math.min(...vals),max=Math.max(...vals);if(max===min)max=min+1;
 const pts=vals.map((v,i)=>[20+i*650/(vals.length-1),185-160*(v-min)/(max-min)]);
 const p=pts.map(x=>x.join(',')).join(' ');return '<svg class="graph" preserveAspectRatio="none" viewBox="0 0 690 210" aria-label="historical graph"><line x1="20" x2="670" y1="105" y2="105" stroke="#2b3e52" stroke-dasharray="4 6"/><polyline points="'+p+'" fill="none" stroke="'+col+'" stroke-width="3" stroke-linejoin="round"/><circle cx="'+pts.at(-1)[0]+'" cy="'+pts.at(-1)[1]+'" r="5" fill="'+col+'"/></svg>'}
function factors(data){return Object.entries(data).sort((a,b)=>Math.abs(b[1])-Math.abs(a[1])).map(([k,v])=>'<div class="factor"><header><span>'+e(k.toUpperCase())+'</span><b class="'+(v>=0?'buy':'sell')+'">'+(v>0?'+':'')+v.toFixed(1)+' pts</b></header><i><span class="'+(v<0?'neg':'')+'" style="width:'+Math.min(100,Math.abs(v)*3)+'%"></span></i></div>').join('')}
function meter(s){
 $('score').textContent=s.score==null?'—':s.score;$('category').textContent=s.category.toUpperCase();
 const tone=cls(s.category),col=tone==='buy'?'#2ce0ac':tone==='sell'?'#f16a7b':'#9eacbe';
 $('category').setAttribute('fill',col);$('shine').setAttribute('stroke',col);
 $('needle').setAttribute('transform','rotate('+((s.score==null?50:s.score)*1.8-90)+' 180 167)');
 $('meterNote').textContent=s.evidence_count+' independent events · '+s.status;
 $('drivers').innerHTML=factors(s.drivers);$('researchDrivers').innerHTML=factors(s.drivers);
 document.querySelectorAll('[data-h]').forEach(b=>b.classList.toggle('active',b.dataset.h===state.horizon));
}
function overview(d){
 let s=d.signal,px=d.prices[d.symbol],last=px.at(-1),prev=px.at(-2)||last,delta=Number.isFinite(last)&&Number.isFinite(prev)?(last/prev-1)*100:null;
 $('quote').textContent=fmt(last);$('quoteChange').textContent=delta==null?'NO QUOTE':(delta>=0?'+':'')+delta.toFixed(2)+'%';
 $('quoteChange').className=delta!=null&&delta>=0?'positive':'neutral';$('symbol').value=d.symbol;
 const live=!d.mode.startsWith('SYNTHETIC');
 $('modeBanner').innerHTML=live?'<b>AUTHORIZED-DATA MODE</b> No data provider is connected automatically. TradeMeter remains unavailable until enough authorized evidence and price history exist.':'<b>DEMO DATA</b> All prices, events and TradeMeter scores are synthetic and unvalidated. Not trading signals.';
 $('newIdea').disabled=live;$('newIdea').title=live?'Requires user authentication (not yet implemented)':'';
 document.querySelectorAll('[data-goto="createIdea"],[data-goto="createAlert"]').forEach(b=>{b.disabled=live;b.title=live?'User authentication is required for personal data':''});
 $('chartTag').textContent=live?'STORED AUTHORIZED CLOSES':'SYNTHETIC DAILY';
 $('chartNote').textContent=live?'Last 45 stored closes · availability depends on imported provider data':'Last 45 stored closes · simulated prices';
 $('riskRadar').hidden=live;
 meter(s);$('horizonRows').innerHTML=Object.values(d.signals).map(x=>'<div class="horizon-row"><div><h3>'+e(x.label.toUpperCase())+'</h3><p>Expected relevance: <strong>'+e(x.duration)+'</strong></p></div><b class="'+cls(x.direction)+'">● '+e(x.direction.toUpperCase())+'</b></div>').join('');
 $('chartPrice').textContent=fmt(last);$('chart').innerHTML=graph(px,delta==null||delta>=0?'#2ce0ac':'#f16a7b');
 $('levelHorizon').textContent=s.label.toUpperCase();$('levels').innerHTML='<div class="level"><span>Resistance</span><b class="sell">'+fmt(s.resistance)+'</b></div><div class="level"><span>Current price</span><b>'+fmt(last)+'</b></div><div class="level"><span>Support</span><b class="buy">'+fmt(s.support)+'</b></div>';
 $('invalidation').textContent=s.invalidation;
 const news=x=>'<div class="news-row"><div><h3>'+e(x.title)+'</h3><p>'+e(x.source)+' · '+tm(x.ts)+' · '+(x.demo?'synthetic':'authorized metadata')+'</p></div>'+sourceLink(x.url)+'</div>';
 $('news').innerHTML=d.feed.slice(0,3).map(news).join('');
 $('newsAll').innerHTML=d.feed.map(x=>'<div class="news-row"><div><h3>'+e(x.title)+'</h3><p>'+e(x.body)+'</p><p>'+e(x.kind)+' · '+tm(x.ts)+' · '+e(x.rights)+'</p></div>'+sourceLink(x.url)+'</div>').join('')||'<p class="note">No authorized source records imported yet.</p>';
 $('marketRows').innerHTML=d.instruments.map(x=>{let v=d.prices[x],a=v.at(-1),b=v.at(-2)||a,pct=Number.isFinite(a)&&Number.isFinite(b)?(a/b-1)*100:null;return '<div class="market-row"><strong>'+e(x)+'</strong><span>'+fmt(a)+'</span><b class="'+(pct==null?'neutral':pct>=0?'buy':'sell')+'">'+(pct==null?'NO QUOTE':(pct>=0?'+':'')+pct.toFixed(2)+'%')+'</b><button data-symbol="'+e(x)+'">Analyze ↗</button></div>'}).join('');
 $('history').innerHTML=graph(d.history.map(r=>r.score).filter(v=>v!=null),'#91a7ff');
 const study=d.study[state.horizon];
 const detail=study.sufficient
  ?'<div class="study-metrics"><div><small>COMPLETED EVENTS</small><strong>'+study.count+'</strong></div><div><small>MEDIAN RETURN</small><strong class="'+(study.median_return_pct>=0?'buy':'sell')+'">'+study.median_return_pct+'%</strong></div><div><small>POSITIVE OUTCOMES</small><strong>'+(study.positive_fraction*100).toFixed(1)+'%</strong></div><div><small>MIDDLE 50% RANGE</small><strong>'+study.p25_return_pct+'% to '+study.p75_return_pct+'%</strong></div></div>'
  :'<p class="note">Insufficient comparable completed outcomes ('+study.count+' found; minimum '+study.min_sample+'). Do not infer a bias from this study.</p>';
 $('study').innerHTML='<p class="note">'+e(study.status)+' · '+study.observations_forward+' subsequent stored daily closes · '+e(d.symbol)+'</p>'+detail;
 $('ideaRows').innerHTML=d.ideas.map(x=>'<div class="idea-row"><div><h3>'+e(x.title)+' · '+e(x.symbol)+'</h3><p>'+e(x.thesis)+'</p><p>'+e(x.horizon)+' / '+e(x.direction)+' · '+tm(x.ts)+' · entry '+fmt(x.entry)+' · stop '+fmt(x.stop)+' · target '+fmt(x.target)+'</p></div></div>').join('')||'<p class="note">No trade ideas recorded. Create one to preserve your hypothesis.</p>';
 $('alertRows').innerHTML=d.alerts.map(x=>'<div class="alert-row"><strong>'+e(x.symbol)+' '+e(x.comparison)+' '+fmt(x.price)+'</strong><span class="note">Rule stored, not actively monitored</span></div>').join('')||'<p class="note">No alert rules saved.</p>';
}
async function load(){try{let d=await request('/api/dashboard?symbol='+encodeURIComponent(state.symbol)+'&horizon='+encodeURIComponent(state.horizon));state.data=d;
 if(!$('symbol').options.length)$('symbol').innerHTML=d.instruments.map(x=>'<option>'+e(x)+'</option>').join('');
 overview(d)}catch(err){toast(err.message);console.error(err)}}
const titles={overview:['Overview','Market overview'],markets:['Markets','Market universe'],intelligence:['Intelligence','Market intelligence'],research:['Research Lab','Statistical research'],ideas:['Trade Ideas','Trade idea notebook'],alerts:['Price Alerts','Saved alert rules']};
function navigate(page){if(!titles[page])return;state.page=page;document.querySelectorAll('[data-page]').forEach(x=>x.hidden=x.dataset.page!==page);document.querySelectorAll('.nav').forEach(x=>x.classList.toggle('active',x.dataset.view===page));$('crumb').textContent=titles[page][0];$('pageTitle').innerHTML=e(titles[page][1])+'<span>.</span>'}
let type='ideas';
function modal(kind){type=kind;const select='<label>Instrument<select name="symbol">'+state.data.instruments.map(x=>'<option '+(x===state.symbol?'selected':'')+'>'+e(x)+'</option>').join('')+'</select></label>';
 $('modalTitle').textContent=kind==='ideas'?'New trade idea':'New price alert';
 $('fields').innerHTML=kind==='ideas'?select+'<label>Horizon<select name="horizon"><option value="short">Short-term</option><option value="mid">Mid-term</option><option value="long">Long-term</option></select></label><label>Direction<select name="direction"><option>Buy</option><option>Sell</option><option>Neutral</option></select></label><label>Title<input required maxlength="100" name="title"></label><label>Thesis<textarea name="thesis" maxlength="2000" required></textarea></label><label>Entry<input type="number" step="any" name="entry"></label><label>Invalidation / stop<input type="number" step="any" name="stop"></label><label>Level / target<input type="number" step="any" name="target"></label>':select+'<label>Threshold<select name="comparison"><option>above</option><option>below</option></select></label><label>Price<input type="number" step="any" required min="0.000001" name="price"></label>';
 $('modal').showModal()}
document.addEventListener('click',async ev=>{const b=ev.target.closest('button');if(!b)return;
 if(b.dataset.view)navigate(b.dataset.view);
 if(b.dataset.h){state.horizon=b.dataset.h;await load()}
 if(b.dataset.symbol){state.symbol=b.dataset.symbol;await load();navigate('overview')}
 if(b.dataset.goto){if(b.dataset.goto==='createIdea')modal('ideas');else if(b.dataset.goto==='createAlert')modal('alerts');else navigate(b.dataset.goto)}
});
$('symbol').addEventListener('change',ev=>{state.symbol=ev.target.value;load()});
$('refresh').addEventListener('click',load);
$('newIdea').addEventListener('click',()=>modal('ideas'));
$('expand').addEventListener('click',()=>{$('drivers').hidden=!$('drivers').hidden});
$('close').addEventListener('click',()=>$('modal').close());$('cancel').addEventListener('click',()=>$('modal').close());
$('modalForm').addEventListener('submit',async ev=>{ev.preventDefault();const v=Object.fromEntries(new FormData(ev.currentTarget));for(const k of ['entry','stop','target','price'])if(v[k]==='')v[k]=null;
 try{await request('/api/'+type,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(v)});$('modal').close();await load();navigate(type);toast(type==='ideas'?'Trade idea saved':'Alert rule saved (not actively monitored)')}catch(err){toast(err.message)}});
setInterval(()=>{$('clock').textContent=new Date().toLocaleTimeString('en-GB',{hour:'2-digit',minute:'2-digit',timeZone:'UTC'})+' UTC'},30000);
load();