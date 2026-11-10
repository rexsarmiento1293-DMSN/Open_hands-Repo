# -*- coding: utf-8 -*-
"""MCSN AppFactory - BATCH 2: Negosyo Toolkit.

15 standalone offline HTML apps para sa maliliit na negosyo (business tools).
Light/clean theme, mobile-first, vanilla JS (localStorage), PWA-installable.
Ginagawa sa apps-v2/ para hindi haluin ang unang 36 apps.
"""
import os, json, re, shutil, zipfile, math
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "apps-v2")
APPS = []

BATCH = "Negosyo"

LIGHT_CSS = r"""
:root{
  --bg:#f4f7fb;--card:#ffffff;--card2:#eef3fb;--line:#dbe4f0;
  --txt:#12203a;--mut:#6b7a93;--pri:#0b6cf0;--pri2:#3b8bff;
  --ok:#0aa06e;--warn:#e08a00;--bad:#e0435f;--radius:16px;
  --shadow:0 6px 20px rgba(18,32,58,.08);
}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;
  background:linear-gradient(180deg,#eaf1fb 0%,var(--bg) 40%);color:var(--txt);min-height:100vh}
.wrap{max-width:520px;margin:0 auto;padding:14px 14px 96px}
header.app{display:flex;align-items:center;gap:10px;padding:6px 2px 14px}
header.app .logo{width:42px;height:42px;border-radius:13px;flex:0 0 auto;
  background:linear-gradient(135deg,var(--pri),var(--pri2));display:flex;align-items:center;
  justify-content:center;font-size:22px;box-shadow:0 8px 22px rgba(11,108,240,.28)}
header.app h1{font-size:16px;margin:0;line-height:1.2}
header.app .tag{font-size:11px;color:var(--mut);margin-top:2px}
h2{font-size:19px;margin:2px 0 12px}
h3{font-size:12px;margin:18px 0 8px;color:var(--mut);text-transform:uppercase;letter-spacing:.08em}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);
  padding:15px;margin-bottom:12px;box-shadow:var(--shadow)}
.card.tight{padding:12px}
.mut{color:var(--mut)}
.small{font-size:12px}
.center{text-align:center}
.field{margin-bottom:12px}
.field label{display:block;font-size:12px;color:var(--mut);margin-bottom:6px}
.field input,.field select,.field textarea{width:100%;padding:13px 14px;border-radius:12px;
  border:1px solid var(--line);background:var(--card2);color:var(--txt);font-size:16px;outline:none}
.field input:focus,.field select:focus{border-color:var(--pri2);background:#fff}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;width:100%;
  padding:14px 16px;border-radius:13px;border:0;background:linear-gradient(135deg,var(--pri),var(--pri2));
  color:#fff;font-size:16px;font-weight:600;cursor:pointer;margin-top:4px;box-shadow:0 6px 16px rgba(11,108,240,.25)}
.btn.ghost{background:var(--card2);border:1px solid var(--line);color:var(--txt);font-weight:500;box-shadow:none}
.btn.ok{background:linear-gradient(135deg,#089367,#0aa06e);color:#fff}
.btn.warn{background:linear-gradient(135deg,#c67c00,#e08a00);color:#fff}
.btn.bad{background:linear-gradient(135deg,#c8304b,#e0435f);color:#fff}
.btn.sm{padding:10px 12px;font-size:14px;width:auto}
.row{display:flex;gap:10px}
.row>*{flex:1}
.item{display:flex;align-items:center;gap:12px;padding:12px;border-radius:13px;
  background:var(--card);border:1px solid var(--line);margin-bottom:9px}
.item .ic{width:38px;height:38px;flex:0 0 auto;border-radius:11px;background:var(--card2);
  display:flex;align-items:center;justify-content:center;font-size:19px}
.item .grow{flex:1;min-width:0}
.item .t{font-weight:600;font-size:14px}
.item .s{font-size:12px;color:var(--mut);margin-top:2px;overflow:hidden;text-overflow:ellipsis}
.pill{display:inline-block;padding:4px 10px;border-radius:999px;font-size:11px;font-weight:700}
.pill.ok{background:rgba(10,160,110,.14);color:var(--ok)}
.pill.warn{background:rgba(224,138,0,.14);color:var(--warn)}
.pill.bad{background:rgba(224,67,95,.14);color:var(--bad)}
.pill.pri{background:rgba(11,108,240,.12);color:var(--pri)}
.kv{display:flex;justify-content:space-between;padding:9px 0;border-bottom:1px dashed var(--line);font-size:14px}
.kv:last-child{border-bottom:0}
.kv b{font-weight:700}
.big{font-size:30px;font-weight:800;letter-spacing:-.5px}
.hero{background:linear-gradient(135deg,rgba(11,108,240,.12),rgba(59,139,255,.04));
  border:1px solid var(--line);border-radius:18px;padding:18px;margin-bottom:12px}
.bar{height:12px;border-radius:999px;background:var(--card2);overflow:hidden;border:1px solid var(--line)}
.bar>i{display:block;height:100%;background:linear-gradient(90deg,var(--pri),var(--ok))}
.chips{display:flex;flex-wrap:wrap;gap:8px}
.chip{padding:9px 13px;border-radius:999px;background:var(--card);border:1px solid var(--line);
  font-size:13px;cursor:pointer}
.chip.on{background:linear-gradient(135deg,var(--pri),var(--pri2));border-color:transparent;color:#fff}
.chk{display:flex;align-items:center;gap:11px;padding:12px;border-radius:13px;background:var(--card);
  border:1px solid var(--line);margin-bottom:9px;cursor:pointer}
.chk .box{width:24px;height:24px;border-radius:7px;border:2px solid var(--line);flex:0 0 auto;
  display:flex;align-items:center;justify-content:center;font-size:15px}
.chk.on .box{background:var(--ok);border-color:var(--ok);color:#fff}
.chk.on .t{text-decoration:line-through;color:var(--mut)}
.alert{padding:12px 14px;border-radius:12px;font-size:13px;margin-top:10px}
.alert.err{background:rgba(224,67,95,.10);border:1px solid rgba(224,67,95,.35);color:#a01e33}
.alert.ok{background:rgba(10,160,110,.10);border:1px solid rgba(10,160,110,.3);color:#07724f}
.alert.warn{background:rgba(224,138,0,.10);border:1px solid rgba(224,138,0,.3);color:#8a5500}
.tabs{position:fixed;left:0;right:0;bottom:0;display:flex;background:rgba(255,255,255,.94);
  backdrop-filter:blur(10px);border-top:1px solid var(--line);padding:6px 6px 8px;z-index:20}
.tabs button{flex:1;border:0;background:transparent;color:var(--mut);font-size:11px;font-weight:600;
  padding:8px 2px;border-radius:12px;cursor:pointer;display:flex;flex-direction:column;align-items:center;gap:3px}
.tabs button .e{font-size:19px;line-height:1}
.tabs button.on{color:var(--pri);background:rgba(11,108,240,.10)}
.toast{position:fixed;left:50%;bottom:86px;transform:translateX(-50%) translateY(20px);opacity:0;
  background:#12203a;color:#fff;padding:11px 16px;border-radius:999px;
  font-size:13px;transition:.25s;z-index:40;pointer-events:none;max-width:88vw;text-align:center}
.toast.on{opacity:1;transform:translateX(-50%) translateY(0)}
.foot{text-align:center;color:var(--mut);font-size:11px;margin-top:18px;line-height:1.7}
.screen[hidden]{display:none}
"""

RUNTIME_JS = r"""
const $=(s,r=document)=>r.querySelector(s);
const $$=(s,r=document)=>Array.from(r.querySelectorAll(s));
function money(n){n=Number(n||0);return '\u20B1'+n.toLocaleString('en-PH',{minimumFractionDigits:2,maximumFractionDigits:2});}
function show(name){
  $$('.screen').forEach(s=>{s.hidden=(s.dataset.screen!==name);});
  $$('.tabs button').forEach(b=>b.classList.toggle('on',b.dataset.go===name));
  try{window.scrollTo(0,0);}catch(e){}
}
function toast(m){var t=$('.toast');if(!t)return;t.textContent=m;t.classList.add('on');
  clearTimeout(window.__tt);window.__tt=setTimeout(()=>t.classList.remove('on'),1900);}
function val(id){var e=document.getElementById(id);return e?e.value.trim():'';}
function num(id){var v=parseFloat(val(id));return isNaN(v)?NaN:v;}
const Store={
  get(k,d){try{var v=localStorage.getItem(k);return v==null?d:JSON.parse(v);}catch(e){return d;}},
  set(k,v){try{localStorage.setItem(k,JSON.stringify(v));}catch(e){}}
};
function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
document.addEventListener('click',function(e){
  var b=e.target.closest('[data-go]');if(!b)return;
  if(b.dataset.go==='__back'){history.length>1?history.back():show('home');return;}
  show(b.dataset.go);
});
function resetForm(ids){ids.forEach(function(id){var e=document.getElementById(id);if(e)e.value='';});}
"""


def define(**kw):
    APPS.append(kw)


# ---------------- APP 1: Profit Margin Calculator ----------------
define(name="Profit Margin Calculator", icon="\U0001F4C8", tag="Cost + Presyo -> Tubo %",
home=r"""
<div class="hero"><div class="mut small">Huling Tubo</div><div class="big" id="pmBig">&mdash;</div><div class="mut small" id="pmSub">Kalkulahin ang margin</div></div>
<button class="btn" data-go="input">\U0001F4C8 Compute Margin</button>
<h3>Kasaysayan</h3><div id="pmList"></div>
""",
input=r"""
<div class="card">
 <div class="field"><label>Puhunan / Cost (PHP)</label><input id="pmCost" type="number" inputmode="decimal" placeholder="Hal: 50"></div>
 <div class="field"><label>Presyo / Selling Price (PHP)</label><input id="pmPrice" type="number" inputmode="decimal" placeholder="Hal: 80"></div>
 <div class="field"><label>Dami / Qty</label><input id="pmQty" type="number" inputmode="numeric" placeholder="1" value="1"></div>
 <button class="btn" onclick="pmCalc()">Kalkulahin</button>
 <div id="pmErr"></div>
</div>
""",
result=r"""
<div class="card">
 <div class="kv"><span>Presyo bawat isa</span><b id="pmRPrice">&mdash;</b></div>
 <div class="kv"><span>Puhunan bawat isa</span><b id="pmRCost">&mdash;</b></div>
 <div class="kv"><span>Tubo bawat isa</span><b id="pmRProfit">&mdash;</b></div>
 <div class="kv"><span>Margin</span><b><span class="pill pri" id="pmRMargin">&mdash;</span></b></div>
 <div class="kv"><span>Markup</span><b id="pmRMarkup">&mdash;</b></div>
 <div class="kv"><span>Kabuuang Tubo</span><b id="pmRTotal">&mdash;</b></div>
 <button class="btn ok" onclick="pmSave()">\U0001F4BE I-save</button>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F4C8</div>
 <h2>Naka-save</h2>
 <div class="kv"><span>Tubo</span><b id="pmDProfit">&mdash;</b></div>
 <div class="kv"><span>Margin</span><b id="pmDMargin">&mdash;</b></div>
 <button class="btn ghost" onclick="pmNew()">\u2795 Bagong Compute</button>
</div>
""",
js=r"""
var PM_KEY='mcsn2_pm';var pmData=Store.get(PM_KEY,[]);var pmCur=null;
function pmRender(){
  var el=$('#pmList');
  if(!pmData.length){el.innerHTML='<div class="mut small">Wala pang record.</div>';return;}
  var tot=pmData.reduce(function(a,b){return a+b.total;},0);
  el.innerHTML=pmData.slice().reverse().map(function(r){
    return '<div class="item"><div class="ic">\U0001F4C8</div><div class="grow"><div class="t">'+money(r.price)+' bawat isa</div><div class="s">Tubo '+money(r.profit)+' \u2022 Margin '+r.margin+'%</div></div></div>';
  }).join('')+'<div class="card tight mut small">Kabuuang tubo: <b>'+money(tot)+'</b></div>';
}
function pmCalc(){
  var cost=num('pmCost'),price=num('pmPrice'),qty=num('pmQty')||1;
  if(isNaN(cost)||isNaN(price)){$('#pmErr').innerHTML='<div class="alert err">Ilagay ang cost at presyo.</div>';return;}
  if(price<cost){$('#pmErr').innerHTML='<div class="alert warn">Babala: lugi ka dito (presyo < puhunan).</div>';}
  else{$('#pmErr').innerHTML='';}
  var profit=price-cost;var margin=price>0?(profit/price*100):0;var markup=cost>0?(profit/cost*100):0;
  pmCur={cost:cost,price:price,qty:qty,profit:profit,margin:margin.toFixed(1),markup:markup.toFixed(1),total:profit*qty};
  $('#pmRPrice').textContent=money(price);$('#pmRCost').textContent=money(cost);
  $('#pmRProfit').textContent=money(profit);
  var m=$('#pmRMargin');m.textContent=pmCur.margin+'%';
  m.className='pill '+(margin>=30?'ok':margin>=15?'warn':'bad');
  $('#pmRMarkup').textContent=pmCur.markup+'%';
  $('#pmRTotal').textContent=money(pmCur.total);
  show('result');
}
function pmSave(){if(!pmCur)return;pmData.push(pmCur);Store.set(PM_KEY,pmData);pmRender();
  $('#pmDProfit').textContent=money(pmCur.total);$('#pmDMargin').textContent=pmCur.margin+'%';
  toast('Naka-save');show('done');}
function pmNew(){resetForm(['pmCost','pmPrice','pmQty']);$('#pmErr').innerHTML='';show('input');}
pmRender();
""")

# ---------------- APP 2: Service Quote Builder ----------------
define(name="Service Quote Builder", icon="\U0001F4C4", tag="Items -> Quote Total",
home=r"""
<div class="hero"><div class="mut small">Huling Quote</div><div class="big" id="sqBig">\u20B10.00</div><div class="mut small" id="sqSub">Gumawa ng quote para sa customer</div></div>
<button class="btn" data-go="input">\U0001F4C4 Bagong Quote</button>
<h3>Mga Quote</h3><div id="sqList"></div>
""",
input=r"""
<div class="card">
 <div class="field"><label>Pangalan ng Customer</label><input id="sqCust" placeholder="Hal: Aling Nena"></div>
 <div class="field"><label>Serbisyo</label><input id="sqSvc" placeholder="Hal: Pag-repair ng bubong"></div>
 <div class="row">
  <div class="field"><label>Dami</label><input id="sqQty" type="number" inputmode="numeric" placeholder="1"></div>
  <div class="field"><label>Presyo bawat isa</label><input id="sqRate" type="number" inputmode="decimal" placeholder="500"></div>
 </div>
 <div class="field"><label>Diskwento (%)</label><input id="sqDisc" type="number" inputmode="decimal" placeholder="0" value="0"></div>
 <button class="btn" onclick="sqCalc()">Gumawa ng Quote</button>
 <div id="sqErr"></div>
</div>
""",
result=r"""
<div class="card">
 <div class="kv"><span>Customer</span><b id="sqRCust">&mdash;</b></div>
 <div class="kv"><span>Serbisyo</span><b id="sqRSvc">&mdash;</b></div>
 <div class="kv"><span>Subtotal</span><b id="sqRSub">&mdash;</b></div>
 <div class="kv"><span>Diskwento</span><b id="sqRDisc">&mdash;</b></div>
 <div class="kv"><span>Kabuuan</span><b id="sqRTotal">&mdash;</b></div>
 <div class="mut small" id="sqRNo" style="margin-top:8px">&mdash;</div>
 <button class="btn ok" onclick="sqSave()">\U0001F4BE I-save ang Quote</button>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F4C4</div>
 <h2>Quote Saved</h2>
 <div class="kv"><span>Customer</span><b id="sqDCust">&mdash;</b></div>
 <div class="kv"><span>Kabuuan</span><b id="sqDTotal">&mdash;</b></div>
 <button class="btn ghost" onclick="sqNew()">\u2795 Bagong Quote</button>
</div>
""",
js=r"""
var SQ_KEY='mcsn2_sq';var sqData=Store.get(SQ_KEY,[]);var sqCur=null;
function sqRender(){
  var el=$('#sqList');
  if(!sqData.length){el.innerHTML='<div class="mut small">Wala pang quote.</div>';return;}
  el.innerHTML=sqData.slice().reverse().map(function(q){
    return '<div class="item"><div class="ic">\U0001F4C4</div><div class="grow"><div class="t">'+esc(q.cust)+'</div><div class="s">'+esc(q.svc)+' \u2022 '+money(q.total)+'</div></div></div>';
  }).join('');
}
function sqCalc(){
  var cust=val('sqCust'),svc=val('sqSvc'),qty=num('sqQty')||1,rate=num('sqRate'),disc=num('sqDisc')||0;
  if(!cust||isNaN(rate)){$('#sqErr').innerHTML='<div class="alert err">Ilagay customer at presyo.</div>';return;}
  var sub=qty*rate;var d=sub*disc/100;var total=sub-d;
  sqCur={cust:cust,svc:svc,qty:qty,rate:rate,disc:disc,sub:sub,total:total,no:'QT-'+Date.now().toString().slice(-6)};
  $('#sqRCust').textContent=cust;$('#sqRSvc').textContent=svc||'\u2014';
  $('#sqRSub').textContent=money(sub);$('#sqRDisc').textContent='-'+money(d);
  $('#sqRTotal').textContent=money(total);$('#sqRNo').textContent='Quote No: '+sqCur.no;
  $('#sqBig').textContent=money(total);$('#sqSub').textContent=cust;
  show('result');
}
function sqSave(){if(!sqCur)return;sqData.push(sqCur);Store.set(SQ_KEY,sqData);sqRender();
  $('#sqDCust').textContent=sqCur.cust;$('#sqDTotal').textContent=money(sqCur.total);
  toast('Quote saved');show('done');}
function sqNew(){resetForm(['sqCust','sqSvc','sqQty','sqRate','sqDisc']);$('#sqErr').innerHTML='';show('input');}
sqRender();
""")

# ---------------- APP 3: Payroll & Attendance ----------------
define(name="Payroll & Attendance", icon="\U0001F9FE", tag="Araw + Rate -> Sahod",
home=r"""
<div class="hero"><div class="mut small">Huling Sahod</div><div class="big" id="prBig">\u20B10.00</div><div class="mut small" id="prSub">Compute ng sahod</div></div>
<button class="btn" data-go="input">\U0001F9FE Compute Sahod</button>
<h3>Mga Payroll</h3><div id="prList"></div>
""",
input=r"""
<div class="card">
 <div class="field"><label>Pangalan ng Empleyado</label><input id="prName" placeholder="Hal: Mang Tonyo"></div>
 <div class="field"><label>Daily Rate (PHP)</label><input id="prRate" type="number" inputmode="decimal" placeholder="Hal: 610"></div>
 <div class="row">
  <div class="field"><label>Araw na Trabaho</label><input id="prDays" type="number" inputmode="decimal" placeholder="Hal: 22"></div>
  <div class="field"><label>Overtime (oras)</label><input id="prOt" type="number" inputmode="decimal" placeholder="0" value="0"></div>
 </div>
 <div class="field"><label>Bawas / Cash Advance (PHP)</label><input id="prCa" type="number" inputmode="decimal" placeholder="0" value="0"></div>
 <button class="btn" onclick="prCalc()">Kalkulahin</button>
 <div id="prErr"></div>
</div>
""",
result=r"""
<div class="card">
 <div class="kv"><span>Empleyado</span><b id="prRName">&mdash;</b></div>
 <div class="kv"><span>Basic Pay</span><b id="prRBasic">&mdash;</b></div>
 <div class="kv"><span>Overtime Pay</span><b id="prROt">&mdash;</b></div>
 <div class="kv"><span>Gross Pay</span><b id="prRGross">&mdash;</b></div>
 <div class="kv"><span>Bawas (CA)</span><b id="prRCa">&mdash;</b></div>
 <div class="kv"><span>Net Pay</span><b id="prRNet">&mdash;</b></div>
 <button class="btn ok" onclick="prSave()">\U0001F4BE I-save</button>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F9FE</div>
 <h2>Naka-save</h2>
 <div class="kv"><span>Empleyado</span><b id="prDName">&mdash;</b></div>
 <div class="kv"><span>Net Pay</span><b id="prDNet">&mdash;</b></div>
 <button class="btn ghost" onclick="prNew()">\u2795 Bagong Payroll</button>
</div>
""",
js=r"""
var PR_KEY='mcsn2_pr';var prData=Store.get(PR_KEY,[]);var prCur=null;
function prRender(){
  var el=$('#prList');
  if(!prData.length){el.innerHTML='<div class="mut small">Wala pang payroll.</div>';return;}
  var tot=prData.reduce(function(a,b){return a+b.net;},0);
  el.innerHTML=prData.slice().reverse().map(function(r){
    return '<div class="item"><div class="ic">\U0001F9FE</div><div class="grow"><div class="t">'+esc(r.name)+'</div><div class="s">Net: '+money(r.net)+'</div></div></div>';
  }).join('')+'<div class="card tight mut small">Total payroll: <b>'+money(tot)+'</b></div>';
}
function prCalc(){
  var name=val('prName'),rate=num('prRate'),days=num('prDays'),ot=num('prOt')||0,ca=num('prCa')||0;
  if(!name||isNaN(rate)||isNaN(days)){$('#prErr').innerHTML='<div class="alert err">Kumpletuhin ang pangalan, rate, at araw.</div>';return;}
  $('#prErr').innerHTML='';
  var basic=rate*days;var hourly=rate/8;var otPay=hourly*1.25*ot;var gross=basic+otPay;var net=gross-ca;
  prCur={name:name,rate:rate,days:days,ot:ot,ca:ca,basic:basic,otPay:otPay,gross:gross,net:net};
  $('#prRName').textContent=name;$('#prRBasic').textContent=money(basic);
  $('#prROt').textContent=money(otPay);$('#prRGross').textContent=money(gross);
  $('#prRCa').textContent='-'+money(ca);$('#prRNet').textContent=money(net);
  $('#prBig').textContent=money(net);$('#prSub').textContent=name;
  show('result');
}
function prSave(){if(!prCur)return;prData.push(prCur);Store.set(PR_KEY,prData);prRender();
  $('#prDName').textContent=prCur.name;$('#prDNet').textContent=money(prCur.net);
  toast('Naka-save');show('done');}
function prNew(){resetForm(['prName','prRate','prDays','prOt','prCa']);$('#prErr').innerHTML='';show('input');}
prRender();
""")

# ---------------- APP 4: Inventory Stock Alert ----------------
define(name="Inventory Stock Alert", icon="\U0001F4E6", tag="Stock + Reorder Level",
home=r"""
<div class="hero"><div class="mut small">Mababang Stock</div><div class="big" id="ivBig">0</div><div class="mut small">item ang kailangan i-restock</div></div>
<button class="btn" data-go="input">\U0001F4E6 Magdagdag ng Item</button>
<h3>Listahan ng Stock</h3><div id="ivList"></div>
""",
input=r"""
<div class="card">
 <div class="field"><label>Pangalan ng Item</label><input id="ivName" placeholder="Hal: Coke 1.5L"></div>
 <div class="row">
  <div class="field"><label>Kasalukuyang Stock</label><input id="ivQty" type="number" inputmode="numeric" placeholder="10"></div>
  <div class="field"><label>Reorder Level</label><input id="ivMin" type="number" inputmode="numeric" placeholder="5"></div>
 </div>
 <div class="field"><label>Presyo (PHP)</label><input id="ivPrice" type="number" inputmode="decimal" placeholder="Hal: 65"></div>
 <button class="btn" onclick="ivAdd()">Idagdag</button>
 <div id="ivErr"></div>
</div>
""",
result=r"""
<div class="card">
 <div class="kv"><span>Item</span><b id="ivRName">&mdash;</b></div>
 <div class="kv"><span>Stock</span><b id="ivRQty">&mdash;</b></div>
 <div class="kv"><span>Reorder Level</span><b id="ivRMin">&mdash;</b></div>
 <div class="kv"><span>Halaga ng Stock</span><b id="ivRVal">&mdash;</b></div>
 <div class="kv"><span>Status</span><b><span class="pill" id="ivRStatus">&mdash;</span></b></div>
 <button class="btn ok" onclick="ivSave()">\U0001F4BE I-save</button>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F4E6</div>
 <h2>Naidagdag</h2>
 <div class="mut small" id="ivDMsg">Naka-save sa listahan</div>
 <button class="btn ghost" onclick="ivNew()">\u2795 Bagong Item</button>
</div>
""",
js=r"""
var IV_KEY='mcsn2_iv';var ivData=Store.get(IV_KEY,[]);var ivCur=null;
function ivRender(){
  var el=$('#ivList');var low=0;
  if(!ivData.length){el.innerHTML='<div class="mut small">Wala pang item.</div>';$('#ivBig').textContent='0';return;}
  el.innerHTML=ivData.slice().reverse().map(function(r){
    var isLow=r.qty<=r.min;if(isLow)low++;
    return '<div class="item"><div class="ic">\U0001F4E6</div><div class="grow"><div class="t">'+esc(r.name)+'</div><div class="s">Stock: '+r.qty+' \u2022 Min: '+r.min+' \u2022 '+money(r.price)+'</div></div><span class="pill '+(isLow?'bad':'ok')+'">'+(isLow?'LOW':'OK')+'</span></div>';
  }).join('');
  $('#ivBig').textContent=String(low);
}
function ivAdd(){
  var name=val('ivName'),qty=num('ivQty'),min=num('ivMin'),price=num('ivPrice')||0;
  if(!name||isNaN(qty)||isNaN(min)){$('#ivErr').innerHTML='<div class="alert err">Kumpletuhin ang item, stock, at reorder level.</div>';return;}
  $('#ivErr').innerHTML='';
  var isLow=qty<=min;
  ivCur={name:name,qty:qty,min:min,price:price,low:isLow};
  $('#ivRName').textContent=name;$('#ivRQty').textContent=String(qty);
  $('#ivRMin').textContent=String(min);$('#ivRVal').textContent=money(qty*price);
  var s=$('#ivRStatus');s.textContent=isLow?'KAILANGAN I-RESTOCK':'SAPAT';
  s.className='pill '+(isLow?'bad':'ok');
  show('result');
}
function ivSave(){if(!ivCur)return;ivData.push(ivCur);Store.set(IV_KEY,ivData);ivRender();
  $('#ivDMsg').textContent=ivCur.name+' \u2014 naidagdag';toast('Naidagdag');show('done');}
function ivNew(){resetForm(['ivName','ivQty','ivMin','ivPrice']);$('#ivErr').innerHTML='';show('input');}
ivRender();
""")

# ---------------- APP 5: Customer Loyalty Points ----------------
define(name="Customer Loyalty Points", icon="\U0001F381", tag="Bili -> Puntos",
home=r"""
<div class="hero"><div class="mut small">Kabuuang Puntos</div><div class="big" id="lpBig">0</div><div class="mut small">sa lahat ng customer</div></div>
<button class="btn" data-go="input">\U0001F381 Magbigay ng Puntos</button>
<h3>Mga Customer</h3><div id="lpList"></div>
""",
input=r"""
<div class="card">
 <div class="field"><label>Pangalan ng Customer</label><input id="lpName" placeholder="Hal: Mang Ben"></div>
 <div class="field"><label>Halaga ng Binili (PHP)</label><input id="lpAmt" type="number" inputmode="decimal" placeholder="Hal: 500"></div>
 <div class="field"><label>Puntos kada \u20B1100 (rate)</label><input id="lpRate" type="number" inputmode="decimal" placeholder="1" value="1"></div>
 <button class="btn" onclick="lpCalc()">Kalkulahin</button>
 <div id="lpErr"></div>
</div>
""",
result=r"""
<div class="card">
 <div class="kv"><span>Customer</span><b id="lpRName">&mdash;</b></div>
 <div class="kv"><span>Halaga ng Bili</span><b id="lpRAmt">&mdash;</b></div>
 <div class="kv"><span>Puntos Ngayon</span><b id="lpREarn">&mdash;</b></div>
 <div class="kv"><span>Kabuuang Puntos</span><b id="lpRTotal">&mdash;</b></div>
 <div class="kv"><span>Pwede I-redeem</span><b id="lpRRedeem">&mdash;</b></div>
 <button class="btn ok" onclick="lpSave()">\U0001F4BE I-save</button>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F381</div>
 <h2>Puntos Naidagdag</h2>
 <div class="kv"><span>Customer</span><b id="lpDName">&mdash;</b></div>
 <div class="kv"><span>Total Puntos</span><b id="lpDTotal">&mdash;</b></div>
 <button class="btn ghost" onclick="lpNew()">\u2795 Bagong Bili</button>
</div>
""",
js=r"""
var LP_KEY='mcsn2_lp';var lpData=Store.get(LP_KEY,[]);var lpCur=null;
function lpFind(n){for(var i=0;i<lpData.length;i++){if(lpData[i].name.toLowerCase()===n.toLowerCase())return lpData[i];}return null;}
function lpRender(){
  var el=$('#lpList');var tot=0;
  if(!lpData.length){el.innerHTML='<div class="mut small">Wala pang customer.</div>';$('#lpBig').textContent='0';return;}
  el.innerHTML=lpData.slice().reverse().map(function(c){tot+=c.pts;
    return '<div class="item"><div class="ic">\U0001F381</div><div class="grow"><div class="t">'+esc(c.name)+'</div><div class="s">'+c.pts+' puntos \u2022 halaga '+money(c.pts*1)+'</div></div></div>';
  }).join('');
  $('#lpBig').textContent=String(tot);
}
function lpCalc(){
  var name=val('lpName'),amt=num('lpAmt'),rate=num('lpRate')||1;
  if(!name||isNaN(amt)){$('#lpErr').innerHTML='<div class="alert err">Ilagay customer at halaga.</div>';return;}
  $('#lpErr').innerHTML='';
  var earn=Math.floor(amt/100*rate);var prev=lpFind(name);var total=(prev?prev.pts:0)+earn;
  lpCur={name:name,earn:earn,total:total,amt:amt,prev:prev?prev.pts:0};
  $('#lpRName').textContent=name;$('#lpRAmt').textContent=money(amt);
  $('#lpREarn').textContent='+'+earn;$('#lpRTotal').textContent=String(total);
  $('#lpRRedeem').textContent=money(Math.floor(total/10)*10);
  show('result');
}
function lpSave(){
  if(!lpCur)return;
  var ex=lpFind(lpCur.name);
  if(ex){ex.pts=lpCur.total;}else{lpData.push({name:lpCur.name,pts:lpCur.total});}
  Store.set(LP_KEY,lpData);lpRender();
  $('#lpDName').textContent=lpCur.name;$('#lpDTotal').textContent=String(lpCur.total);
  toast('Puntos naidagdag');show('done');
}
function lpNew(){resetForm(['lpName','lpAmt']);$('#lpErr').innerHTML='';show('input');}
lpRender();
""")

# ---------------- APP 6: Supplier Price Compare ----------------
define(name="Supplier Price Compare", icon="\U0001F91D", tag="Piliin ang pinakamura",
home=r"""
<div class="hero"><div class="mut small">Pinakamurang Supplier</div><div class="big" id="spBig">&mdash;</div><div class="mut small">batay sa unit price</div></div>
<button class="btn" data-go="input">\U0001F91D Maghambing ng Presyo</button>
<h3>Listahan</h3><div id="spList"></div>
""",
input=r"""
<div class="card">
 <div class="field"><label>Produkto</label><input id="spProd" placeholder="Hal: Bigas 25kg"></div>
 <div class="field"><label>Supplier A \u2014 Presyo / Dami</label>
  <div class="row"><input id="spPA" type="number" inputmode="decimal" placeholder="Presyo"><input id="spQA" type="number" inputmode="decimal" placeholder="Dami"></div>
 </div>
 <div class="field"><label>Supplier B \u2014 Presyo / Dami</label>
  <div class="row"><input id="spPB" type="number" inputmode="decimal" placeholder="Presyo"><input id="spQB" type="number" inputmode="decimal" placeholder="Dami"></div>
 </div>
 <button class="btn" onclick="spCalc()">Ihambing</button>
 <div id="spErr"></div>
</div>
""",
result=r"""
<div class="card">
 <div class="kv"><span>Produkto</span><b id="spRProd">&mdash;</b></div>
 <div class="kv"><span>Supplier A (unit)</span><b id="spRA">&mdash;</b></div>
 <div class="kv"><span>Supplier B (unit)</span><b id="spRB">&mdash;</b></div>
 <div class="kv"><span>Pinakamura</span><b><span class="pill ok" id="spRBest">&mdash;</span></b></div>
 <div class="kv"><span>Tipid bawat unit</span><b id="spRSave">&mdash;</b></div>
 <button class="btn ok" onclick="spSave()">\U0001F4BE I-save</button>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F91D</div>
 <h2>Naka-save</h2>
 <div class="mut small" id="spDMsg">Naka-save ang comparison</div>
 <button class="btn ghost" onclick="spNew()">\u2795 Bagong Hambing</button>
</div>
""",
js=r"""
var SP_KEY='mcsn2_sp';var spData=Store.get(SP_KEY,[]);var spCur=null;
function spRender(){
  var el=$('#spList');
  if(!spData.length){el.innerHTML='<div class="mut small">Wala pang comparison.</div>';return;}
  el.innerHTML=spData.slice().reverse().map(function(r){
    return '<div class="item"><div class="ic">\U0001F91D</div><div class="grow"><div class="t">'+esc(r.prod)+'</div><div class="s">'+r.best+' ang mas mura \u2022 tipid '+money(r.save)+'/unit</div></div></div>';
  }).join('');
}
function spCalc(){
  var prod=val('spProd'),pa=num('spPA'),qa=num('spQA'),pb=num('spPB'),qb=num('spQB');
  if(!prod||isNaN(pa)||isNaN(qa)||isNaN(pb)||isNaN(qb)||qa<=0||qb<=0){$('#spErr').innerHTML='<div class="alert err">Kumpletuhin lahat ng field.</div>';return;}
  $('#spErr').innerHTML='';
  var ua=pa/qa,ub=pb/qb;var best=ua<=ub?'Supplier A':'Supplier B';var save=Math.abs(ua-ub);
  spCur={prod:prod,ua:ua,ub:ub,best:best,save:save};
  $('#spRProd').textContent=prod;$('#spRA').textContent=money(ua);$('#spRB').textContent=money(ub);
  $('#spRBest').textContent=best;$('#spRSave').textContent=money(save);
  $('#spBig').textContent=best;
  show('result');
}
function spSave(){if(!spCur)return;spData.push(spCur);Store.set(SP_KEY,spData);spRender();
  $('#spDMsg').textContent=spCur.prod+' \u2014 '+spCur.best;toast('Naka-save');show('done');}
function spNew(){resetForm(['spProd','spPA','spQA','spPB','spQB']);$('#spErr').innerHTML='';show('input');}
spRender();
""")

# ---------------- APP 7: Daily Sales Tracker ----------------
define(name="Daily Sales Tracker", icon="\U0001F4B0", tag="Araw-araw na benta",
home=r"""
<div class="hero"><div class="mut small">Benta Ngayong Buwan</div><div class="big" id="dsBig">\u20B10.00</div><div class="mut small" id="dsSub">0 araw naitala</div></div>
<button class="btn" data-go="input">\U0001F4B0 I-record ang Benta</button>
<h3>Mga Araw</h3><div id="dsList"></div>
""",
input=r"""
<div class="card">
 <div class="field"><label>Petsa</label><input id="dsDate" type="date"></div>
 <div class="field"><label>Kabuuang Benta (PHP)</label><input id="dsAmt" type="number" inputmode="decimal" placeholder="Hal: 3500"></div>
 <div class="field"><label>Puhunan (PHP)</label><input id="dsCost" type="number" inputmode="decimal" placeholder="Hal: 2000"></div>
 <button class="btn" onclick="dsCalc()">I-record</button>
 <div id="dsErr"></div>
</div>
""",
result=r"""
<div class="card">
 <div class="kv"><span>Petsa</span><b id="dsRDate">&mdash;</b></div>
 <div class="kv"><span>Benta</span><b id="dsRAmt">&mdash;</b></div>
 <div class="kv"><span>Puhunan</span><b id="dsRCost">&mdash;</b></div>
 <div class="kv"><span>Tubo</span><b id="dsRProfit">&mdash;</b></div>
 <div class="kv"><span>Margin</span><b><span class="pill" id="dsRMargin">&mdash;</span></b></div>
 <button class="btn ok" onclick="dsSave()">\U0001F4BE I-save</button>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F4B0</div>
 <h2>Naitala</h2>
 <div class="kv"><span>Tubo</span><b id="dsDProfit">&mdash;</b></div>
 <button class="btn ghost" onclick="dsNew()">\u2795 Bagong Araw</button>
</div>
""",
js=r"""
var DS_KEY='mcsn2_ds';var dsData=Store.get(DS_KEY,[]);var dsCur=null;
function dsRender(){
  var el=$('#dsList');
  if(!dsData.length){el.innerHTML='<div class="mut small">Wala pang record.</div>';$('#dsBig').textContent='\u20B10.00';$('#dsSub').textContent='0 araw naitala';return;}
  var tot=dsData.reduce(function(a,b){return a+b.amt;},0);var prof=dsData.reduce(function(a,b){return a+b.profit;},0);
  el.innerHTML=dsData.slice().reverse().map(function(r){
    return '<div class="item"><div class="ic">\U0001F4B0</div><div class="grow"><div class="t">'+r.date+'</div><div class="s">Benta '+money(r.amt)+' \u2022 Tubo '+money(r.profit)+'</div></div></div>';
  }).join('')+'<div class="card tight mut small">Kabuuang tubo: <b>'+money(prof)+'</b></div>';
  $('#dsBig').textContent=money(tot);$('#dsSub').textContent=dsData.length+' araw naitala';
}
function dsCalc(){
  var date=val('dsDate')||new Date().toISOString().slice(0,10);
  var amt=num('dsAmt'),cost=num('dsCost')||0;
  if(isNaN(amt)){$('#dsErr').innerHTML='<div class="alert err">Ilagay ang benta.</div>';return;}
  $('#dsErr').innerHTML='';
  var profit=amt-cost;var margin=amt>0?(profit/amt*100):0;
  dsCur={date:date,amt:amt,cost:cost,profit:profit,margin:margin.toFixed(1)};
  $('#dsRDate').textContent=date;$('#dsRAmt').textContent=money(amt);$('#dsRCost').textContent=money(cost);
  $('#dsRProfit').textContent=money(profit);
  var m=$('#dsRMargin');m.textContent=dsCur.margin+'%';m.className='pill '+(margin>=30?'ok':margin>=10?'warn':'bad');
  show('result');
}
function dsSave(){if(!dsCur)return;dsData.push(dsCur);Store.set(DS_KEY,dsData);dsRender();
  $('#dsDProfit').textContent=money(dsCur.profit);toast('Naitala');show('done');}
function dsNew(){resetForm(['dsDate','dsAmt','dsCost']);$('#dsErr').innerHTML='';show('input');}
dsRender();
""")

# ---------------- APP 8: Break-even Calculator ----------------
define(name="Break-even Calculator", icon="\u2696\uFE0F", tag="Ilang benta bago kumita",
home=r"""
<div class="hero"><div class="mut small">Break-even</div><div class="big" id="beBig">0</div><div class="mut small">units bago kumita</div></div>
<button class="btn" data-go="input">\u2696\uFE0F Kalkulahin</button>
<h3>Paliwanag</h3>
<div class="card tight mut small">Break-even = Fixed Cost \u00F7 (Presyo \u2212 Variable Cost). Pagkabenta mo ng ganitong dami, tabla ka na \u2014 puro tubo na pagkatapos.</div>
""",
input=r"""
<div class="card">
 <div class="field"><label>Fixed Cost (PHP) \u2014 upa, kuryente, atbp.</label><input id="beFixed" type="number" inputmode="decimal" placeholder="Hal: 5000"></div>
 <div class="field"><label>Presyo bawat Unit (PHP)</label><input id="bePrice" type="number" inputmode="decimal" placeholder="Hal: 50"></div>
 <div class="field"><label>Variable Cost bawat Unit (PHP)</label><input id="beVar" type="number" inputmode="decimal" placeholder="Hal: 30"></div>
 <button class="btn" onclick="beCalc()">Kalkulahin</button>
 <div id="beErr"></div>
</div>
""",
result=r"""
<div class="card">
 <div class="kv"><span>Fixed Cost</span><b id="beRFixed">&mdash;</b></div>
 <div class="kv"><span>Contribution / Unit</span><b id="beRContrib">&mdash;</b></div>
 <div class="kv"><span>Break-even Units</span><b id="beRUnits">&mdash;</b></div>
 <div class="kv"><span>Break-even Sales</span><b id="beRSales">&mdash;</b></div>
 <div class="kv"><span>Benta kada araw (est.)</span><b id="beRDay">&mdash;</b></div>
 <div class="mut small" id="beRNote" style="margin-top:8px"></div>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\u2696\uFE0F</div>
 <h2>Kalkulado</h2>
 <div class="mut small" id="beDMsg">Nasa Resulta ang detalye</div>
 <button class="btn ghost" onclick="beNew()">\u2795 Bagong Compute</button>
</div>
""",
js=r"""
function beCalc(){
  var fixed=num('beFixed'),price=num('bePrice'),vc=num('beVar');
  if(isNaN(fixed)||isNaN(price)||isNaN(vc)){$('#beErr').innerHTML='<div class="alert err">Kumpletuhin lahat ng field.</div>';return;}
  var contrib=price-vc;
  if(contrib<=0){$('#beErr').innerHTML='<div class="alert err">Lugi kada unit \u2014 dapat mas mataas ang presyo sa variable cost.</div>';return;}
  $('#beErr').innerHTML='';
  var units=Math.ceil(fixed/contrib);var sales=units*price;
  $('#beRFixed').textContent=money(fixed);$('#beRContrib').textContent=money(contrib);
  $('#beRUnits').textContent=units+' units';$('#beRSales').textContent=money(sales);
  $('#beRDay').textContent=Math.ceil(units/30)+' units/araw';
  $('#beRNote').textContent='Pagkabenta ng '+units+' units (halaga '+money(sales)+'), tabla ka na.';
  $('#beBig').textContent=String(units);
  toast('Kalkulado');show('result');
}
function beNew(){resetForm(['beFixed','bePrice','beVar']);$('#beErr').innerHTML='';show('input');}
""")

# ---------------- APP 9: VAT / Tax Calculator ----------------
define(name="VAT / Tax Calculator", icon="\U0001F9FE", tag="VAT 12% (in/out)",
home=r"""
<div class="hero"><div class="mut small">VAT Rate</div><div class="big">12%</div><div class="mut small">Philippine standard VAT</div></div>
<button class="btn" data-go="input">\U0001F9FE Kalkulahin ang VAT</button>
<h3>Paliwanag</h3>
<div class="card tight mut small">VAT-Exclusive: presyo + VAT. VAT-Inclusive: hinati ang VAT mula sa kabuuang presyo.</div>
""",
input=r"""
<div class="card">
 <div class="field"><label>Halaga (PHP)</label><input id="vtAmt" type="number" inputmode="decimal" placeholder="Hal: 1120"></div>
 <div class="field"><label>VAT Rate (%)</label><input id="vtRate" type="number" inputmode="decimal" placeholder="12" value="12"></div>
 <div class="field"><label>Uri</label>
  <select id="vtType"><option value="excl">VAT-Exclusive (dagdag ang VAT)</option><option value="incl">VAT-Inclusive (kasama na ang VAT)</option></select>
 </div>
 <button class="btn" onclick="vtCalc()">Kalkulahin</button>
 <div id="vtErr"></div>
</div>
""",
result=r"""
<div class="card">
 <div class="kv"><span>Net (walang VAT)</span><b id="vtRNet">&mdash;</b></div>
 <div class="kv"><span>VAT</span><b id="vtRVat">&mdash;</b></div>
 <div class="kv"><span>Gross (may VAT)</span><b id="vtRGross">&mdash;</b></div>
 <div class="kv"><span>Rate</span><b><span class="pill pri" id="vtRRate">&mdash;</span></b></div>
 <div class="mut small" id="vtRNote" style="margin-top:8px"></div>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F9FE</div>
 <h2>Kalkulado</h2>
 <div class="kv"><span>VAT</span><b id="vtDVat">&mdash;</b></div>
 <div class="kv"><span>Gross</span><b id="vtDGross">&mdash;</b></div>
 <button class="btn ghost" onclick="vtNew()">\u2795 Bagong Compute</button>
</div>
""",
js=r"""
function vtCalc(){
  var amt=num('vtAmt'),rate=num('vtRate');var type=val('vtType');
  if(isNaN(amt)||isNaN(rate)){$('#vtErr').innerHTML='<div class="alert err">Ilagay ang halaga at rate.</div>';return;}
  $('#vtErr').innerHTML='';
  var net,vat,gross;
  if(type==='incl'){net=amt/(1+rate/100);vat=amt-net;gross=amt;}
  else{net=amt;vat=amt*rate/100;gross=amt+vat;}
  $('#vtRNet').textContent=money(net);$('#vtRVat').textContent=money(vat);$('#vtRGross').textContent=money(gross);
  $('#vtRRate').textContent=rate+'%';
  $('#vtRNote').textContent=type==='incl'?'VAT-inclusive: hinati ang VAT mula sa '+money(amt):'VAT-exclusive: dinagdag ang VAT sa '+money(amt);
  $('#vtDVat').textContent=money(vat);$('#vtDGross').textContent=money(gross);
  toast('Kalkulado');show('result');
}
function vtNew(){resetForm(['vtAmt','vtRate']);$('#vtErr').innerHTML='';show('input');}
""")

# ---------------- APP 10: Appointment Booking ----------------
define(name="Appointment Booking", icon="\U0001F4C5", tag="Booking list + reminder",
home=r"""
<div class="hero"><div class="mut small">Mga Booking</div><div class="big" id="abBig">0</div><div class="mut small">naka-schedule</div></div>
<button class="btn" data-go="input">\U0001F4C5 Bagong Booking</button>
<h3>Schedule</h3><div id="abList"></div>
""",
input=r"""
<div class="card">
 <div class="field"><label>Pangalan ng Customer</label><input id="abName" placeholder="Hal: Gng. Cruz"></div>
 <div class="field"><label>Serbisyo</label><input id="abSvc" placeholder="Hal: Haircut"></div>
 <div class="row">
  <div class="field"><label>Petsa</label><input id="abDate" type="date"></div>
  <div class="field"><label>Oras</label><input id="abTime" type="time"></div>
 </div>
 <div class="field"><label>Bayad (PHP)</label><input id="abFee" type="number" inputmode="decimal" placeholder="Hal: 150"></div>
 <button class="btn" onclick="abBook()">I-book</button>
 <div id="abErr"></div>
</div>
""",
result=r"""
<div class="card">
 <div class="kv"><span>Customer</span><b id="abRName">&mdash;</b></div>
 <div class="kv"><span>Serbisyo</span><b id="abRSvc">&mdash;</b></div>
 <div class="kv"><span>Petsa at Oras</span><b id="abRWhen">&mdash;</b></div>
 <div class="kv"><span>Bayad</span><b id="abRFee">&mdash;</b></div>
 <div class="kv"><span>Status</span><b><span class="pill pri" id="abRStatus">Booked</span></b></div>
 <button class="btn ok" onclick="abSave()">\U0001F4BE I-save</button>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F4C5</div>
 <h2>Naka-book</h2>
 <div class="kv"><span>Customer</span><b id="abDName">&mdash;</b></div>
 <div class="kv"><span>Kailan</span><b id="abDWhen">&mdash;</b></div>
 <button class="btn ghost" onclick="abNew()">\u2795 Bagong Booking</button>
</div>
""",
js=r"""
var AB_KEY='mcsn2_ab';var abData=Store.get(AB_KEY,[]);var abCur=null;
function abRender(){
  var el=$('#abList');
  if(!abData.length){el.innerHTML='<div class="mut small">Wala pang booking.</div>';$('#abBig').textContent='0';return;}
  var s=abData.slice().sort(function(a,b){return (a.date+a.time)<(b.date+b.time)?-1:1;});
  el.innerHTML=s.map(function(r){
    return '<div class="item"><div class="ic">\U0001F4C5</div><div class="grow"><div class="t">'+esc(r.name)+'</div><div class="s">'+esc(r.svc)+' \u2022 '+r.date+' '+r.time+' \u2022 '+money(r.fee)+'</div></div></div>';
  }).join('');
  $('#abBig').textContent=String(abData.length);
}
function abBook(){
  var name=val('abName'),svc=val('abSvc'),date=val('abDate'),time=val('abTime'),fee=num('abFee')||0;
  if(!name||!date||!time){$('#abErr').innerHTML='<div class="alert err">Ilagay pangalan, petsa, at oras.</div>';return;}
  $('#abErr').innerHTML='';
  abCur={name:name,svc:svc,date:date,time:time,fee:fee};
  $('#abRName').textContent=name;$('#abRSvc').textContent=svc||'\u2014';
  $('#abRWhen').textContent=date+' '+time;$('#abRFee').textContent=money(fee);
  show('result');
}
function abSave(){if(!abCur)return;abData.push(abCur);Store.set(AB_KEY,abData);abRender();
  $('#abDName').textContent=abCur.name;$('#abDWhen').textContent=abCur.date+' '+abCur.time;
  toast('Naka-book');show('done');}
function abNew(){resetForm(['abName','abSvc','abDate','abTime','abFee']);$('#abErr').innerHTML='';show('input');}
abRender();
""")

# ---------------- APP 11: Commission Calculator ----------------
define(name="Commission Calculator", icon="\U0001F4B5", tag="Benta -> Komisyon",
home=r"""
<div class="hero"><div class="mut small">Huling Komisyon</div><div class="big" id="cmBig">\u20B10.00</div><div class="mut small" id="cmSub">Compute ng komisyon</div></div>
<button class="btn" data-go="input">\U0001F4B5 Kalkulahin</button>
<h3>Kasaysayan</h3><div id="cmList"></div>
""",
input=r"""
<div class="card">
 <div class="field"><label>Pangalan ng Ahente</label><input id="cmName" placeholder="Hal: Ana"></div>
 <div class="field"><label>Halaga ng Benta (PHP)</label><input id="cmSales" type="number" inputmode="decimal" placeholder="Hal: 50000"></div>
 <div class="field"><label>Commission Rate (%)</label><input id="cmRate" type="number" inputmode="decimal" placeholder="Hal: 5"></div>
 <div class="field"><label>Bonus (PHP)</label><input id="cmBonus" type="number" inputmode="decimal" placeholder="0" value="0"></div>
 <button class="btn" onclick="cmCalc()">Kalkulahin</button>
 <div id="cmErr"></div>
</div>
""",
result=r"""
<div class="card">
 <div class="kv"><span>Ahente</span><b id="cmRName">&mdash;</b></div>
 <div class="kv"><span>Benta</span><b id="cmRSales">&mdash;</b></div>
 <div class="kv"><span>Komisyon</span><b id="cmRComm">&mdash;</b></div>
 <div class="kv"><span>Bonus</span><b id="cmRBonus">&mdash;</b></div>
 <div class="kv"><span>Kabuuang Kita</span><b id="cmRTotal">&mdash;</b></div>
 <button class="btn ok" onclick="cmSave()">\U0001F4BE I-save</button>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F4B5</div>
 <h2>Naka-save</h2>
 <div class="kv"><span>Ahente</span><b id="cmDName">&mdash;</b></div>
 <div class="kv"><span>Kabuuan</span><b id="cmDTotal">&mdash;</b></div>
 <button class="btn ghost" onclick="cmNew()">\u2795 Bagong Compute</button>
</div>
""",
js=r"""
var CM_KEY='mcsn2_cm';var cmData=Store.get(CM_KEY,[]);var cmCur=null;
function cmRender(){
  var el=$('#cmList');
  if(!cmData.length){el.innerHTML='<div class="mut small">Wala pang record.</div>';return;}
  var tot=cmData.reduce(function(a,b){return a+b.total;},0);
  el.innerHTML=cmData.slice().reverse().map(function(r){
    return '<div class="item"><div class="ic">\U0001F4B5</div><div class="grow"><div class="t">'+esc(r.name)+'</div><div class="s">Komisyon '+money(r.comm)+' \u2022 total '+money(r.total)+'</div></div></div>';
  }).join('')+'<div class="card tight mut small">Kabuuang komisyon: <b>'+money(tot)+'</b></div>';
}
function cmCalc(){
  var name=val('cmName'),sales=num('cmSales'),rate=num('cmRate'),bonus=num('cmBonus')||0;
  if(!name||isNaN(sales)||isNaN(rate)){$('#cmErr').innerHTML='<div class="alert err">Kumpletuhin ang pangalan, benta, at rate.</div>';return;}
  $('#cmErr').innerHTML='';
  var comm=sales*rate/100;var total=comm+bonus;
  cmCur={name:name,sales:sales,rate:rate,comm:comm,bonus:bonus,total:total};
  $('#cmRName').textContent=name;$('#cmRSales').textContent=money(sales);$('#cmRComm').textContent=money(comm);
  $('#cmRBonus').textContent=money(bonus);$('#cmRTotal').textContent=money(total);
  $('#cmBig').textContent=money(total);$('#cmSub').textContent=name;
  show('result');
}
function cmSave(){if(!cmCur)return;cmData.push(cmCur);Store.set(CM_KEY,cmData);cmRender();
  $('#cmDName').textContent=cmCur.name;$('#cmDTotal').textContent=money(cmCur.total);
  toast('Naka-save');show('done');}
function cmNew(){resetForm(['cmName','cmSales','cmRate','cmBonus']);$('#cmErr').innerHTML='';show('input');}
cmRender();
""")

# ---------------- APP 12: Loan Amortization ----------------
define(name="Loan Amortization", icon="\U0001F3E6", tag="Buwanang bayad + schedule",
home=r"""
<div class="hero"><div class="mut small">Buwanang Bayad</div><div class="big" id="laBig">\u20B10.00</div><div class="mut small" id="laSub">loan amortization</div></div>
<button class="btn" data-go="input">\U0001F3E6 Kalkulahin</button>
<h3>Paliwanag</h3>
<div class="card tight mut small">Ipakita ang buwanang hulog, kabuuang bayad, at interes para sa negosyo loan.</div>
""",
input=r"""
<div class="card">
 <div class="field"><label>Halaga ng Utang / Principal (PHP)</label><input id="laP" type="number" inputmode="decimal" placeholder="Hal: 100000"></div>
 <div class="field"><label>Taunang Interes (%)</label><input id="laR" type="number" inputmode="decimal" placeholder="Hal: 12"></div>
 <div class="field"><label>Buwan / Term (months)</label><input id="laN" type="number" inputmode="numeric" placeholder="Hal: 12"></div>
 <button class="btn" onclick="laCalc()">Kalkulahin</button>
 <div id="laErr"></div>
</div>
""",
result=r"""
<div class="card">
 <div class="kv"><span>Principal</span><b id="laRP">&mdash;</b></div>
 <div class="kv"><span>Buwanang Bayad</span><b id="laRMonthly">&mdash;</b></div>
 <div class="kv"><span>Kabuuang Bayad</span><b id="laRTotal">&mdash;</b></div>
 <div class="kv"><span>Kabuuang Interes</span><b id="laRInterest">&mdash;</b></div>
 <div class="mut small" id="laRNote" style="margin-top:8px"></div>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F3E6</div>
 <h2>Kalkulado</h2>
 <div class="kv"><span>Buwanang Bayad</span><b id="laDMonthly">&mdash;</b></div>
 <div class="kv"><span>Kabuuan</span><b id="laDTotal">&mdash;</b></div>
 <button class="btn ghost" onclick="laNew()">\u2795 Bagong Compute</button>
</div>
""",
js=r"""
function laCalc(){
  var P=num('laP'),r=num('laR'),n=num('laN');
  if(isNaN(P)||isNaN(r)||isNaN(n)||n<=0){$('#laErr').innerHTML='<div class="alert err">Kumpletuhin lahat ng field (term > 0).</div>';return;}
  $('#laErr').innerHTML='';
  var i=r/100/12;var monthly;
  if(i===0){monthly=P/n;}
  else{monthly=P*i*Math.pow(1+i,n)/(Math.pow(1+i,n)-1);}
  var total=monthly*n;var interest=total-P;
  $('#laRP').textContent=money(P);$('#laRMonthly').textContent=money(monthly);
  $('#laRTotal').textContent=money(total);$('#laRInterest').textContent=money(interest);
  $('#laRNote').textContent='Sa loob ng '+n+' buwan, ang interes mo ay '+money(interest)+' ('+(interest/P*100).toFixed(1)+'% ng principal).';
  $('#laBig').textContent=money(monthly);$('#laSub').textContent=n+' buwan';
  $('#laDMonthly').textContent=money(monthly);$('#laDTotal').textContent=money(total);
  toast('Kalkulado');show('result');
}
function laNew(){resetForm(['laP','laR','laN']);$('#laErr').innerHTML='';show('input');}
""")

# ---------------- APP 13: Negosyo Expense Tracker ----------------
define(name="Negosyo Expense Tracker", icon="\U0001F4D2", tag="Gastos kada kategorya",
home=r"""
<div class="hero"><div class="mut small">Kabuuang Gastos</div><div class="big" id="exBig">\u20B10.00</div><div class="mut small" id="exSub">0 record</div></div>
<button class="btn" data-go="input">\U0001F4D2 Magdagdag ng Gastos</button>
<h3>Mga Gastos</h3><div id="exList"></div>
""",
input=r"""
<div class="card">
 <div class="field"><label>Paglalarawan</label><input id="exDesc" placeholder="Hal: Kuryente sa tindahan"></div>
 <div class="field"><label>Halaga (PHP)</label><input id="exAmt" type="number" inputmode="decimal" placeholder="Hal: 1200"></div>
 <div class="field"><label>Kategorya</label>
  <select id="exCat"><option>Puhunan</option><option>Upa</option><option>Kuryente/Tubig</option><option>Sweldo</option><option>Transportasyon</option><option>Iba pa</option></select>
 </div>
 <button class="btn" onclick="exAdd()">Idagdag</button>
 <div id="exErr"></div>
</div>
""",
result=r"""
<div class="card">
 <div class="kv"><span>Paglalarawan</span><b id="exRDesc">&mdash;</b></div>
 <div class="kv"><span>Kategorya</span><b id="exRCat">&mdash;</b></div>
 <div class="kv"><span>Halaga</span><b id="exRAmt">&mdash;</b></div>
 <div class="kv"><span>Kabuuang Gastos</span><b id="exRTotal">&mdash;</b></div>
 <button class="btn ok" onclick="exSave()">\U0001F4BE I-save</button>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F4D2</div>
 <h2>Naidagdag</h2>
 <div class="mut small" id="exDMsg">Naka-save</div>
 <button class="btn ghost" onclick="exNew()">\u2795 Bagong Gastos</button>
</div>
""",
js=r"""
var EX_KEY='mcsn2_ex';var exData=Store.get(EX_KEY,[]);var exCur=null;
function exRender(){
  var el=$('#exList');
  if(!exData.length){el.innerHTML='<div class="mut small">Wala pang gastos.</div>';$('#exBig').textContent='\u20B10.00';$('#exSub').textContent='0 record';return;}
  var tot=exData.reduce(function(a,b){return a+b.amt;},0);
  var byCat={};exData.forEach(function(r){byCat[r.cat]=(byCat[r.cat]||0)+r.amt;});
  var breakdown=Object.keys(byCat).map(function(k){return '<div class="kv"><span>'+esc(k)+'</span><b>'+money(byCat[k])+'</b></div>';}).join('');
  el.innerHTML=exData.slice().reverse().map(function(r){
    return '<div class="item"><div class="ic">\U0001F4D2</div><div class="grow"><div class="t">'+esc(r.desc)+'</div><div class="s">'+esc(r.cat)+' \u2022 '+money(r.amt)+'</div></div></div>';
  }).join('')+'<div class="card tight"><h3>Breakdown</h3>'+breakdown+'</div>';
  $('#exBig').textContent=money(tot);$('#exSub').textContent=exData.length+' record';
}
function exAdd(){
  var desc=val('exDesc'),amt=num('exAmt'),cat=val('exCat');
  if(!desc||isNaN(amt)){$('#exErr').innerHTML='<div class="alert err">Ilagay ang paglalarawan at halaga.</div>';return;}
  $('#exErr').innerHTML='';
  exCur={desc:desc,amt:amt,cat:cat};
  var tot=exData.reduce(function(a,b){return a+b.amt;},0)+amt;
  $('#exRDesc').textContent=desc;$('#exRCat').textContent=cat;$('#exRAmt').textContent=money(amt);
  $('#exRTotal').textContent=money(tot);
  show('result');
}
function exSave(){if(!exCur)return;exData.push(exCur);Store.set(EX_KEY,exData);exRender();
  $('#exDMsg').textContent=exCur.desc+' \u2014 '+money(exCur.amt);toast('Naidagdag');show('done');}
function exNew(){resetForm(['exDesc','exAmt']);$('#exErr').innerHTML='';show('input');}
exRender();
""")

# ---------------- APP 14: Discount & Promo Calculator ----------------
define(name="Discount & Promo Calculator", icon="\U0001F3F7\uFE0F", tag="Promo + diskwento",
home=r"""
<div class="hero"><div class="mut small">Final na Presyo</div><div class="big" id="dcBig">\u20B10.00</div><div class="mut small" id="dcSub">may promo at diskwento</div></div>
<button class="btn" data-go="input">\U0001F3F7\uFE0F Kalkulahin</button>
<h3>Tips</h3>
<div class="card tight mut small">Puwede mong pagsamahin ang store discount at promo code para sa final na presyo.</div>
""",
input=r"""
<div class="card">
 <div class="field"><label>Presyo (PHP)</label><input id="dcPrice" type="number" inputmode="decimal" placeholder="Hal: 1000"></div>
 <div class="field"><label>Diskwento ng Tindahan (%)</label><input id="dcStore" type="number" inputmode="decimal" placeholder="Hal: 10" value="0"></div>
 <div class="field"><label>Promo (\u20B1 o %)</label>
  <div class="row">
   <input id="dcPromo" type="number" inputmode="decimal" placeholder="Hal: 50">
   <select id="dcPromoType"><option value="amt">Peso (\u20B1)</option><option value="pct">Porsyento (%)</option></select>
  </div>
 </div>
 <button class="btn" onclick="dcCalc()">Kalkulahin</button>
 <div id="dcErr"></div>
</div>
""",
result=r"""
<div class="card">
 <div class="kv"><span>Orihinal na Presyo</span><b id="dcROrig">&mdash;</b></div>
 <div class="kv"><span>Store Discount</span><b id="dcRStore">&mdash;</b></div>
 <div class="kv"><span>Promo Bawas</span><b id="dcRPromo">&mdash;</b></div>
 <div class="kv"><span>Final na Presyo</span><b id="dcRFinal">&mdash;</b></div>
 <div class="kv"><span>Kabuuang Tipid</span><b><span class="pill ok" id="dcRSave">&mdash;</span></b></div>
 <button class="btn ok" onclick="dcSave()">\U0001F4BE I-save</button>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F3F7\uFE0F</div>
 <h2>Kalkulado</h2>
 <div class="kv"><span>Final</span><b id="dcDFinal">&mdash;</b></div>
 <div class="kv"><span>Tipid</span><b id="dcDSave">&mdash;</b></div>
 <button class="btn ghost" onclick="dcNew()">\u2795 Bagong Compute</button>
</div>
""",
js=r"""
function dcCalc(){
  var price=num('dcPrice'),store=num('dcStore')||0,promo=num('dcPromo')||0,ptype=val('dcPromoType');
  if(isNaN(price)){$('#dcErr').innerHTML='<div class="alert err">Ilagay ang presyo.</div>';return;}
  $('#dcErr').innerHTML='';
  var afterStore=price*(1-store/100);var storeAmt=price-afterStore;
  var promoAmt=ptype==='pct'?afterStore*promo/100:promo;
  if(promoAmt>afterStore)promoAmt=afterStore;
  var final=afterStore-promoAmt;var save=price-final;
  $('#dcROrig').textContent=money(price);$('#dcRStore').textContent='-'+money(storeAmt);
  $('#dcRPromo').textContent='-'+money(promoAmt);$('#dcRFinal').textContent=money(final);
  $('#dcRSave').textContent=money(save)+' ('+(save/price*100).toFixed(0)+'%)';
  $('#dcBig').textContent=money(final);$('#dcSub').textContent='tipid '+money(save);
  $('#dcDFinal').textContent=money(final);$('#dcDSave').textContent=money(save);
  toast('Kalkulado');show('result');
}
function dcNew(){resetForm(['dcPrice','dcStore','dcPromo']);$('#dcErr').innerHTML='';show('input');}
""")

# ---------------- APP 15: Cash Flow Forecast ----------------
define(name="Cash Flow Forecast", icon="\U0001F4CA", tag="Pera papasok/palabas",
home=r"""
<div class="hero"><div class="mut small">Net Cash Flow</div><div class="big" id="cfBig">\u20B10.00</div><div class="mut small" id="cfSub">papasok \u2212 palabas</div></div>
<button class="btn" data-go="input">\U0001F4CA Kalkulahin</button>
<h3>Paliwanag</h3>
<div class="card tight mut small">Alamin kung positibo o negatibo ang takbo ng pera sa loob ng isang panahon.</div>
""",
input=r"""
<div class="card">
 <div class="field"><label>Panahon</label><input id="cfPeriod" placeholder="Hal: Nobyembre"></div>
 <div class="field"><label>Pera Papasok (PHP)</label><input id="cfIn" type="number" inputmode="decimal" placeholder="Hal: 80000"></div>
 <div class="field"><label>Pera Palabas (PHP)</label><input id="cfOut" type="number" inputmode="decimal" placeholder="Hal: 55000"></div>
 <div class="field"><label>Panimulang Cash (PHP)</label><input id="cfStart" type="number" inputmode="decimal" placeholder="Hal: 20000"></div>
 <button class="btn" onclick="cfCalc()">Kalkulahin</button>
 <div id="cfErr"></div>
</div>
""",
result=r"""
<div class="card">
 <div class="kv"><span>Panahon</span><b id="cfRPeriod">&mdash;</b></div>
 <div class="kv"><span>Papasok</span><b id="cfRIn">&mdash;</b></div>
 <div class="kv"><span>Palabas</span><b id="cfROut">&mdash;</b></div>
 <div class="kv"><span>Net Cash Flow</span><b id="cfRNet">&mdash;</b></div>
 <div class="kv"><span>Katapusang Cash</span><b id="cfREnd">&mdash;</b></div>
 <div class="kv"><span>Kalagayan</span><b><span class="pill" id="cfRStatus">&mdash;</span></b></div>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F4CA</div>
 <h2>Kalkulado</h2>
 <div class="kv"><span>Net</span><b id="cfDNet">&mdash;</b></div>
 <div class="kv"><span>Katapusan</span><b id="cfDEnd">&mdash;</b></div>
 <button class="btn ghost" onclick="cfNew()">\u2795 Bagong Compute</button>
</div>
""",
js=r"""
function cfCalc(){
  var period=val('cfPeriod')||'Kasalukuyan',inc=num('cfIn')||0,out=num('cfOut')||0,start=num('cfStart')||0;
  if(isNaN(inc)||isNaN(out)){$('#cfErr').innerHTML='<div class="alert err">Ilagay ang papasok at palabas.</div>';return;}
  $('#cfErr').innerHTML='';
  var net=inc-out;var end=start+net;var ok=net>=0;
  $('#cfRPeriod').textContent=period;$('#cfRIn').textContent=money(inc);$('#cfROut').textContent=money(out);
  $('#cfRNet').textContent=(net<0?'-':'')+money(Math.abs(net));
  $('#cfREnd').textContent=money(end);
  var s=$('#cfRStatus');s.textContent=ok?'POSITIBO':'NEGATIBO';s.className='pill '+(ok?'ok':'bad');
  $('#cfBig').textContent=(net<0?'-':'')+money(Math.abs(net));$('#cfSub').textContent=period;
  $('#cfDNet').textContent=(net<0?'-':'')+money(Math.abs(net));$('#cfDEnd').textContent=money(end);
  toast('Kalkulado');show('result');
}
function cfNew(){resetForm(['cfPeriod','cfIn','cfOut','cfStart']);$('#cfErr').innerHTML='';show('input');}
""")


def make_icon(path, size):
    """Business-themed icon: blue circle with gold ring."""
    img = Image.new("RGB", (size, size), "#0b6cf0")
    d = ImageDraw.Draw(img)
    d.ellipse([size*0.14, size*0.14, size*0.86, size*0.86], fill="#0a3f8f")
    d.ellipse([size*0.2, size*0.2, size*0.8, size*0.8], outline="#fcd116", width=max(2, int(size*0.03)))
    cx, cy, r = size/2, size/2, size*0.26
    d.rectangle([cx-r*0.9, cy-r*0.2, cx+r*0.9, cy+r*0.2], fill="#fcd116")
    d.rectangle([cx-r*0.2, cy-r*0.9, cx+r*0.2, cy+r*0.9], fill="#fcd116")
    img.save(path)


def slug(name):
    s = name.lower()
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    return s


def deunicode(s):
    s = re.sub(r'\\U([0-9a-fA-F]{8})', lambda m: chr(int(m.group(1), 16)), s)
    s = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), s)
    return s


def page(app):
    tabs = [('home', 'Home', '\U0001F3E0'), ('input', 'Input', '\u270F\uFE0F'),
            ('result', 'Resulta', '\U0001F4CA'), ('done', 'Tapos Na', '\u2705')]
    nav = ''.join('<button data-go="%s"><span class="e">%s</span>%s</button>' % (k, ic, lb) for k, lb, ic in tabs)
    return """<!DOCTYPE html>
<html lang="fil">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#0b6cf0">
<title>%(name)s</title>
<style>%(css)s</style>
</head>
<body>
<div class="wrap">
  <header class="app">
    <div class="logo">%(icon)s</div>
    <div><h1>%(name)s</h1><div class="tag">MCSN Negosyo Toolkit &bull; %(tag)s</div></div>
  </header>
  <main>
    <section class="screen" data-screen="home">%(home)s</section>
    <section class="screen" data-screen="input" hidden>%(inp)s</section>
    <section class="screen" data-screen="result" hidden>%(res)s</section>
    <section class="screen" data-screen="done" hidden>%(done)s</section>
  </main>
  <div class="foot">MCSN Negosyo Toolkit &bull; Offline HTML App<br>Para sa maliliit na negosyo ng Pilipino</div>
</div>
<nav class="tabs">%(nav)s</nav>
<div class="toast"></div>
<script>%(rt)s</script>
<script>%(js)s</script>
</body>
</html>""" % dict(name=app['name'], css=LIGHT_CSS, icon=app['icon'], tag=app['tag'],
                   home=app['home'], inp=app['input'], res=app['result'], done=app['done'],
                   nav=nav, rt=RUNTIME_JS, js=app['js'])


HUB_TEMPLATE = """<!DOCTYPE html>
<html lang="fil">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MCSN Negosyo Toolkit - %(count)s Apps</title>
<style>%(css)s
.appcard{display:flex;align-items:center;gap:12px;padding:14px;border-radius:14px;background:var(--card);border:1px solid var(--line);text-decoration:none;color:var(--txt);margin-bottom:10px;box-shadow:var(--shadow)}
.appcard .e{width:44px;height:44px;border-radius:12px;background:var(--card2);display:flex;align-items:center;justify-content:center;font-size:23px;flex:0 0 auto}
.appcard .n{font-weight:700;font-size:14px}
.appcard .t{font-size:12px;color:var(--mut);margin-top:2px}
</style>
</head>
<body>
<div class="wrap">
 <header class="app"><div class="logo">\U0001F3E2</div><div><h1>MCSN Negosyo Toolkit</h1><div class="tag">%(count)s Business Apps \u2022 Offline</div></div></header>
 <div class="hero"><div class="mut small">Para sa maliliit na negosyo</div><div class="big">%(count)s Apps</div><div class="mut small">Light theme \u2022 Mobile-first \u2022 Offline</div></div>
 <a class="btn" href="downloads.html" style="text-decoration:none">\u2B07 Downloads at ZIP</a>
 <h3>Lahat ng Apps</h3>
 %(cards)s
 <div class="foot">MCSN Negosyo Toolkit &bull; Batch 2</div>
</div>
</body>
</html>"""

DOWNLOADS_TEMPLATE = """<!DOCTYPE html>
<html lang="fil">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Downloads - MCSN Negosyo Toolkit</title>
<style>%(css)s
.dlcard{padding:14px;border-radius:14px;background:var(--card);border:1px solid var(--line);margin-bottom:10px;box-shadow:var(--shadow)}
.dlhead{display:flex;align-items:center;gap:12px;margin-bottom:10px}
.dlhead .e{width:42px;height:42px;border-radius:12px;background:var(--card2);display:flex;align-items:center;justify-content:center;font-size:22px;flex:0 0 auto}
.dlhead .n{font-weight:700;font-size:14px}
.dlhead .t{font-size:12px;color:var(--mut);margin-top:2px}
.dlbtns{display:flex;gap:8px}
.dlbtns .btn{margin-top:0}
</style>
</head>
<body>
<div class="wrap">
 <header class="app"><div class="logo">\u2B07</div><div><h1>Downloads</h1><div class="tag">%(count)s Apps \u2022 Installable + ZIP</div></div></header>
 <div class="hero"><div class="mut small">%(count)s Apps \u2022 Bawat isa</div><div class="big">Install + Download</div><div class="mut small">Buksan sa Chrome para sa "Add to Home Screen"</div></div>
 <a class="btn" href="downloads/ALL-%(count)s-Apps.zip" style="text-decoration:none;display:block;text-align:center;margin-bottom:14px">\u2B07 DOWNLOAD LAHAT \u2014 1 ZIP (%(count)s apps)</a>
 %(cards)s
 <div class="foot">MCSN Negosyo Toolkit &bull; Batch 2</div>
</div>
</body>
</html>"""


def write_pwa(app, folder, d, idx):
    name = app['name']; short = name[:12]
    icon_dir = os.path.join(d, "icons"); os.makedirs(icon_dir, exist_ok=True)
    for s in (192, 512):
        make_icon(os.path.join(icon_dir, "icon-%d.png" % s), s)
    manifest = {
        "name": name, "short_name": short, "start_url": "./index.html",
        "scope": "./", "display": "standalone", "orientation": "portrait",
        "background_color": "#f4f7fb", "theme_color": "#0b6cf0", "lang": "fil",
        "description": "MCSN Negosyo Toolkit - %s. Offline HTML app." % app['tag'],
        "icons": [
            {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
            {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}
        ]
    }
    with open(os.path.join(d, "manifest.webmanifest"), 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    sw = ("const CACHE='mcsn2-%s-v1';\n"
          "const ASSETS=['./','./index.html','./manifest.webmanifest','./icons/icon-192.png','./icons/icon-512.png'];\n"
          "self.addEventListener('install',e=>{self.skipWaiting();e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS)));});\n"
          "self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))));});\n"
          "self.addEventListener('fetch',e=>{e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request).then(resp=>{const cp=resp.clone();caches.open(CACHE).then(c=>c.put(e.request,cp));return resp;}).catch(()=>caches.match('./index.html'))));});\n") % folder
    with open(os.path.join(d, "sw.js"), 'w', encoding='utf-8') as f:
        f.write(sw)
    head = ('<link rel="manifest" href="manifest.webmanifest">\n'
            '<link rel="icon" href="icons/icon-192.png">\n'
            '<link rel="apple-touch-icon" href="icons/icon-192.png">\n'
            '<meta name="apple-mobile-web-app-capable" content="yes">\n'
            '<meta name="mobile-web-app-capable" content="yes">\n'
            '<meta name="apple-mobile-web-app-title" content="%s">\n' % name)
    idx = idx.replace('</head>', head + '</head>')
    script = ("<script>if('serviceWorker' in navigator){window.addEventListener('load',function(){navigator.serviceWorker.register('sw.js').catch(function(){});});}</script>\n")
    idx = idx.replace('</body>', script + '</body>')
    return idx


def build():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    dl_dir = os.path.join(OUT, "downloads")
    os.makedirs(dl_dir)
    cards = []; dl_cards = []; apps_info = []
    for i, app in enumerate(APPS, 1):
        folder = "%02d-%s" % (i, slug(app['name']))
        apps_info.append((i, app, folder))
        d = os.path.join(OUT, folder)
        os.makedirs(d, exist_ok=True)
        html = deunicode(page(app))
        html = write_pwa(app, folder, d, html)
        with open(os.path.join(d, "index.html"), 'w', encoding='utf-8') as f:
            f.write(html)
        with open(os.path.join(d, "README.md"), 'w', encoding='utf-8') as f:
            f.write("# %s\n\nMCSN Negosyo Toolkit \u2022 %s (App #%d)\n\n" % (app['name'], BATCH, i))
            f.write("- Screens: Home / Input / Resulta / Tapos Na\n")
            f.write("- Logic: %s\n" % app['tag'])
            f.write("- Offline, mobile-first, vanilla JS (localStorage)\n")
        zip_name = "%s.zip" % folder
        with zipfile.ZipFile(os.path.join(dl_dir, zip_name), 'w', zipfile.ZIP_DEFLATED) as z:
            for root, _, files in os.walk(d):
                for fn in files:
                    fp = os.path.join(root, fn)
                    z.write(fp, os.path.join(folder, os.path.relpath(fp, d)))
        cards.append('<a class="appcard" href="%s/index.html"><div class="e">%s</div><div><div class="n">%d. %s</div><div class="t">%s</div></div></a>' % (folder, app['icon'], i, app['name'], app['tag']))
        dl_cards.append('<div class="dlcard"><div class="dlhead"><div class="e">%s</div><div><div class="n">%d. %s</div><div class="t">%s</div></div></div><div class="dlbtns"><a class="btn" href="%s/index.html">\u25B6 Buksan / Install</a><a class="btn ghost" href="downloads/%s">\u2B07 ZIP</a></div></div>' % (app['icon'], i, app['name'], app['tag'], folder, zip_name))
    with open(os.path.join(OUT, "index.html"), 'w', encoding='utf-8') as f:
        f.write(deunicode(HUB_TEMPLATE % dict(css=LIGHT_CSS, count=len(APPS), cards=''.join(cards))))
    with open(os.path.join(OUT, "downloads.html"), 'w', encoding='utf-8') as f:
        f.write(deunicode(DOWNLOADS_TEMPLATE % dict(css=LIGHT_CSS, count=len(APPS), cards=''.join(dl_cards))))
    all_name = "ALL-%d-Apps.zip" % len(APPS)
    with zipfile.ZipFile(os.path.join(dl_dir, all_name), 'w', zipfile.ZIP_DEFLATED) as z:
        for i, app, folder in apps_info:
            z.write(os.path.join(dl_dir, "%s.zip" % folder), "%s.zip" % folder)
    zip_path = os.path.join(OUT, "MCSN-Negosyo-Toolkit-%d-Apps.zip" % len(APPS))
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(OUT):
            if os.path.abspath(root).startswith(os.path.abspath(dl_dir)):
                continue
            for fn in files:
                fp = os.path.join(root, fn)
                z.write(fp, os.path.relpath(fp, OUT))
    print("Built %d apps -> %s" % (len(APPS), OUT))
    print("Per-app ZIPs -> %s (%d)" % (dl_dir, len(APPS)))
    print("Master ZIP -> %s" % zip_path)


if __name__ == "__main__":
    build()
