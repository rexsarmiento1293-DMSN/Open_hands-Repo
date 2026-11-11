# -*- coding: utf-8 -*-
"""MCSN AppFactory - generates 17 standalone offline HTML apps (Deepseek logic batch)."""
import os, json, re, shutil, zipfile
from PIL import Image, ImageDraw, ImageFont
import icons

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "apps")
APPS = []

BASE_CSS = open(os.path.join(ROOT, "glass_dark.css"), encoding="utf-8").read()

RUNTIME_JS = r"""
const $=(s,r=document)=>r.querySelector(s);
const $$=(s,r=document)=>Array.from(r.querySelectorAll(s));
function money(n){n=Number(n||0);return '\u20B1'+n.toLocaleString('en-PH',{maximumFractionDigits:2});}
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
document.addEventListener('click',function(e){
  var b=e.target.closest('[data-go]');if(!b)return;
  if(b.dataset.go==='__back'){history.length>1?history.back():show('home');return;}
  show(b.dataset.go);
});
function resetForm(ids){ids.forEach(id=>{var e=document.getElementById(id);if(e)e.value='';});}
"""

def page(app):
    tabs=[('home','Home','\U0001F3E0'),('input','Input','\u270F\uFE0F'),
          ('result','Resulta','\U0001F4CA'),('done','Tapos Na','\u2705')]
    nav=''.join('<button data-go="%s"><span class="e">%s</span>%s</button>'%(k,ic,lb) for k,lb,ic in tabs)
    return """<!DOCTYPE html>
<html lang="fil">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#0f1220">
<title>%(name)s</title>
<style>%(css)s</style>
</head>
<body>
<div class="bg"><span></span><span></span><span></span></div>
<div class="wrap">
  <header class="app">
    <div class="logo"><img src="icons/icon-192.png" alt=""></div>
    <div><h1>%(name)s</h1><div class="tag">MCSN AppFactory &bull; %(tag)s</div></div>
  </header>
  <main>
    <section class="screen" data-screen="home">%(home)s</section>
    <section class="screen" data-screen="input" hidden>%(inp)s</section>
    <section class="screen" data-screen="result" hidden>%(res)s</section>
    <section class="screen" data-screen="done" hidden>%(done)s</section>
  </main>
  <div class="foot">FOUNDER DECIDES &bull; REX BUILDS &bull; SOF COMMUNICATES &bull; SYSTEM RECORDS<br>MCSN AppFactory &bull; Offline HTML App</div>
</div>
<nav class="tabs">%(nav)s</nav>
<div class="toast"></div>
<script>%(rt)s</script>
<script>%(js)s</script>
</body>
</html>"""%dict(name=app['name'],css=BASE_CSS,icon=app['icon'],tag=app['tag'],
                 home=app['home'],inp=app['input'],res=app['result'],done=app['done'],
                 nav=nav,rt=RUNTIME_JS,js=app['js'])

def define(**kw):
    APPS.append(kw)

# ---------------- APP 1: Barangay Blotter Helper PRO ----------------
define(name="Barangay Blotter Helper PRO", icon="\U0001F4C1", tag="Logic: Active/Pending/Resolved",
home=r"""
<div class="hero"><div class="mut small">Active Cases</div><div class="big" id="bActive">0</div><div class="mut small" id="bSub">Walang active na kaso</div></div>
<button class="btn" data-go="input">\U0001F4DD File Blotter</button>
<h3>Mga Kaso</h3><div id="bList"></div>
""",
input=r"""
<div class="card">
 <div class="field"><label>Complainant</label><input id="bComp" placeholder="Hal: Juan"></div>
 <div class="field"><label>Respondent</label><input id="bResp" placeholder="Hal: Pedro"></div>
 <div class="field"><label>Nature ng Reklamo</label><input id="bNature" placeholder="Hal: Ingay"></div>
 <button class="btn" onclick="bFile()">I-file ang Kaso</button>
 <div id="bErr"></div>
</div>
""",
result=r"""
<div class="card">
 <div class="kv"><span>Case No.</span><b id="bCaseNo">&mdash;</b></div>
 <div class="kv"><span>Complainant</span><b id="bRComp">&mdash;</b></div>
 <div class="kv"><span>Respondent</span><b id="bRResp">&mdash;</b></div>
 <div class="kv"><span>Nature</span><b id="bRNature">&mdash;</b></div>
 <div class="kv"><span>Status</span><b><span class="pill ok" id="bRStatus">Active</span></b></div>
 <div class="kv"><span>Days Pending</span><b id="bRDays">0</b></div>
 <button class="btn ok" onclick="bResolve()">\u2705 Mark as Resolved</button>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\u2705</div>
 <h2>Resolved</h2>
 <div class="kv"><span>Case No.</span><b id="dCaseNo">&mdash;</b></div>
 <div class="kv"><span>Date Closed</span><b id="dDate">&mdash;</b></div>
 <div class="kv"><span>Status</span><b><span class="pill ok">Resolved</span></b></div>
 <button class="btn ghost" onclick="bNew()">\u2795 Bagong Kaso</button>
</div>
""",
js=r"""
var B_KEY='mcsn_blotter';var bData=Store.get(B_KEY,{seq:0,cases:[]});var bCur=null;
function bSave(){Store.set(B_KEY,bData);}
function bToday(){return new Date().toISOString().slice(0,10);}
function bRender(){
  var act=bData.cases.filter(function(c){return c.status==='Active';}).length;
  $('#bActive').textContent=act;
  $('#bSub').textContent=act?('May '+act+' active na kaso'):'Walang active na kaso';
  var el=$('#bList');
  if(!bData.cases.length){el.innerHTML='<div class="mut small">Wala pang kaso.</div>';return;}
  el.innerHTML=bData.cases.slice().reverse().map(function(c){
    var pill=c.status==='Active'?'<span class="pill warn">Active</span>':'<span class="pill ok">Resolved</span>';
    return '<div class="item"><div class="ic">\U0001F4C1</div><div class="grow"><div class="t">Case #'+c.no+' &middot; '+c.nature+'</div><div class="s">'+c.complainant+' vs '+c.respondent+'</div></div>'+pill+'</div>';
  }).join('');
}
function bFile(){
  var c=val('bComp'),r=val('bResp'),n=val('bNature');
  if(!c||!r||!n){$('#bErr').innerHTML='<div class="alert err">Kailangan punan lahat</div>';return;}
  $('#bErr').innerHTML='';
  bData.seq++;var no=String(bData.seq).padStart(3,'0');
  bCur={no:no,complainant:c,respondent:r,nature:n,status:'Active',filed:bToday(),closed:null};
  bData.cases.push(bCur);bSave();bRender();bFill();
  toast('Case #'+no+' filed');show('result');
}
function bFill(){
  if(!bCur)return;
  $('#bCaseNo').textContent='#'+bCur.no;$('#bRComp').textContent=bCur.complainant;
  $('#bRResp').textContent=bCur.respondent;$('#bRNature').textContent=bCur.nature;
  var days=Math.max(0,Math.round((Date.now()-new Date(bCur.filed).getTime())/86400000));
  $('#bRDays').textContent=days;$('#bRStatus').textContent=bCur.status;
}
function bResolve(){
  if(!bCur)return;bCur.status='Resolved';bCur.closed=bToday();bSave();bRender();
  $('#dCaseNo').textContent='#'+bCur.no;$('#dDate').textContent=bCur.closed;
  toast('Case #'+bCur.no+' resolved');show('done');
}
function bNew(){resetForm(['bComp','bResp','bNature']);show('input');}
bRender();
""")

# ---------------- APP 2: Sari-Sari Price List + Tubo PRO ----------------
define(name="Sari-Sari Price List + Tubo PRO", icon="\U0001F6D2", tag="Tubo = Benta - Puhunan",
home=r"""
<div class="hero"><div class="mut small">Paninda sa listahan</div><div class="big" id="sCount">0</div><div class="mut small">Presyo base sa example</div></div>
<button class="btn" data-go="input">\u2795 Magdagdag ng Paninda</button>
<h3>Price List</h3><div id="sList"></div>
""",
input=r"""
<div class="card">
 <div class="field"><label>Pangalan ng Paninda</label><input id="sName" placeholder="Hal: Sardinas"></div>
 <div class="row">
   <div class="field"><label>Puhunan</label><input id="sCost" type="number" inputmode="decimal" placeholder="18"></div>
   <div class="field"><label>Benta</label><input id="sPrice" type="number" inputmode="decimal" placeholder="25"></div>
 </div>
 <button class="btn" onclick="sCalc()">Kalkulahin ang Tubo</button>
 <div id="sErr"></div>
</div>
""",
result=r"""
<div class="card">
 <div class="kv"><span>Paninda</span><b id="sRName">&mdash;</b></div>
 <div class="kv"><span>Puhunan</span><b id="sRCost">&mdash;</b></div>
 <div class="kv"><span>Benta</span><b id="sRPrice">&mdash;</b></div>
 <div class="kv"><span>Tubo</span><b id="sRTubo">&mdash;</b></div>
 <div class="kv"><span>Porsyento</span><b id="sRPct">&mdash;</b></div>
 <div class="kv"><span>Kita</span><b id="sRKita">&mdash;</b></div>
 <div id="sRMsg"></div>
 <button class="btn ok" onclick="sPaid()">\U0001F9FE Resibo + PAID</button>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F9FE</div>
 <h2>Naka-save na</h2>
 <div class="mut small" id="sDMsg">Resibo + PAID</div>
 <div id="sDList" style="margin-top:12px;text-align:left"></div>
 <button class="btn ghost" onclick="sNew()">\u2795 Bagong Paninda</button>
</div>
""",
js=r"""
var S_KEY='mcsn_sarisari';var sData=Store.get(S_KEY,[]);var sCur=null;
function sSave(){Store.set(S_KEY,sData);}
function sRender(){
  $('#sCount').textContent=sData.length;
  var el=$('#sList');
  if(!sData.length){el.innerHTML='<div class="mut small">Wala pang paninda. Idagdag ang una.</div>';return;}
  el.innerHTML=sData.slice().reverse().map(function(p){
    var lugi=p.tubo<0;var cls=lugi?'bad':'ok';
    return '<div class="item"><div class="ic">\U0001F6D2</div><div class="grow"><div class="t">'+p.name+'</div><div class="s">Puhunan '+money(p.cost)+' &rarr; Benta '+money(p.price)+'</div></div><span class="pill '+cls+'">'+(lugi?'Lugi ':'')+money(p.tubo)+'</span></div>';
  }).join('');
}
function sCalc(){
  var name=val('sName'),cost=num('sCost'),price=num('sPrice');
  if(!name){$('#sErr').innerHTML='<div class="alert err">Ilagay pangalan ng paninda</div>';return;}
  if(isNaN(cost)||cost===0){$('#sErr').innerHTML='<div class="alert err">Ilagay puhunan</div>';return;}
  if(isNaN(price)){$('#sErr').innerHTML='<div class="alert err">Ilagay benta</div>';return;}
  $('#sErr').innerHTML='';
  var tubo=price-cost,pct=(tubo/cost)*100;
  sCur={name:name,cost:cost,price:price,tubo:tubo,pct:pct};
  $('#sRName').textContent=name;$('#sRCost').textContent=money(cost);
  $('#sRPrice').textContent=money(price);$('#sRTubo').textContent=money(tubo);
  $('#sRPct').textContent=pct.toFixed(1)+'%';$('#sRKita').textContent=money(price)+' - '+money(cost)+' = '+money(tubo);
  $('#sRMsg').innerHTML=tubo<0?'<div class="alert err">Lugi ka</div>':'<div class="alert ok">May tubo: '+money(tubo)+' ('+pct.toFixed(1)+'%)</div>';
  show('result');
}
function sPaid(){
  if(!sCur)return;sData.push(sCur);sSave();sRender();
  $('#sDMsg').textContent='Resibo: '+sCur.name+' \u2014 PAID';
  $('#sDList').innerHTML='<div class="kv"><span>Tubo</span><b>'+money(sCur.tubo)+'</b></div><div class="kv"><span>Porsyento</span><b>'+sCur.pct.toFixed(1)+'%</b></div>';
  toast('Naka-save: '+sCur.name);show('done');
}
function sNew(){resetForm(['sName','sCost','sPrice']);show('input');}
sRender();
""")

# ---------------- APP 3: Toda Fare Calculator PRO ----------------
define(name="Toda Fare Calculator PRO", icon="\U0001F695", tag="Base + Distansya x Rate",
home=r"""
<div class="hero"><div class="mut small">Base Fare</div><div class="big">\u20B110</div><div class="mut small">Rate: \u20B115 / km \u2022 Discount 20% (Student/Senior)</div></div>
<button class="btn" data-go="input">\U0001F695 Kalkulahin ang Pamasahe</button>
<h3>Mga Naka-save</h3><div id="tList"></div>
""",
input=r"""
<div class="card">
 <div class="field"><label>Distansya (km)</label><input id="tDist" type="number" inputmode="decimal" placeholder="5"></div>
 <div class="field"><label>Uri ng Pasahero</label>
  <select id="tType"><option value="Regular">Regular</option><option value="Student">Student (-20%)</option><option value="Senior">Senior (-20%)</option></select>
 </div>
 <button class="btn" onclick="tCalc()">Kalkulahin</button>
 <div id="tErr"></div>
</div>
""",
result=r"""
<div class="card">
 <div class="kv"><span>Base Fare</span><b id="tRBase">\u20B110</b></div>
 <div class="kv"><span>Distansya</span><b id="tRDist">&mdash;</b></div>
 <div class="kv"><span>Rate</span><b id="tRRate">\u20B115/km</b></div>
 <div class="kv"><span>Subtotal</span><b id="tRSub">&mdash;</b></div>
 <div class="kv"><span>Discount</span><b id="tRDisc">&mdash;</b></div>
 <div class="kv"><span><b>TOTAL</b></span><b class="big" id="tRTotal">&mdash;</b></div>
 <button class="btn ok" onclick="tSave()">\U0001F4BE I-save ang Resibo</button>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F695</div>
 <h2>Naka-save</h2>
 <div class="mut small" id="tDMsg">Resibo ng pamasahe</div>
 <div id="tDList" style="margin-top:12px;text-align:left"></div>
 <button class="btn ghost" onclick="tNew()">\u2795 Bagong Kalkula</button>
</div>
""",
js=r"""
var T_KEY='mcsn_toda';var BASE=10,RATE=15;var tData=Store.get(T_KEY,[]);var tCur=null;
function tSaveData(){Store.set(T_KEY,tData);}
function tRender(){
  var el=$('#tList');
  if(!tData.length){el.innerHTML='<div class="mut small">Wala pang naka-save.</div>';return;}
  el.innerHTML=tData.slice().reverse().map(function(r){
    return '<div class="item"><div class="ic">\U0001F695</div><div class="grow"><div class="t">'+r.dist+' km \u2022 '+r.type+'</div><div class="s">Base '+money(BASE)+' + '+money(RATE)+'/km</div></div><span class="pill pri">'+money(r.total)+'</span></div>';
  }).join('');
}
function tCalc(){
  var d=num('tDist'),type=val('tType');
  if(isNaN(d)){$('#tErr').innerHTML='<div class="alert err">Ilagay distansya</div>';return;}
  if(d<=0){$('#tErr').innerHTML='<div class="alert err">Ilagay distansya</div>';return;}
  $('#tErr').innerHTML='';
  var sub=BASE+d*RATE,disc=(type==='Regular')?0:sub*0.20,total=sub-disc;
  tCur={dist:d,type:type,sub:sub,disc:disc,total:total};
  $('#tRDist').textContent=d+' km';$('#tRSub').textContent=money(sub);
  $('#tRDisc').textContent=(disc?('-'+money(disc)):'Wala');$('#tRTotal').textContent=money(total);
  show('result');
}
function tSave(){
  if(!tCur)return;tData.push(tCur);tSaveData();tRender();
  $('#tDMsg').textContent=tCur.dist+' km \u2022 '+tCur.type+' \u2022 '+money(tCur.total);
  $('#tDList').innerHTML='<div class="kv"><span>Subtotal</span><b>'+money(tCur.sub)+'</b></div><div class="kv"><span>Discount</span><b>-'+money(tCur.disc)+'</b></div><div class="kv"><span>Total</span><b>'+money(tCur.total)+'</b></div>';
  toast('Resibo naka-save');show('done');
}
function tNew(){resetForm(['tDist']);show('input');}
tRender();
""")

# ---------------- APP 4: Electric Bill Estimator PRO ----------------
define(name="Electric Bill Estimator PRO", icon="\u26A1", tag="Usage x Rate + Fixed",
home=r"""
<div class="hero"><div class="mut small">Rate base</div><div class="big">\u20B112/kWh</div><div class="mut small">+ Fixed charges kung meron</div></div>
<button class="btn" data-go="input">\u26A1 I-estimate ang Bill</button>
<h3>History</h3><div id="eList"></div>
""",
input=r"""
<div class="card">
 <div class="row">
  <div class="field"><label>Previous Reading</label><input id="ePrev" type="number" inputmode="decimal" placeholder="1200"></div>
  <div class="field"><label>Current Reading</label><input id="eCur" type="number" inputmode="decimal" placeholder="1500"></div>
 </div>
 <div class="row">
  <div class="field"><label>Rate / kWh</label><input id="eRate" type="number" inputmode="decimal" value="12"></div>
  <div class="field"><label>Fixed Charges</label><input id="eFix" type="number" inputmode="decimal" value="0"></div>
 </div>
 <button class="btn" onclick="eCalc()">Kalkulahin</button>
 <div id="eErr"></div>
</div>
""",
result=r"""
<div class="card">
 <div class="kv"><span>Consumption</span><b id="eRUse">&mdash;</b></div>
 <div class="kv"><span>Rate</span><b id="eRRate">&mdash;</b></div>
 <div class="kv"><span>Fixed</span><b id="eRFix">&mdash;</b></div>
 <div class="kv"><span><b>TOTAL BILL</b></span><b class="big" id="eRTotal">&mdash;</b></div>
 <button class="btn ok" onclick="eSave()">\U0001F4BE I-save</button>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\u26A1</div>
 <h2>Bill Estimated</h2>
 <div class="mut small">Naka-save na sa history</div>
 <button class="btn ghost" onclick="eNew()">\u2795 Bagong Estimate</button>
</div>
""",
js=r"""
var E_KEY='mcsn_electric';var eData=Store.get(E_KEY,[]);var eCur=null;
function eSaveData(){Store.set(E_KEY,eData);}
function eRender(){
  var el=$('#eList');
  if(!eData.length){el.innerHTML='<div class="mut small">Wala pang estimate.</div>';return;}
  el.innerHTML=eData.slice().reverse().map(function(r){
    return '<div class="item"><div class="ic">\u26A1</div><div class="grow"><div class="t">'+r.use+' kWh</div><div class="s">'+r.prev+' \u2192 '+r.cur+' @ '+money(r.rate)+'/kWh</div></div><span class="pill pri">'+money(r.total)+'</span></div>';
  }).join('');
}
function eCalc(){
  var prev=num('ePrev'),cur=num('eCur'),rate=num('eRate'),fix=num('eFix');
  if(isNaN(prev)||isNaN(cur)){$('#eErr').innerHTML='<div class="alert err">Ilagay readings</div>';return;}
  if(cur<prev){$('#eErr').innerHTML='<div class="alert err">Mali ang reading</div>';return;}
  if(isNaN(rate))rate=12;if(isNaN(fix))fix=0;
  $('#eErr').innerHTML='';
  var use=cur-prev,total=use*rate+fix;
  eCur={prev:prev,cur:cur,rate:rate,fix:fix,use:use,total:total};
  $('#eRUse').textContent=use+' kWh';$('#eRRate').textContent=money(rate)+'/kWh';
  $('#eRFix').textContent=money(fix);$('#eRTotal').textContent=money(total);
  show('result');
}
function eSave(){if(!eCur)return;eData.push(eCur);eSaveData();eRender();toast('Naka-save');show('done');}
function eNew(){resetForm(['ePrev','eCur']);show('input');}
eRender();
""")

# ---------------- APP 5: Rent / Bills Reminder PRO ----------------
define(name="Rent / Bills Reminder PRO", icon="\U0001F4C5", tag="Days Left = Due - Today",
home=r"""
<div class="hero"><div class="mut small">Bills na babayaran</div><div class="big" id="rCount">0</div><div class="mut small" id="rSub">Wala pang bill</div></div>
<button class="btn" data-go="input">\u2795 Magdagdag ng Bill</button>
<h3>Listahan</h3><div id="rList"></div>
""",
input=r"""
<div class="card">
 <div class="field"><label>Pangalan ng Bill</label><input id="rName" placeholder="Hal: Rent"></div>
 <div class="field"><label>Halaga</label><input id="rAmt" type="number" inputmode="decimal" placeholder="5000"></div>
 <div class="field"><label>Due Date</label><input id="rDue" type="date"></div>
 <button class="btn" onclick="rAdd()">Idagdag</button>
 <div id="rErr"></div>
</div>
""",
result=r"""
<div class="card">
 <div class="kv"><span>Bill</span><b id="rRName">&mdash;</b></div>
 <div class="kv"><span>Halaga</span><b id="rRAmt">&mdash;</b></div>
 <div class="kv"><span>Due Date</span><b id="rRDue">&mdash;</b></div>
 <div class="kv"><span>Status</span><b><span class="pill" id="rRStatus">&mdash;</span></b></div>
 <button class="btn ok" onclick="rPaid()">\u2705 Mark as Paid</button>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\u2705</div>
 <h2>Paid</h2>
 <div class="mut small" id="rDMsg">Bayad na</div>
 <button class="btn ghost" onclick="rNew()">\u2795 Bagong Bill</button>
</div>
""",
js=r"""
var R_KEY='mcsn_rent';var rData=Store.get(R_KEY,[]);var rCur=null;
function rSave(){Store.set(R_KEY,rData);}
function rDays(due){var d=new Date(due+'T00:00:00');var n=new Date();n.setHours(0,0,0,0);return Math.round((d-n)/86400000);}
function rStatus(b){if(b.paid)return['ok','Paid'];var d=rDays(b.due);if(d<0)return['bad','Overdue'];if(d<=2)return['warn','Due in '+d+' day'+(d===1?'':'s')];return['pri','Due in '+d+' days'];}
function rRender(){
  var un=rData.filter(function(b){return !b.paid;}).length;
  $('#rCount').textContent=un;
  $('#rSub').textContent=rData.length?('Unpaid: '+un):'Wala pang bill';
  var el=$('#rList');
  if(!rData.length){el.innerHTML='<div class="mut small">Wala pang bill. Magdagdag.</div>';return;}
  el.innerHTML=rData.slice().reverse().map(function(b){
    var s=rStatus(b);
    return '<div class="item"><div class="ic">\U0001F4C5</div><div class="grow"><div class="t">'+b.name+' \u2022 '+money(b.amt)+'</div><div class="s">Due: '+b.due+'</div></div><span class="pill '+s[0]+'">'+s[1]+'</span></div>';
  }).join('');
}
function rAdd(){
  var name=val('rName'),amt=num('rAmt'),due=val('rDue');
  if(!name||isNaN(amt)||!due){$('#rErr').innerHTML='<div class="alert err">Punan lahat ng field</div>';return;}
  $('#rErr').innerHTML='';
  rCur={name:name,amt:amt,due:due,paid:false};rData.push(rCur);rSave();rRender();
  $('#rRName').textContent=name;$('#rRAmt').textContent=money(amt);$('#rRDue').textContent=due;
  var s=rStatus(rCur);$('#rRStatus').textContent=s[1];$('#rRStatus').className='pill '+s[0];
  show('result');
}
function rPaid(){if(!rCur)return;rCur.paid=true;rSave();rRender();
  $('#rDMsg').textContent=rCur.name+' \u2014 bayad na ('+money(rCur.amt)+')';toast('Paid');show('done');}
function rNew(){resetForm(['rName','rAmt','rDue']);show('input');}
rRender();
""")

# ---------------- APP 6: Calculator + Discount PRO ----------------
define(name="Calculator + Discount PRO", icon="\U0001F9EE", tag="Final = Price - Discount",
home=r"""
<div class="hero"><div class="mut small">Discount Calculator</div><div class="big">%</div><div class="mut small">Alamin ang bawas at final price</div></div>
<button class="btn" data-go="input">\U0001F9EE Kalkulahin</button>
""",
input=r"""
<div class="card">
 <div class="field"><label>Presyo</label><input id="dPrice" type="number" inputmode="decimal" placeholder="1000"></div>
 <div class="field"><label>Discount (%)</label><input id="dPct" type="number" inputmode="decimal" placeholder="20"></div>
 <button class="btn" onclick="dCalc()">Kalkulahin</button>
 <div id="dErr"></div>
</div>
""",
result=r"""
<div class="card">
 <div class="kv"><span>Presyo</span><b id="dRPrice">&mdash;</b></div>
 <div class="kv"><span>Discount</span><b id="dRDisc">&mdash;</b></div>
 <div class="kv"><span><b>FINAL PRICE</b></span><b class="big" id="dRFinal">&mdash;</b></div>
 <button class="btn ok" onclick="dSave()">\U0001F4BE Sale Summary</button>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F3F7\uFE0F</div>
 <h2>Sale Summary</h2>
 <div id="dDList" style="text-align:left;margin-top:8px"></div>
 <button class="btn ghost" onclick="dNew()">\U0001F9EE Bagong Kalkula</button>
</div>
""",
js=r"""
var dCur=null;
function dCalc(){
  var p=num('dPrice'),pc=num('dPct');
  if(isNaN(p)||p<0){$('#dErr').innerHTML='<div class="alert err">Invalid</div>';return;}
  if(isNaN(pc)||pc<0){$('#dErr').innerHTML='<div class="alert err">Ilagay discount</div>';return;}
  if(pc>100){$('#dErr').innerHTML='<div class="alert err">Max 100%</div>';return;}
  $('#dErr').innerHTML='';
  var disc=p*(pc/100),final=p-disc;
  dCur={price:p,pct:pc,disc:disc,final:final};
  $('#dRPrice').textContent=money(p);$('#dRDisc').textContent='-'+money(disc);
  $('#dRFinal').textContent=money(final);show('result');
}
function dSave(){
  if(!dCur)return;
  $('#dDList').innerHTML='<div class="kv"><span>Presyo</span><b>'+money(dCur.price)+'</b></div><div class="kv"><span>Discount ('+dCur.pct+'%)</span><b>-'+money(dCur.disc)+'</b></div><div class="kv"><span>Final</span><b>'+money(dCur.final)+'</b></div>';
  toast('Sale summary saved');show('done');
}
function dNew(){resetForm(['dPrice','dPct']);show('input');}
""")

# ---------------- APP 7: Unit Converter PRO ----------------
define(name="Unit Converter PRO", icon="\U0001F4CF", tag="Standard conversions",
home=r"""
<div class="hero"><div class="mut small">Categories</div><div class="big">3</div><div class="mut small">Haba, Timbang, Temperatura</div></div>
<button class="btn" data-go="input">\U0001F4CF Mag-convert</button>
<h3>History</h3><div id="uList"></div>
""",
input=r"""
<div class="card">
 <div class="field"><label>Kategorya</label>
  <select id="uCat" onchange="uFill()">
   <option value="length">Haba (Length)</option>
   <option value="weight">Timbang (Weight)</option>
   <option value="temp">Temperatura</option>
  </select>
 </div>
 <div class="field"><label>Halaga</label><input id="uVal" type="number" inputmode="decimal" placeholder="5"></div>
 <div class="row">
  <div class="field"><label>Mula sa</label><select id="uFrom"></select></div>
  <div class="field"><label>Papunta sa</label><select id="uTo"></select></div>
 </div>
 <button class="btn" onclick="uCalc()">I-convert</button>
 <div id="uErr"></div>
</div>
""",
result=r"""
<div class="card">
 <div class="kv"><span>Input</span><b id="uRIn">&mdash;</b></div>
 <div class="kv"><span>Resulta</span><b class="big" id="uROut">&mdash;</b></div>
 <button class="btn ok" onclick="uSave()">\U0001F4BE Conversion History</button>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F4CF</div>
 <h2>Naka-save</h2>
 <div class="mut small">Nasa history na</div>
 <button class="btn ghost" onclick="uNew()">\u2795 Bagong Convert</button>
</div>
""",
js=r"""
var UNITS={
 length:{name:'Haba',base:'m',u:{'mm (millimeter)':0.001,'cm (sentimetro)':0.01,'m (metro)':1,'km (kilometro)':1000,'in (pulgada)':0.0254,'ft (talampakan)':0.3048,'yd (yarda)':0.9144,'mi (milya)':1609.344}},
 weight:{name:'Timbang',base:'g',u:{'mg':0.001,'g (gramo)':1,'kg (kilo)':1000,'oz (onsa)':28.349523125,'lb (libra)':453.59237,'t (tonelada)':1000000}},
 temp:{name:'Temperatura',base:'C',u:{'Celsius (C)':1,'Fahrenheit (F)':1,'Kelvin (K)':1}}
};
var U_KEY='mcsn_units';var uData=Store.get(U_KEY,[]);var uCur=null;
function uFill(){
  var cat=val('uCat'),u=Object.keys(UNITS[cat].u);
  $('#uFrom').innerHTML=u.map(function(k){return '<option>'+k+'</option>';}).join('');
  $('#uTo').innerHTML=u.slice().reverse().map(function(k){return '<option>'+k+'</option>';}).join('');
}
function uRender(){
  var el=$('#uList');
  if(!uData.length){el.innerHTML='<div class="mut small">Wala pang conversion.</div>';return;}
  el.innerHTML=uData.slice().reverse().map(function(r){
    return '<div class="item"><div class="ic">\U0001F4CF</div><div class="grow"><div class="t">'+r.txt+'</div></div></div>';
  }).join('');
}
function uConv(cat,from,to,v){
  if(cat==='temp'){
    var c=v;if(from.indexOf('Fahrenheit')>=0)c=(v-32)*5/9;else if(from.indexOf('Kelvin')>=0)c=v-273.15;
    if(to.indexOf('Celsius')>=0)return c;if(to.indexOf('Fahrenheit')>=0)return c*9/5+32;return c+273.15;
  }
  var f=UNITS[cat].u[from],t=UNITS[cat].u[to];return v*f/t;
}
function uCalc(){
  var cat=val('uCat'),from=val('uFrom'),to=val('uTo'),v=num('uVal');
  if(isNaN(v)){$('#uErr').innerHTML='<div class="alert err">Enter value</div>';return;}
  $('#uErr').innerHTML='';
  var out=(from===to)?v:uConv(cat,from,to,v);
  var fShort=from.split(' ')[0],tShort=to.split(' ')[0];
  uCur={txt:v+' '+fShort+' = '+out.toLocaleString('en-PH',{maximumFractionDigits:4})+' '+tShort};
  $('#uRIn').textContent=v+' '+from;
  $('#uROut').textContent=out.toLocaleString('en-PH',{maximumFractionDigits:4})+' '+tShort;
  show('result');
}
function uSave(){if(!uCur)return;uData.push(uCur);Store.set(U_KEY,uData);uRender();toast('Naka-save');show('done');}
function uNew(){resetForm(['uVal']);show('input');}
uFill();uRender();
""")

# ---------------- APP 8: QR Code Info Card PRO ----------------
define(name="QR Code Info Card PRO", icon="\U0001F4F1", tag="Name+Address+Contact -> QR", lib_file="qrcode.min.js",
home=r"""
<div class="hero"><div class="mut small">Digital Contact Card</div><div class="big">QR</div><div class="mut small">Gawa ng QR mula sa info mo</div></div>
<button class="btn" data-go="input">\U0001F4F1 Gumawa ng QR</button>
<h3>Naka-save</h3><div id="qList"></div>
""",
input=r"""
<div class="card">
 <div class="field"><label>Pangalan</label><input id="qName" placeholder="Hal: Rex"></div>
 <div class="field"><label>Address</label><input id="qAddr" placeholder="Hal: Bacoor"></div>
 <div class="field"><label>Contact</label><input id="qPhone" placeholder="Hal: 0912345"></div>
 <button class="btn" onclick="qGen()">Generate QR</button>
 <div id="qErr"></div>
</div>
""",
result=r"""
<div class="card center">
 <div id="qBox" style="display:flex;justify-content:center"></div>
 <div class="mut small" style="margin-top:10px" id="qPreview"></div>
 <button class="btn ok" onclick="qSave()">\U0001F4BE I-save ang QR</button>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F4F1</div>
 <h2>QR Saved</h2>
 <div class="mut small" id="qDMsg">Naka-save na</div>
 <button class="btn ghost" onclick="qNew()">\u2795 Bagong QR</button>
</div>
""",
js=r"""
var Q_KEY='mcsn_qr';var qData=Store.get(Q_KEY,[]);var qCur=null;
function qRender(){
  var el=$('#qList');
  if(!qData.length){el.innerHTML='<div class="mut small">Wala pang naka-save.</div>';return;}
  el.innerHTML=qData.slice().reverse().map(function(c){
    return '<div class="item"><div class="ic">\U0001F4F1</div><div class="grow"><div class="t">'+c.name+'</div><div class="s">'+c.addr+' \u2022 '+c.phone+'</div></div></div>';
  }).join('');
}
function qMake(text){
  var qr=qrcode(0,'M');qr.addData(text);qr.make();
  return qr.createDataURL(6,12);
}
function qGen(){
  var name=val('qName'),addr=val('qAddr'),phone=val('qPhone');
  if(!name){$('#qErr').innerHTML='<div class="alert err">Fill at least Name</div>';return;}
  $('#qErr').innerHTML='';
  var text='BEGIN:VCARD\nVERSION:3.0\nFN:'+name+'\nADR:'+addr+'\nTEL:'+phone+'\nEND:VCARD';
  var url=qMake(text);
  qCur={name:name,addr:addr,phone:phone,url:url};
  $('#qBox').innerHTML='<img class="qr" alt="QR" src="'+url+'">';
  $('#qPreview').textContent=name+' \u2022 '+addr+' \u2022 '+phone;
  show('result');
}
function qSave(){if(!qCur)return;qData.push({name:qCur.name,addr:qCur.addr,phone:qCur.phone});Store.set(Q_KEY,qData);qRender();
  $('#qDMsg').textContent=qCur.name+' \u2014 QR Saved to Gallery';toast('QR saved');show('done');}
function qNew(){resetForm(['qName','qAddr','qPhone']);show('input');}
qRender();
""")

# ---------------- APP 9: Password Checklist PRO ----------------
define(name="Password Checklist PRO", icon="\U0001F510", tag="Score 0-4 strength",
home=r"""
<div class="hero"><div class="mut small">Password Strength</div><div class="big" id="pScoreBig">0/4</div><div class="mut small">Lakas ng password</div></div>
<button class="btn" data-go="input">\U0001F510 Suriin ang Password</button>
<h3>Tips</h3>
<div class="card tight mut small">Gumamit ng 8+ characters, may malaking letra, numero, at special character para maging Strong.</div>
""",
input=r"""
<div class="card">
 <div class="field"><label>Password</label><input id="pPass" type="text" placeholder="Hal: Rex123" oninput="pLive()"></div>
 <button class="btn" onclick="pCheck()">Suriin</button>
 <div id="pErr"></div>
</div>
""",
result=r"""
<div class="card">
 <div class="hero"><div class="mut small">Score</div><div class="big" id="pRScore">&mdash;</div><div class="mut small" id="pRLabel">&mdash;</div></div>
 <div class="kv"><span>8+ characters</span><b id="pL1">&mdash;</b></div>
 <div class="kv"><span>May uppercase</span><b id="pL2">&mdash;</b></div>
 <div class="kv"><span>May numero</span><b id="pL3">&mdash;</b></div>
 <div class="kv"><span>May special char</span><b id="pL4">&mdash;</b></div>
 <button class="btn ok" onclick="pDone()">\u2705 Tapos Na</button>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F512</div>
 <h2>Strong Password Created</h2>
 <div class="mut small" id="pDMsg">Lakas: &mdash;</div>
 <button class="btn ghost" onclick="pNew()">\u2795 Bagong Password</button>
</div>
""",
js=r"""
function pEval(p){
  var s=0;var c1=p.length>=8,c2=/[A-Z]/.test(p),c3=/[0-9]/.test(p),c4=/[^A-Za-z0-9]/.test(p);
  s=(c1?1:0)+(c2?1:0)+(c3?1:0)+(c4?1:0);
  return {score:s,checks:[c1,c2,c3,c4]};
}
function pLabel(s){return s<=1?'Weak':(s<=3?'Medium':'Strong');}
function pLive(){var r=pEval(val('pPass'));$('#pScoreBig').textContent=r.score+'/4';}
function pCheck(){
  var p=val('pPass');
  if(!p){$('#pErr').innerHTML='<div class="alert err">Enter password</div>';return;}
  $('#pErr').innerHTML='';
  var r=pEval(p);var lab=pLabel(r.score);
  $('#pRScore').textContent=r.score+'/4';$('#pRLabel').textContent=lab;
  ['#pL1','#pL2','#pL3','#pL4'].forEach(function(id,i){
    $(id).innerHTML=r.checks[i]?'<span class="pill ok">\u2714 Meron</span>':'<span class="pill bad">\u2716 Wala</span>';
  });
  window.pLab=lab;window.pScore=r.score;show('result');
}
function pDone(){$('#pDMsg').textContent='Lakas: '+(window.pLab||'')+' ('+(window.pScore||0)+'/4)';toast('Naka-check');show('done');}
function pNew(){resetForm(['pPass']);$('#pScoreBig').textContent='0/4';show('input');}
""")

# ---------------- APP 10: Invoice Maker Sari-Sari PRO ----------------
define(name="Invoice Maker Sari-Sari PRO", icon="\U0001F9FE", tag="Total = Sum(Price x Qty)",
home=r"""
<div class="hero"><div class="mut small">Invoice Maker</div><div class="big" id="ivCount">0</div><div class="mut small">items sa kasalukuyang invoice</div></div>
<button class="btn" data-go="input">\U0001F9FE Gumawa ng Invoice</button>
""",
input=r"""
<div class="card">
 <div class="field"><label>Pangalan ng Client</label><input id="ivClient" placeholder="Hal: Aling Nena"></div>
 <h3 style="margin-top:6px">Mga Item</h3>
 <div id="ivItems"></div>
 <div class="row">
  <div class="field"><label>Item</label><input id="ivName" placeholder="Hal: Sabon"></div>
  <div class="field"><label>Presyo</label><input id="ivPrice" type="number" inputmode="decimal" placeholder="50"></div>
  <div class="field"><label>Qty</label><input id="ivQty" type="number" inputmode="decimal" value="1"></div>
 </div>
 <button class="btn ghost" onclick="ivAddItem()">\u2795 Add Item</button>
 <div class="field" style="margin-top:12px"><label>Fixed Fees (opsyonal)</label><input id="ivFee" type="number" inputmode="decimal" value="0"></div>
 <button class="btn" onclick="ivGen()">Generate Invoice</button>
 <div id="ivErr"></div>
</div>
""",
result=r"""
<div class="card">
 <div class="kv"><span>Client</span><b id="ivRClient">&mdash;</b></div>
 <div id="ivRItems"></div>
 <div class="kv"><span>Subtotal</span><b id="ivRSub">&mdash;</b></div>
 <div class="kv"><span>Fees</span><b id="ivRFee">&mdash;</b></div>
 <div class="kv"><span><b>TOTAL</b></span><b class="big" id="ivRTotal">&mdash;</b></div>
 <button class="btn ok" onclick="ivDone()">\U0001F5A8\uFE0F Invoice Generated</button>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F9FE</div>
 <h2>Invoice Generated</h2>
 <div class="mut small" id="ivDMsg">Ready to print</div>
 <div id="ivDList" style="text-align:left;margin-top:10px"></div>
 <button class="btn ghost" onclick="ivNew()">\u2795 Bagong Invoice</button>
</div>
""",
js=r"""
var ivItems=[],ivCur=null;
function ivRenderItems(){
  $('#ivCount').textContent=ivItems.length;
  var el=$('#ivItems');
  if(!ivItems.length){el.innerHTML='<div class="mut small">Wala pang item.</div>';return;}
  el.innerHTML=ivItems.map(function(it,i){
    return '<div class="item"><div class="ic">\U0001F4E6</div><div class="grow"><div class="t">'+it.qty+'x '+it.name+'</div><div class="s">'+money(it.price)+' bawat isa</div></div><span class="pill pri">'+money(it.qty*it.price)+'</span><button class="btn sm bad" onclick="ivDel('+i+')">\u2716</button></div>';
  }).join('');
}
function ivAddItem(){
  var name=val('ivName'),price=num('ivPrice'),qty=num('ivQty');
  if(!name||isNaN(price)){$('#ivErr').innerHTML='<div class="alert err">Ilagay item at presyo</div>';return;}
  if(isNaN(qty)||qty<=0)qty=1;
  $('#ivErr').innerHTML='';ivItems.push({name:name,price:price,qty:qty});
  resetForm(['ivName','ivPrice']);$('#ivQty').value=1;ivRenderItems();
}
function ivDel(i){ivItems.splice(i,1);ivRenderItems();}
function ivGen(){
  var client=val('ivClient'),fee=num('ivFee');
  if(!ivItems.length){$('#ivErr').innerHTML='<div class="alert err">Add at least 1 item</div>';return;}
  $('#ivErr').innerHTML='';if(isNaN(fee))fee=0;
  var sub=ivItems.reduce(function(a,b){return a+b.price*b.qty;},0);
  ivCur={client:client||'Walk-in',items:ivItems.slice(),sub:sub,fee:fee,total:sub+fee};
  $('#ivRClient').textContent=ivCur.client;
  $('#ivRItems').innerHTML=ivCur.items.map(function(it){return '<div class="kv"><span>'+it.qty+'x '+it.name+'</span><b>'+money(it.qty*it.price)+'</b></div>';}).join('');
  $('#ivRSub').textContent=money(sub);$('#ivRFee').textContent=money(fee);$('#ivRTotal').textContent=money(ivCur.total);
  show('result');
}
function ivDone(){
  if(!ivCur)return;
  $('#ivDMsg').textContent='Client: '+ivCur.client+' \u2022 Total: '+money(ivCur.total);
  $('#ivDList').innerHTML=ivCur.items.map(function(it){return '<div class="kv"><span>'+it.qty+'x '+it.name+'</span><b>'+money(it.qty*it.price)+'</b></div>';}).join('')+'<div class="kv"><span>TOTAL</span><b>'+money(ivCur.total)+'</b></div>';
  toast('Invoice ready');show('done');
}
function ivNew(){ivItems=[];ivRenderItems();resetForm(['ivClient','ivName','ivPrice','ivFee']);$('#ivQty').value=1;show('input');}
ivRenderItems();
""")

# ---------------- APP 11: Loan / Utang Tracker PRO ----------------
define(name="Loan / Utang Tracker PRO", icon="\U0001F4B8", tag="Balance = Principal - Paid",
home=r"""
<div class="hero"><div class="mut small">Total Receivables</div><div class="big" id="lTotal">\u20B10</div><div class="mut small" id="lSub">Walang utang</div></div>
<button class="btn" data-go="input">\u2795 Magdagdag ng Utang</button>
<h3>Mga Utang</h3><div id="lList"></div>
""",
input=r"""
<div class="card">
 <div class="field"><label>Pangalan ng Nangutang</label><input id="lName" placeholder="Hal: Juan"></div>
 <div class="field"><label>Halaga</label><input id="lAmt" type="number" inputmode="decimal" placeholder="500"></div>
 <button class="btn" onclick="lAdd()">Idagdag</button>
 <div id="lErr"></div>
</div>
""",
result=r"""
<div class="card">
 <div class="kv"><span>Nangutang</span><b id="lRName">&mdash;</b></div>
 <div class="kv"><span>Principal</span><b id="lRPrin">&mdash;</b></div>
 <div class="kv"><span>Bayad na</span><b id="lRPaid">&mdash;</b></div>
 <div class="kv"><span><b>BALANCE</b></span><b class="big" id="lRBal">&mdash;</b></div>
 <div class="field"><label>Record Payment</label><input id="lPay" type="number" inputmode="decimal" placeholder="Hal: 200"></div>
 <button class="btn ok" onclick="lPayNow()">\U0001F4B5 Record Payment</button>
 <div id="lPayErr"></div>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F4B8</div>
 <h2 id="lDTitle">Payment Received</h2>
 <div class="mut small" id="lDMsg">Bayad na</div>
 <button class="btn ghost" onclick="lNew()">\u2795 Bagong Utang</button>
</div>
""",
js=r"""
var L_KEY='mcsn_utang';var lData=Store.get(L_KEY,[]);var lCur=null;
function lSave(){Store.set(L_KEY,lData);}
function lRender(){
  var tot=lData.reduce(function(a,b){return a+(b.principal-b.paid);},0);
  $('#lTotal').textContent=money(tot);
  $('#lSub').textContent=lData.length?(lData.length+' record(s)'):'Walang utang';
  var el=$('#lList');
  if(!lData.length){el.innerHTML='<div class="mut small">Wala pang utang.</div>';return;}
  el.innerHTML=lData.slice().reverse().map(function(b){
    var bal=b.principal-b.paid;var cl=bal<=0?'ok':'warn';
    return '<div class="item"><div class="ic">\U0001F4B8</div><div class="grow"><div class="t">'+b.name+'</div><div class="s">Principal '+money(b.principal)+' \u2022 Bayad '+money(b.paid)+'</div></div><span class="pill '+cl+'">'+(bal<=0?'Cleared':money(bal))+'</span></div>';
  }).join('');
}
function lAdd(){
  var name=val('lName'),amt=num('lAmt');
  if(!name||isNaN(amt)||amt<=0){$('#lErr').innerHTML='<div class="alert err">Punan pangalan at halaga</div>';return;}
  $('#lErr').innerHTML='';
  lCur={name:name,principal:amt,paid:0};lData.push(lCur);lSave();lRender();lFill();show('result');
}
function lFill(){
  if(!lCur)return;
  $('#lRName').textContent=lCur.name;$('#lRPrin').textContent=money(lCur.principal);
  $('#lRPaid').textContent=money(lCur.paid);$('#lRBal').textContent=money(lCur.principal-lCur.paid);
}
function lPayNow(){
  if(!lCur)return;var p=num('lPay');
  if(isNaN(p)||p<=0){$('#lPayErr').innerHTML='<div class="alert err">Ilagay bayad</div>';return;}
  var bal=lCur.principal-lCur.paid;
  if(p>bal){$('#lPayErr').innerHTML='<div class="alert err">Overpayment</div>';return;}
  $('#lPayErr').innerHTML='';lCur.paid+=p;lSave();lFill();lRender();
  var cleared=(lCur.principal-lCur.paid)<=0;
  $('#lDTitle').textContent=cleared?'Cleared':'Payment Received';
  $('#lDMsg').textContent=lCur.name+' \u2014 bayad '+money(p)+' \u2022 Balanse '+money(lCur.principal-lCur.paid);
  toast('Payment recorded');show('done');
}
function lNew(){resetForm(['lName','lAmt','lPay']);show('input');}
lRender();
""")

# ---------------- APP 12: Savings Goal Tracker PRO ----------------
define(name="Savings Goal Tracker PRO", icon="\U0001F3AF", tag="Progress % = Saved / Goal",
home=r"""
<div class="hero"><div class="mut small">Goal</div><div class="big" id="svGoalName">&mdash;</div><div class="mut small" id="svSub">Wala pang goal</div></div>
<button class="btn" data-go="input">\U0001F3AF Mag-set ng Goal</button>
<div id="svHomeBar"></div>
""",
input=r"""
<div class="card">
 <div class="field"><label>Pangalan ng Goal</label><input id="svName" placeholder="Hal: Bike"></div>
 <div class="field"><label>Target Amount</label><input id="svTarget" type="number" inputmode="decimal" placeholder="5000"></div>
 <div class="field"><label>Naka-save Na</label><input id="svSaved" type="number" inputmode="decimal" placeholder="2000"></div>
 <button class="btn" onclick="svCalc()">Kalkulahin</button>
 <div id="svErr"></div>
</div>
""",
result=r"""
<div class="card">
 <div class="hero"><div class="mut small">Progress</div><div class="big" id="svPct">&mdash;</div><div class="mut small" id="svToGo">&mdash;</div></div>
 <div class="bar"><i id="svBar" style="width:0%"></i></div>
 <div class="kv" style="margin-top:10px"><span>Target</span><b id="svRTarget">&mdash;</b></div>
 <div class="kv"><span>Naka-save</span><b id="svRSaved">&mdash;</b></div>
 <button class="btn ok" onclick="svDone()">\u2705 I-save ang Goal</button>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px" id="svEmoji">\U0001F3AF</div>
 <h2 id="svDTitle">Goal Saved</h2>
 <div class="mut small" id="svDMsg">Naka-save na</div>
 <button class="btn ghost" onclick="svNew()">\u2795 Bagong Goal</button>
</div>
""",
js=r"""
var SV_KEY='mcsn_savings';var svData=Store.get(SV_KEY,null);var svCur=null;
function svRender(){
  if(!svData){$('#svHomeBar').innerHTML='';return;}
  var pct=Math.min(100,(svData.saved/svData.target)*100);
  $('#svGoalName').textContent=svData.name;
  $('#svSub').textContent=money(svData.saved)+' / '+money(svData.target)+' ('+pct.toFixed(0)+'%)';
  $('#svHomeBar').innerHTML='<div class="bar" style="margin-top:10px"><i style="width:'+pct+'%"></i></div>';
}
function svCalc(){
  var name=val('svName'),target=num('svTarget'),saved=num('svSaved');
  if(!name||isNaN(target)){$('#svErr').innerHTML='<div class="alert err">Punan lahat</div>';return;}
  if(target<=0){$('#svErr').innerHTML='<div class="alert err">Target must be > 0</div>';return;}
  if(isNaN(saved))saved=0;
  $('#svErr').innerHTML='';
  var pct=(saved/target)*100;
  svCur={name:name,target:target,saved:saved,pct:pct};
  $('#svPct').textContent=pct.toFixed(1)+'%';
  $('#svToGo').textContent=(saved>=target)?'Goal reached!':(money(target-saved)+' to go');
  $('#svBar').style.width=Math.min(100,pct)+'%';
  $('#svRTarget').textContent=money(target);$('#svRSaved').textContent=money(saved);
  show('result');
}
function svDone(){
  if(!svCur)return;svData=svCur;Store.set(SV_KEY,svData);svRender();
  var reached=svCur.saved>=svCur.target;
  $('#svEmoji').textContent=reached?'\U0001F389':'\U0001F3AF';
  $('#svDTitle').textContent=reached?'Goal Reached! \U0001F389':'Goal Saved';
  $('#svDMsg').textContent=svCur.name+' \u2022 '+svCur.pct.toFixed(1)+'% ('+money(svCur.saved)+' / '+money(svCur.target)+')';
  toast('Goal saved');show('done');
}
function svNew(){resetForm(['svName','svTarget','svSaved']);show('input');}
svRender();
""")

# ---------------- APP 13: Daily Habit Tracker PRO ----------------
define(name="Daily Habit Tracker PRO", icon="\U0001F4AA", tag="Streak = sunod-sunod na araw",
home=r"""
<div class="hero"><div class="mut small">Habits ngayon</div><div class="big" id="hToday">0</div><div class="mut small" id="hSub">Wala pang habit</div></div>
<button class="btn" data-go="input">\u2795 Magdagdag ng Habit</button>
<h3>Mga Habit</h3><div id="hList"></div>
""",
input=r"""
<div class="card">
 <div class="field"><label>Pangalan ng Habit</label><input id="hName" placeholder="Hal: Drink Water"></div>
 <button class="btn" onclick="hAdd()">Idagdag</button>
 <div id="hErr"></div>
</div>
""",
result=r"""
<div class="card">
 <div class="hero"><div class="mut small">Streak</div><div class="big" id="hStreak">0</div><div class="mut small" id="hTotal">Total: 0</div></div>
 <div class="kv"><span>Habit</span><b id="hRName">&mdash;</b></div>
 <button class="btn ok" onclick="hCheck()">\u2705 Check Today</button>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F4AA</div>
 <h2>Habit Completed</h2>
 <div class="mut small" id="hDMsg">Nice work!</div>
 <button class="btn ghost" onclick="hNew()">\u2795 Bagong Habit</button>
</div>
""",
js=r"""
var H_KEY='mcsn_habits';var hData=Store.get(H_KEY,[]);var hCur=null;
function hTodayStr(){return new Date().toISOString().slice(0,10);}
function hSave(){Store.set(H_KEY,hData);}
function hStreak(dates){
  if(!dates||!dates.length)return 0;
  var set={};dates.forEach(function(d){set[d]=1;});
  var n=0,cur=new Date();
  for(var i=0;i<400;i++){
    var k=cur.toISOString().slice(0,10);
    if(set[k]){n++;cur.setDate(cur.getDate()-1);}else break;
  }
  return n;
}
function hRender(){
  var today=hTodayStr();
  var done=hData.filter(function(h){return h.dates.indexOf(today)>=0;}).length;
  $('#hToday').textContent=done+'/'+hData.length;
  $('#hSub').textContent=hData.length?(done+' tapos na ngayon'):'Wala pang habit';
  var el=$('#hList');
  if(!hData.length){el.innerHTML='<div class="mut small">Wala pang habit. Magdagdag.</div>';return;}
  el.innerHTML=hData.map(function(h,i){
    var on=h.dates.indexOf(today)>=0;
    return '<div class="chk '+(on?'on':'')+'" onclick="hToggle('+i+')"><div class="box">'+(on?'\u2714':'')+'</div><div class="grow"><div class="t">'+h.name+'</div><div class="s">Streak: '+hStreak(h.dates)+' araw</div></div></div>';
  }).join('');
}
function hAdd(){
  var name=val('hName');
  if(!name){$('#hErr').innerHTML='<div class="alert err">Ilagay pangalan</div>';return;}
  $('#hErr').innerHTML='';
  hData.push({name:name,dates:[]});hSave();hRender();resetForm(['hName']);toast('Habit added');
}
function hToggle(i){
  var today=hTodayStr();var h=hData[i];
  var idx=h.dates.indexOf(today);
  if(idx>=0)h.dates.splice(idx,1);else h.dates.push(today);
  hSave();hRender();
}
function hCheck(){
  if(!hCur)return;var today=hTodayStr();
  if(hCur.dates.indexOf(today)<0)hCur.dates.push(today);
  hSave();hRender();
  $('#hStreak').textContent=hStreak(hCur.dates);
  $('#hTotal').textContent='Total: '+hCur.dates.length+' araw';
  toast('Checked today');show('done');
}
function hNew(){resetForm(['hName']);show('input');}
hRender();
""")

# ---------------- APP 14: Ebook Budget 101 ----------------
define(name="Ebook Budget 101", icon="\U0001F4D8", tag="50 / 30 / 20 Rule",
home=r"""
<div class="hero"><div class="mut small">Rule</div><div class="big">50/30/20</div><div class="mut small">Needs 50% \u2022 Wants 30% \u2022 Savings 20%</div></div>
<button class="btn" data-go="input">\U0001F4D8 Gumawa ng Budget Plan</button>
<div id="bdHome"></div>
""",
input=r"""
<div class="card">
 <div class="field"><label>Buwanang Kita (Income)</label><input id="bdIncome" type="number" inputmode="decimal" placeholder="10000"></div>
 <button class="btn" onclick="bdCalc()">Kalkulahin ang 50/30/20</button>
 <div id="bdErr"></div>
</div>
""",
result=r"""
<div class="card">
 <div class="kv"><span>\U0001F3E0 Needs (50%)</span><b id="bdNeeds">&mdash;</b></div>
 <div class="kv"><span>\U0001F389 Wants (30%)</span><b id="bdWants">&mdash;</b></div>
 <div class="kv"><span>\U0001F4B0 Savings (20%)</span><b id="bdSave">&mdash;</b></div>
 <div class="bar" style="margin-top:12px"><i id="bdBar" style="width:100%"></i></div>
 <button class="btn ok" onclick="bdDone()">\U0001F4BE I-save ang Plan</button>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F4D8</div>
 <h2>Budget Plan Saved</h2>
 <div class="mut small" id="bdDMsg">Naka-save na</div>
 <button class="btn ghost" onclick="bdNew()">\u2795 Bagong Plan</button>
</div>
""",
js=r"""
var BD_KEY='mcsn_budget';var bdData=Store.get(BD_KEY,null);var bdCur=null;
function bdRender(){
  if(!bdData){$('#bdHome').innerHTML='';return;}
  $('#bdHome').innerHTML='<div class="card tight" style="margin-top:12px"><div class="kv"><span>Kita</span><b>'+money(bdData.income)+'</b></div><div class="kv"><span>Needs/Wants/Save</span><b>'+money(bdData.needs)+' / '+money(bdData.wants)+' / '+money(bdData.save)+'</b></div></div>';
}
function bdCalc(){
  var inc=num('bdIncome');
  if(isNaN(inc)||inc<=0){$('#bdErr').innerHTML='<div class="alert err">Enter valid income</div>';return;}
  $('#bdErr').innerHTML='';
  bdCur={income:inc,needs:inc*0.5,wants:inc*0.3,save:inc*0.2};
  $('#bdNeeds').textContent=money(bdCur.needs);
  $('#bdWants').textContent=money(bdCur.wants);
  $('#bdSave').textContent=money(bdCur.save);
  show('result');
}
function bdDone(){
  if(!bdCur)return;bdData=bdCur;Store.set(BD_KEY,bdData);bdRender();
  $('#bdDMsg').textContent='Kita '+money(bdCur.income)+' \u2022 Needs '+money(bdCur.needs)+' \u2022 Wants '+money(bdCur.wants)+' \u2022 Savings '+money(bdCur.save);
  toast('Budget plan saved');show('done');
}
function bdNew(){resetForm(['bdIncome']);show('input');}
bdRender();
""")

# ---------------- APP 15: DIY Phone Repair Checklist ----------------
define(name="DIY Phone Repair Checklist", icon="\U0001F527", tag="Progress = Checked / Total",
home=r"""
<div class="hero"><div class="mut small">Title</div><div class="big">Replace Screen</div><div class="mut small" id="drSub">5 steps</div></div>
<button class="btn" data-go="input">\U0001F527 Simulan ang Checklist</button>
<div id="drList"></div>
""",
input=r"""
<div class="card">
 <div class="field"><label>Title</label><input id="drTitle" value="Replace Screen"></div>
 <div class="field"><label>Mga Steps (isang linya bawat step)</label><textarea id="drSteps" rows="5">Remove screws
Disconnect battery
Remove old screen
Install new screen
Test and reassemble</textarea></div>
 <button class="btn" onclick="drLoad()">Load Steps</button>
 <div id="drErr"></div>
</div>
""",
result=r"""
<div class="card">
 <div class="hero"><div class="mut small">Progress</div><div class="big" id="drPct">0%</div><div class="mut small" id="drFrac">0/0 steps</div></div>
 <div class="bar"><i id="drBar" style="width:0%"></i></div>
 <div id="drResultList" style="margin-top:12px"></div>
 <button class="btn ok" onclick="drFinish()">\u2705 Finish</button>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F527</div>
 <h2 id="drDTitle">Repair Complete!</h2>
 <div class="mut small" id="drDMsg">Tapos na lahat</div>
 <button class="btn ghost" onclick="drNew()">\u2795 Bagong Checklist</button>
</div>
""",
js=r"""
var drStepsArr=[],drDone=[];var drTitleTxt='Replace Screen';
function drRender(){
  $('#drSub').textContent=drStepsArr.length+' steps';
  var el=$('#drList');
  if(!drStepsArr.length){el.innerHTML='';return;}
  el.innerHTML=drStepsArr.map(function(s,i){
    var on=drDone[i];
    return '<div class="chk '+(on?'on':'')+'" onclick="drToggle('+i+')"><div class="box">'+(on?'\u2714':'')+'</div><div class="grow"><div class="t">'+s+'</div></div></div>';
  }).join('');
}
function drToggle(i){drDone[i]=!drDone[i];drRender();if($('#drResultList'))drResult();}
function drLoad(){
  var t=val('drTitle')||'Checklist';
  var raw=$('#drSteps').value.split('\n').map(function(s){return s.trim();}).filter(function(s){return s;});
  if(!raw.length){$('#drErr').innerHTML='<div class="alert err">Maglagay ng steps</div>';return;}
  $('#drErr').innerHTML='';
  drTitleTxt=t;drStepsArr=raw;drDone=raw.map(function(){return false;});
  drRender();drResult();show('result');
}
function drResult(){
  var c=drDone.filter(Boolean).length,tot=drStepsArr.length;
  var pct=tot?Math.round(c/tot*100):0;
  $('#drPct').textContent=pct+'%';$('#drFrac').textContent=c+'/'+tot+' steps';
  $('#drBar').style.width=pct+'%';
  $('#drResultList').innerHTML=drStepsArr.map(function(s,i){
    return '<div class="kv"><span>'+s+'</span><b>'+(drDone[i]?'\u2714':'\u25CB')+'</b></div>';
  }).join('');
}
function drFinish(){
  var c=drDone.filter(Boolean).length,tot=drStepsArr.length;
  $('#drDTitle').textContent=(c===tot&&tot>0)?'Repair Complete!':'Progress: '+c+'/'+tot;
  $('#drDMsg').textContent=drTitleTxt+' \u2022 '+(tot?Math.round(c/tot*100):0)+'% tapos';
  toast('Checklist saved');show('done');
}
function drNew(){show('input');}
""")

# ---------------- APP 16: DIY Furniture Assembly ----------------
define(name="DIY Furniture Assembly", icon="\U0001FA91", tag="Progress = Checked / Total",
home=r"""
<div class="hero"><div class="mut small">Title</div><div class="big">Assemble Table</div><div class="mut small" id="dfSub">3 steps</div></div>
<button class="btn" data-go="input">\U0001FA91 Simulan ang Assembly</button>
<div id="dfList"></div>
""",
input=r"""
<div class="card">
 <div class="field"><label>Title</label><input id="dfTitle" value="Assemble Table"></div>
 <div class="field"><label>Mga Step (isang linya bawat step)</label><textarea id="dfSteps" rows="4">Step A: Attach legs
Step B: Fix tabletop
Step C: Tighten all screws</textarea></div>
 <button class="btn" onclick="dfLoad()">Load Manual</button>
 <div id="dfErr"></div>
</div>
""",
result=r"""
<div class="card">
 <div class="hero"><div class="mut small">Progress</div><div class="big" id="dfPct">0%</div><div class="mut small" id="dfFrac">0/0 steps</div></div>
 <div class="bar"><i id="dfBar" style="width:0%"></i></div>
 <div id="dfResultList" style="margin-top:12px"></div>
 <button class="btn ok" onclick="dfFinish()">\u2705 Finish</button>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001FA91</div>
 <h2 id="dfDTitle">Assembly Done</h2>
 <div class="mut small" id="dfDMsg">Tapos na lahat</div>
 <button class="btn ghost" onclick="dfNew()">\u2795 Bagong Manual</button>
</div>
""",
js=r"""
var dfStepsArr=[],dfDone=[];var dfTitleTxt='Assemble Table';
function dfRender(){
  $('#dfSub').textContent=dfStepsArr.length+' steps';
  var el=$('#dfList');
  if(!dfStepsArr.length){el.innerHTML='';return;}
  el.innerHTML=dfStepsArr.map(function(s,i){
    var on=dfDone[i];
    return '<div class="chk '+(on?'on':'')+'" onclick="dfToggle('+i+')"><div class="box">'+(on?'\u2714':'')+'</div><div class="grow"><div class="t">'+s+'</div></div></div>';
  }).join('');
}
function dfToggle(i){dfDone[i]=!dfDone[i];dfRender();if($('#dfResultList'))dfResult();}
function dfLoad(){
  var t=val('dfTitle')||'Assembly';
  var raw=$('#dfSteps').value.split('\n').map(function(s){return s.trim();}).filter(function(s){return s;});
  if(!raw.length){$('#dfErr').innerHTML='<div class="alert err">Invalid input</div>';return;}
  $('#dfErr').innerHTML='';
  dfTitleTxt=t;dfStepsArr=raw;dfDone=raw.map(function(){return false;});
  dfRender();dfResult();show('result');
}
function dfResult(){
  var c=dfDone.filter(Boolean).length,tot=dfStepsArr.length;
  var pct=tot?Math.round(c/tot*100):0;
  $('#dfPct').textContent=pct+'%';$('#dfFrac').textContent=c+'/'+tot+' steps';
  $('#dfBar').style.width=pct+'%';
  $('#dfResultList').innerHTML=dfStepsArr.map(function(s,i){
    return '<div class="kv"><span>'+s+'</span><b>'+(dfDone[i]?'\u2714':'\u25CB')+'</b></div>';
  }).join('');
}
function dfFinish(){
  var c=dfDone.filter(Boolean).length,tot=dfStepsArr.length;
  $('#dfDTitle').textContent=(c===tot&&tot>0)?'Assembly Done':'Progress: '+c+'/'+tot;
  $('#dfDMsg').textContent=dfTitleTxt+' \u2022 '+(tot?Math.round(c/tot*100):0)+'% tapos';
  toast('Assembly saved');show('done');
}
function dfNew(){show('input');}
""")

# ---------------- APP 17: DIY School Project Ideas ----------------
define(name="DIY School Project Ideas", icon="\U0001F4A1", tag="Randomize by category",
home=r"""
<div class="hero"><div class="mut small">Categories</div><div class="big">3</div><div class="mut small">Science \u2022 Art \u2022 Math</div></div>
<button class="btn" data-go="input">\U0001F4A1 Generate Idea</button>
<h3>Mga Naka-save</h3><div id="diList"></div>
""",
input=r"""
<div class="card">
 <h3 style="margin-top:0">Pumili ng Kategorya</h3>
 <div class="chips" id="diCats">
  <div class="chip" data-cat="Science" onclick="diPick(this)">\U0001F52C Science</div>
  <div class="chip" data-cat="Art" onclick="diPick(this)">\U0001F3A8 Art</div>
  <div class="chip" data-cat="Math" onclick="diPick(this)">\U0001F522 Math</div>
 </div>
 <button class="btn" style="margin-top:14px" onclick="diGen()">Generate Idea</button>
 <div id="diErr"></div>
</div>
""",
result=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F4A1</div>
 <div class="big" id="diRIdea">&mdash;</div>
 <div class="mut small" id="diRCat">&mdash;</div>
 <button class="btn ok" onclick="diSave()">\U0001F4BE I-save ang Idea</button>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F4A1</div>
 <h2>Idea Saved</h2>
 <div class="mut small" id="diDMsg">Naka-save na</div>
 <button class="btn ghost" onclick="diNew()">\u2795 Bagong Idea</button>
</div>
""",
js=r"""
var IDEAS={
 Science:['Volcano Eruption','Water Filtration Model','Solar System Diorama','Plant Growth Experiment','Simple Electric Circuit'],
 Art:['Recycled Bottle Art','Paper Mache Mask','Handmade Poster','Origami Mobile','Nature Collage'],
 Math:['Geometry Shape Model','Multiplication Board Game','Fraction Pizza','Measurement Chart','Abacus from Beads']
};
var DI_KEY='mcsn_ideas';var diData=Store.get(DI_KEY,[]);var diCur=null,diCat=null;
function diRender(){
  var el=$('#diList');
  if(!diData.length){el.innerHTML='<div class="mut small">Wala pang idea.</div>';return;}
  el.innerHTML=diData.slice().reverse().map(function(c){
    return '<div class="item"><div class="ic">\U0001F4A1</div><div class="grow"><div class="t">'+c.idea+'</div><div class="s">'+c.cat+'</div></div></div>';
  }).join('');
}
function diPick(el){
  diCat=el.dataset.cat;
  $$('#diCats .chip').forEach(function(c){c.classList.remove('on');});
  el.classList.add('on');
}
function diGen(){
  if(!diCat){$('#diErr').innerHTML='<div class="alert err">Select category</div>';return;}
  $('#diErr').innerHTML='';
  var arr=IDEAS[diCat],idea=arr[Math.floor(Math.random()*arr.length)];
  diCur={idea:idea,cat:diCat};
  $('#diRIdea').textContent=idea;$('#diRCat').textContent=diCat+' project';
  show('result');
}
function diSave(){if(!diCur)return;diData.push(diCur);Store.set(DI_KEY,diData);diRender();
  $('#diDMsg').textContent=diCur.idea+' \u2022 '+diCur.cat;toast('Idea saved');show('done');}
function diNew(){diCat=null;$$('#diCats .chip').forEach(function(c){c.classList.remove('on');});show('input');}
diRender();
""")

# ---------------- GEMINI BATCH: 14 Pinoy Everyday PRO Utility Apps ----------------
define(name="Community Pantry Tracker PRO", icon="\U0001F958", tag="Stocks In - Out = Natitira", batch="Gemini",
home=r"""
<div class="hero"><div class="mut small">Kabuuang Stock</div><div class="big" id="pTot">0</div><div class="mut small">Community Pantry Inventory</div></div>
<button class="btn" data-go="input">\u2795 Log ng Donasyon / Kinuha</button>
<h3>Kasalukuyang Stocks</h3><div id="pList"></div>
""",
input=r"""
<div class="card">
 <div class="field"><label>Item</label>
  <select id="pItem"><option>Bigas</option><option>Delata</option><option>Gulay</option><option>Noodles</option></select></div>
 <div class="field"><label>Aksyon</label>
  <select id="pAct"><option value="in">Dating Donasyon (+)</option><option value="out">Kinuha ng Residente (-)</option></select></div>
 <div class="field"><label>Dami</label><input id="pQty" type="number" placeholder="Hal: 10"></div>
 <button class="btn" onclick="pLog()">I-log</button>
 <div id="pErr"></div>
</div>
""",
result=r"""
<div class="card">
 <h3 style="margin-top:0">Summary Ngayong Araw</h3>
 <div id="pSum"></div>
</div>
<div class="card">
 <h3 style="margin-top:0">Kailangang I-restock</h3>
 <div id="pRestock"></div>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F4CB</div>
 <h2>Daily Pantry Report</h2>
 <div id="pReport"></div>
 <button class="btn ghost" onclick="show('input')">\u2795 Bagong Log</button>
</div>
""",
js=r"""
var P_KEY='mcsn_pantry';var pData=Store.get(P_KEY,{Bigas:40,Delata:25,Gulay:15,Noodles:30});
function pSave(){Store.set(P_KEY,pData);}
function pRender(){
  var tot=0;Object.keys(pData).forEach(function(k){tot+=pData[k];});
  $('#pTot').textContent=tot;
  $('#pList').innerHTML=Object.keys(pData).map(function(k){
    var v=pData[k];var cls=v>20?'ok':(v>=10?'warn':'bad');
    var ic=k==='Bigas'?'\U0001F35A':(k==='Delata'?'\U0001F96B':(k==='Gulay'?'\U0001F966':'\U0001F35C'));
    return '<div class="item"><div class="ic">'+ic+'</div><div class="grow"><div class="t">'+k+'</div><div class="s">Natitira: '+v+'</div></div><span class="pill '+cls+'">'+v+'</span></div>';
  }).join('');
}
function pLog(){
  var it=$('#pItem').value,act=$('#pAct').value,q=parseInt(val('pQty'),10);
  if(isNaN(q)||q<=0){$('#pErr').innerHTML='<div class="alert err">Ilagay ang tamang dami</div>';return;}
  $('#pErr').innerHTML='';
  pData[it]=Math.max(0,(pData[it]||0)+(act==='in'?q:-q));pSave();pRender();
  $('#pSum').innerHTML=Object.keys(pData).map(function(k){return '<div class="kv"><span>'+k+'</span><b>'+pData[k]+'</b></div>';}).join('');
  var low=Object.keys(pData).filter(function(k){return pData[k]<10;});
  $('#pRestock').innerHTML=low.length?low.map(function(k){return '<div class="item"><div class="ic">\u26A0\uFE0F</div><div class="grow"><div class="t">'+k+'</div><div class="s">Kulang na, i-restock bukas</div></div></div>';}).join(''):'<div class="mut small">Wala pang kailangang i-restock.</div>';
  $('#pReport').innerHTML=Object.keys(pData).map(function(k){return '<div class="kv"><span>'+k+'</span><b>'+pData[k]+'</b></div>';}).join('');
  toast(it+' '+(act==='in'?'nadagdag':'nabawasan'));show('result');
}
pRender();
""")

define(name="Ulam Planner 7 Days PRO", icon="\U0001F373", tag="Menu -> Grocery List", batch="Gemini",
home=r"""
<div class="hero"><div class="mut small">Lunes \u2013 Linggo</div><div class="big" id="uCount">0/7</div><div class="mut small">Napiling ulam sa linggo</div></div>
<button class="btn" data-go="input">\U0001F373 Pumili ng Ulam</button>
<h3>Weekly Meal Board</h3><div id="uBoard"></div>
""",
input=r"""
<div class="card">
 <div class="field"><label>Araw</label>
  <select id="uDay"><option>Lunes</option><option>Martes</option><option>Miyerkules</option><option>Huwebes</option><option>Biyernes</option><option>Sabado</option><option>Linggo</option></select></div>
 <div class="field"><label>Ulam</label>
  <select id="uDish"><option>Adobo</option><option>Sinigang</option><option>Tinola</option><option>Ginisang Monggo</option><option>Menudo</option><option>Paksiw</option></select></div>
 <button class="btn" onclick="uPick()">I-set sa Araw</button>
 <div id="uErr"></div>
</div>
""",
result=r"""
<div class="card">
 <h3 style="margin-top:0">Grocery / Palengke List</h3>
 <div id="uGrocery"></div>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F4C5</div>
 <h2>Weekly Menu Saved</h2>
 <div id="uMenu"></div>
 <button class="btn ghost" onclick="show('input')">\u270F\uFE0F Baguhin</button>
</div>
""",
js=r"""
var U_DAYS=['Lunes','Martes','Miyerkules','Huwebes','Biyernes','Sabado','Linggo'];
var U_ING={Adobo:['Manok','Toyo','Suka','Bawang'],Sinigang:['Baboy','Sampalok','Kangkong','Kamatis'],Tinola:['Manok','Papaya','Malunggay','Luya'],'Ginisang Monggo':['Monggo','Hipon','Malunggay','Bawang'],Menudo:['Baboy','Patatas','Karot','Toyo'],Paksiw:['Isda','Suka','Luya','Sili']};
var U_KEY='mcsn_ulam';var uData=Store.get(U_KEY,{});
function uSave(){Store.set(U_KEY,uData);}
function uRender(){
  var n=U_DAYS.filter(function(d){return uData[d];}).length;
  $('#uCount').textContent=n+'/7';
  $('#uBoard').innerHTML=U_DAYS.map(function(d){
    return '<div class="item"><div class="ic">\U0001F373</div><div class="grow"><div class="t">'+d+'</div><div class="s">'+(uData[d]||'Wala pang ulam')+'</div></div></div>';
  }).join('');
}
function uPick(){
  var d=$('#uDay').value,dish=$('#uDish').value;
  uData[d]=dish;uSave();uRender();
  var need={};U_DAYS.forEach(function(day){if(uData[day])U_ING[uData[day]].forEach(function(i){need[i]=1;});});
  $('#uGrocery').innerHTML=Object.keys(need).map(function(i){return '<div class="item"><div class="ic">\U0001F6D2</div><div class="grow"><div class="t">'+i+'</div></div></div>';}).join('');
  $('#uMenu').innerHTML=U_DAYS.map(function(day){return '<div class="kv"><span>'+day+'</span><b>'+(uData[day]||'\u2014')+'</b></div>';}).join('');
  toast(d+': '+dish);show('result');
}
uRender();
""")

define(name="Grocery List + Budget PRO", icon="\U0001F6D2", tag="Budget - Gastos = Natitira", batch="Gemini",
home=r"""
<div class="hero"><div class="mut small">Total Budget</div><div class="big" id="gBud">\u20B10</div><div class="mut small" id="gSub">Walang budget na naka-set</div></div>
<div class="card tight">
 <div class="field" style="margin:0"><label>Itakda ang Budget</label><input id="gBudget" type="number" placeholder="Hal: 2000"></div>
 <button class="btn sm" onclick="gSet()" style="width:100%;margin-top:8px">I-save ang Budget</button>
</div>
<button class="btn" data-go="input">\u2795 Magdagdag ng Bilihin</button>
""",
input=r"""
<div class="card">
 <div class="field"><label>Item</label><input id="gItem" placeholder="Hal: Bigas"></div>
 <div class="field"><label>Kategorya</label><select id="gCat"><option>Karne</option><option>Gulay</option><option>Pampalasa</option><option>Iba pa</option></select></div>
 <div class="field"><label>Presyo</label><input id="gPrice" type="number" placeholder="Hal: 250"></div>
 <button class="btn" onclick="gAdd()">Idagdag sa Cart</button>
 <div id="gErr"></div>
</div>
""",
result=r"""
<div class="card">
 <div class="kv"><span>Nagastos Na</span><b id="gSpent">\u20B10</b></div>
 <div class="kv"><span>Natitirang Budget</span><b id="gLeft">\u20B10</b></div>
 <div class="bar" style="margin-top:10px"><i id="gBar" style="width:0%"></i></div>
 <div id="gWarn"></div>
</div>
<div class="card"><h3 style="margin-top:0">Mga Bilihin</h3><div id="gItems"></div></div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F9FE</div>
 <h2>Digital Receipt</h2>
 <div id="gReceipt"></div>
 <button class="btn ghost" onclick="show('input')">\u2795 Dagdag Pa</button>
</div>
""",
js=r"""
var G_KEY='mcsn_grocery';var gData=Store.get(G_KEY,{budget:0,items:[]});
function gSave(){Store.set(G_KEY,gData);}
function gSpent(){return gData.items.reduce(function(a,i){return a+i.price;},0);}
function gRender(){
  $('#gBud').textContent=money(gData.budget);
  $('#gSub').textContent=gData.budget?('Nagastos: '+money(gSpent())):'Walang budget na naka-set';
}
function gSet(){var b=parseFloat(val('gBudget'));if(isNaN(b)||b<=0){toast('Ilagay ang tamang budget');return;}
  gData.budget=b;gSave();gRender();resetForm(['gBudget']);toast('Budget na-save');}
function gAdd(){
  var it=val('gItem'),p=parseFloat(val('gPrice')),c=$('#gCat').value;
  if(!it||isNaN(p)||p<=0){$('#gErr').innerHTML='<div class="alert err">Punan ang item at presyo</div>';return;}
  $('#gErr').innerHTML='';gData.items.push({name:it,price:p,cat:c});gSave();
  var sp=gSpent(),left=gData.budget-sp,pct=gData.budget?Math.min(100,Math.round(sp/gData.budget*100)):0;
  $('#gSpent').textContent=money(sp);$('#gLeft').textContent=money(left);
  $('#gBar').style.width=pct+'%';$('#gBar').style.background=left<0?'linear-gradient(90deg,#d33b5b,#ff5c7a)':'linear-gradient(90deg,var(--pri),var(--ok))';
  $('#gWarn').innerHTML=(gData.budget&&left<0)?'<div class="alert err">Sobra na sa budget!</div>':((gData.budget&&pct>=80)?'<div class="alert warn">Malapit nang sumobra</div>':'');
  $('#gItems').innerHTML=gData.items.map(function(i){return '<div class="item"><div class="ic">\U0001F6D2</div><div class="grow"><div class="t">'+i.name+'</div><div class="s">'+i.cat+'</div></div><b>'+money(i.price)+'</b></div>';}).join('');
  $('#gReceipt').innerHTML=gData.items.map(function(i){return '<div class="kv"><span>'+i.name+'</span><b>'+money(i.price)+'</b></div>';}).join('')+'<div class="kv"><span>Kabuuan</span><b>'+money(sp)+'</b></div>';
  resetForm(['gItem','gPrice']);toast('Naidagdag: '+it);show('result');
}
gRender();
""")

define(name="Water Bill Tracker PRO", icon="\U0001F4A7", tag="Bill vs Nakaraang Buwan", batch="Gemini",
home=r"""
<div class="hero"><div class="mut small">Bayarin Ngayong Buwan</div><div class="big" id="wBill">\u20B10</div><div class="mut small" id="wDue">Walang due date</div></div>
<button class="btn" data-go="input">\U0001F4A7 I-log ang Water Bill</button>
<h3>Kasaysayan</h3><div id="wList"></div>
""",
input=r"""
<div class="card">
 <div class="field"><label>Metro Reading</label><input id="wRead" type="number" placeholder="Hal: 120"></div>
 <div class="field"><label>Halaga ng Bill</label><input id="wAmt" type="number" placeholder="Hal: 850"></div>
 <div class="field"><label>Due Date</label><input id="wDate" type="date"></div>
 <button class="btn" onclick="wLog()">I-save ang Bill</button>
 <div id="wErr"></div>
</div>
""",
result=r"""
<div class="card">
 <div class="kv"><span>Ngayong Buwan</span><b id="wNow">\u20B10</b></div>
 <div class="kv"><span>Nakaraang Buwan</span><b id="wPrev">\u20B10</b></div>
 <div class="kv"><span>Pagkakaiba</span><b id="wDiff">\u20B10</b></div>
 <div id="wNote"></div>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F4A7</div>
 <h2>Bayad Na</h2>
 <div class="kv"><span>Halaga</span><b id="wPaid">\u20B10</b></div>
 <div class="kv"><span>Due Date</span><b id="wPaidDue">\u2014</b></div>
 <div style="font-size:40px;margin-top:8px">\u2705 PAID</div>
 <button class="btn ghost" onclick="show('input')">\u2795 Bagong Bill</button>
</div>
""",
js=r"""
var W_KEY='mcsn_water';var wData=Store.get(W_KEY,[]);
function wSave(){Store.set(W_KEY,wData);}
function wRender(){
  var last=wData[wData.length-1];
  $('#wBill').textContent=last?money(last.amount):'\u20B10';
  $('#wDue').textContent=last&&last.due?('Due: '+last.due):'Walang due date';
  $('#wList').innerHTML=wData.length?wData.slice().reverse().map(function(w){return '<div class="item"><div class="ic">\U0001F4A7</div><div class="grow"><div class="t">'+money(w.amount)+'</div><div class="s">Reading '+w.reading+' \u2022 '+w.due+'</div></div>'+(w.paid?'<span class="pill ok">PAID</span>':'<span class="pill warn">Pending</span>')+'</div>';}).join(''):'<div class="mut small">Wala pang record.</div>';
}
function wLog(){
  var r=val('wRead'),a=parseFloat(val('wAmt')),d=val('wDate');
  if(!r||isNaN(a)||a<=0){$('#wErr').innerHTML='<div class="alert err">Punan ang reading at halaga</div>';return;}
  $('#wErr').innerHTML='';
  var prev=wData[wData.length-1];
  wData.push({reading:r,amount:a,due:d||'Walang date',paid:false});wSave();wRender();
  var pv=prev?prev.amount:0,diff=a-pv;
  $('#wNow').textContent=money(a);$('#wPrev').textContent=money(pv);$('#wDiff').textContent=(diff>=0?'+':'-')+money(Math.abs(diff));
  $('#wNote').innerHTML=prev?(diff>0?'<div class="alert warn">Mas mataas ng '+money(diff)+' kaysa nakaraang buwan</div>':'<div class="alert ok">Nakatipid ng '+money(Math.abs(diff))+'</div>'):'<div class="mut small">Unang record.</div>';
  toast('Bill na-save');show('result');
}
function wPay(){
  if(!wData.length)return;var last=wData[wData.length-1];last.paid=true;wSave();wRender();
  $('#wPaid').textContent=money(last.amount);$('#wPaidDue').textContent=last.due;show('done');
}
wRender();
""")

define(name="Movie Night Picker PRO", icon="\U0001F3AC", tag="Randomize by genre", batch="Gemini",
home=r"""
<div class="hero"><div class="mut small">Movie Night</div><div class="big" id="mCount">0</div><div class="mut small">Mga napili sa listahan</div></div>
<button class="btn" data-go="input">\U0001F3AC Pumili ng Genre</button>
<h3>Napiling Pelikula</h3><div id="mList"></div>
""",
input=r"""
<div class="card">
 <h3 style="margin-top:0">Piliin ang Genre</h3>
 <div class="chips" id="mCats">
  <div class="chip" data-cat="Pinoy Comedy" onclick="mPick(this)">Pinoy Comedy</div>
  <div class="chip" data-cat="Horror" onclick="mPick(this)">Horror</div>
  <div class="chip" data-cat="Kilig" onclick="mPick(this)">Kilig</div>
  <div class="chip" data-cat="Aksyon" onclick="mPick(this)">Aksyon</div>
  <div class="chip" data-cat="Barkada" onclick="mPick(this)">Barkada</div>
 </div>
 <button class="btn" onclick="mSpin()" style="margin-top:14px">\U0001F3B2 I-pick!</button>
 <div id="mErr"></div>
</div>
""",
result=r"""
<div class="card center">
 <div style="font-size:44px">\U0001F3AC</div>
 <h2 id="mTitle">\u2014</h2>
 <div class="mut" id="mGenre">\u2014</div>
 <div class="mut small" id="mDesc" style="margin-top:8px"></div>
 <button class="btn ok" onclick="mSave()">\u2B50 I-save ang Pick</button>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F37F</div>
 <h2>Tonight's Movie Pick</h2>
 <div class="kv"><span>Pelikula</span><b id="mDTitle">\u2014</b></div>
 <div class="kv"><span>Genre</span><b id="mDGenre">\u2014</b></div>
 <button class="btn ghost" onclick="mNew()">\U0001F3B2 Bagong Pick</button>
</div>
""",
js=r"""
var M_MOVIES={
 'Pinoy Comedy':['Praybeyt Benjamin','Sisterakas','The Amazing Praybeyt','Here Comes the Bride'],
 'Horror':['Sukob','Feng Shui','The Healing','Shake Rattle & Roll'],
 'Kilig':['One More Chance','Hello Love Goodbye','A Second Chance','Starting Over Again'],
 'Aksyon':['Buy Bust','On the Job','Metro Manila','Batangas'],
 'Barkada':['Heneral Luna','Ang Pangarap Kong Holdap','Respeto','Patay na si Hesus']
};
var M_KEY='mcsn_movies';var mData=Store.get(M_KEY,[]);var mCur=null,mCat=null;
function mRender(){var el=$('#mCount');el.textContent=mData.length;
  $('#mList').innerHTML=mData.length?mData.slice().reverse().map(function(m){return '<div class="item"><div class="ic">\U0001F3AC</div><div class="grow"><div class="t">'+m.title+'</div><div class="s">'+m.cat+'</div></div></div>';}).join(''):'<div class="mut small">Wala pang napili.</div>';}
function mPick(el){mCat=el.dataset.cat;$$('#mCats .chip').forEach(function(c){c.classList.remove('on');});el.classList.add('on');}
function mSpin(){
  if(!mCat){$('#mErr').innerHTML='<div class="alert err">Select category</div>';return;}
  $('#mErr').innerHTML='';
  var arr=M_MOVIES[mCat],t=arr[Math.floor(Math.random()*arr.length)];
  mCur={title:t,cat:mCat};$('#mTitle').textContent=t;$('#mGenre').textContent=mCat;
  $('#mDesc').textContent='Genre: '+mCat+' \u2022 handa nang panoorin!';show('result');
}
function mSave(){if(!mCur)return;mData.push(mCur);Store.set(M_KEY,mData);mRender();
  $('#mDTitle').textContent=mCur.title;$('#mDGenre').textContent=mCur.cat;toast('Pick saved');show('done');}
function mNew(){mCat=null;$$('#mCats .chip').forEach(function(c){c.classList.remove('on');});show('input');}
mRender();
""")

define(name="Pinoy Karaoke Song List PRO", icon="\U0001F3A4", tag="Search + Song Code", batch="Gemini",
home=r"""
<div class="hero"><div class="mut small">Aking Setlist</div><div class="big" id="kCount">0</div><div class="mut small">Mga kantang napili</div></div>
<button class="btn" data-go="input">\U0001F3A4 Maghanap ng Kanta</button>
<h3>Kategorya</h3>
<div class="chips" id="kCats">
 <div class="chip" onclick="kFilter(this)" data-cat="Birit Hits">Birit Hits</div>
 <div class="chip" onclick="kFilter(this)" data-cat="90s Banda">90s Banda</div>
 <div class="chip" onclick="kFilter(this)" data-cat="Tito/Tita Classics">Tito/Tita Classics</div>
 <div class="chip" onclick="kFilter(this)" data-cat="Inuman Anthems">Inuman Anthems</div>
</div>
<div id="kList" style="margin-top:12px"></div>
""",
input=r"""
<div class="card">
 <div class="field"><label>Hanapin (kanta o singer)</label><input id="kSearch" placeholder="Hal: Bakit"></div>
 <div class="field"><label>Kanta</label>
  <select id="kSong"></select></div>
 <button class="btn" onclick="kAdd()">\u2795 Add to My List</button>
 <div id="kErr"></div>
</div>
""",
result=r"""
<div class="card">
 <h3 style="margin-top:0">Aking Pila</h3>
 <div id="kQueue"></div>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F3A4</div>
 <h2>Setlist Saved</h2>
 <div id="kSaved"></div>
 <button class="btn ghost" onclick="show('input')">\u2795 Dagdag Kanta</button>
</div>
""",
js=r"""
var K_SONGS=[
 {t:'Bakit Ngayon Ka Lang',s:'OPM',c:'Tito/Tita Classics',code:'12045'},
 {t:'Basang-Basa',s:'Aegis',c:'Birit Hits',code:'20311'},
 {t:'Halik',s:'Kamikazee',c:'90s Banda',code:'31422'},
 {t:'Beer',s:'Itchyworms',c:'Inuman Anthems',code:'40019'},
 {t:'Tadhana',s:'Up Dharma Down',c:'90s Banda',code:'51108'},
 {t:'Narda',s:'Kamikazee',c:'Inuman Anthems',code:'60233'},
 {t:'Ikaw',s:'Yeng Constantino',c:'Birit Hits',code:'70544'},
 {t:'Panalangin',s:'Apo Hiking Society',c:'Tito/Tita Classics',code:'80077'}
];
var K_KEY='mcsn_karaoke';var kData=Store.get(K_KEY,[]);var kFilterCat=null;
function kRenderList(){
  var arr=K_SONGS.filter(function(s){return !kFilterCat||s.c===kFilterCat;});
  $('#kList').innerHTML=arr.map(function(s){return '<div class="item"><div class="ic">\U0001F3B5</div><div class="grow"><div class="t">'+s.t+'</div><div class="s">'+s.s+' \u2022 '+s.c+'</div></div><b>'+s.code+'</b></div>';}).join('');
  $('#kSong').innerHTML=K_SONGS.map(function(s,i){return '<option value="'+i+'">'+s.t+' \u2013 '+s.s+'</option>';}).join('');
}
function kFilter(el){kFilterCat=el.dataset.cat;$$('#kCats .chip').forEach(function(c){c.classList.remove('on');});el.classList.add('on');kRenderList();}
function kAdd(){
  var i=parseInt($('#kSong').value,10);if(isNaN(i)){return;}
  kData.push(K_SONGS[i]);Store.set(K_KEY,kData);
  $('#kQueue').innerHTML=kData.map(function(s){return '<div class="item"><div class="ic">\U0001F3A4</div><div class="grow"><div class="t">'+s.t+'</div><div class="s">'+s.s+'</div></div><b>'+s.code+'</b></div>';}).join('');
  $('#kSaved').innerHTML=kData.map(function(s){return '<div class="kv"><span>'+s.t+'</span><b>'+s.code+'</b></div>';}).join('');
  $('#kCount').textContent=kData.length;toast('Naidagdag sa listahan');show('result');
}
kRenderList();
""")

define(name="Trivia Quiz - Pinoy PRO", icon="\U0001F9E0", tag="Score = Tamang Sagot", batch="Gemini",
home=r"""
<div class="hero"><div class="mut small">Pinoy Trivia</div><div class="big" id="tScore">0</div><div class="mut small">Kabuuang iskor</div></div>
<button class="btn" data-go="input">\U0001F9E0 Simulan ang Quiz</button>
<h3>Kategorya</h3>
<div class="chips">
 <div class="chip on">Kultura</div><div class="chip">Kasaysayan</div><div class="chip">Pagkain</div><div class="chip">Showbiz</div>
</div>
""",
input=r"""
<div class="card">
 <div class="mut small" id="tQNo">Tanong 1/5</div>
 <h2 id="tQ" style="font-size:17px">\u2014</h2>
 <div id="tChoices"></div>
 <div id="tErr"></div>
</div>
""",
result=r"""
<div class="card">
 <div class="kv"><span>Iyong Sagot</span><b id="tYour">\u2014</b></div>
 <div class="kv"><span>Tamang Sagot</span><b id="tRight">\u2014</b></div>
 <div class="alert ok" id="tFact" style="margin-top:12px"></div>
 <div class="kv"><span>Iskor</span><b id="tScore2">0</b></div>
 <button class="btn" onclick="tNext()">Susunod na Tanong</button>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F3C6</div>
 <h2>Pinoy Henyo!</h2>
 <div class="kv"><span>Kabuuang Iskor</span><b id="tFinal">0/5</b></div>
 <div id="tBadge"></div>
 <button class="btn ghost" onclick="tReset()">\U0001F9E0 Ulitin</button>
</div>
""",
js=r"""
var T_Q=[
 {q:'Anong rehiyon ang Baguio City?',c:['Cordillera','Ilocos','Bicol','Mindanao'],a:0,f:'Baguio ay nasa Cordillera Administrative Region.'},
 {q:'Sino ang pambansang bayani ng Pilipinas?',c:['Andres Bonifacio','Jose Rizal','Lapu-Lapu','Emilio Aguinaldo'],a:1,f:'Si Jose Rizal ang pambansang bayani.'},
 {q:'Anong prutas ang ginagawang "sinigang" sa Cebu?',c:['Mangga','Bayabas','Sampalok','Kamias'],a:1,f:'Sa Cebu, bayabas ang madalas gamit.'},
 {q:'Ano ang pinakamalaking isda sa Pilipinas?',c:['Bangus','Tilapia','Butanding','Galunggong'],a:2,f:'Butanding (whale shark) ang pinakamalaki.'},
 {q:'Kailan idineklara ang kalayaan ng Pilipinas?',c:['Hunyo 12, 1898','Agosto 21, 1983','Hulyo 4, 1946','Disyembre 30, 1896'],a:0,f:'Hunyo 12, 1898 sa Kawit, Cavite.'}
];
var T_KEY='mcsn_trivia';var tData=Store.get(T_KEY,{score:0});var tIdx=0,tAns=-1;
function tRender(){tIdx=0;tAns=-1;$('#tScore').textContent=tData.score;tShow();}
function tShow(){
  var q=T_Q[tIdx];$('#tQNo').textContent='Tanong '+(tIdx+1)+'/'+T_Q.length;$('#tQ').textContent=q.q;
  $('#tChoices').innerHTML=q.c.map(function(c,i){return '<button class="btn ghost" style="margin-bottom:8px" onclick="tAnswer('+i+')">'+String.fromCharCode(65+i)+'. '+c+'</button>';}).join('');
  $('#tErr').innerHTML='';
}
function tAnswer(i){
  var q=T_Q[tIdx];tAns=i;
  if(i===q.a){tData.score++;Store.set(T_KEY,tData);}
  $('#tScore').textContent=tData.score;
  $('#tYour').textContent=String.fromCharCode(65+i)+'. '+q.c[i];
  $('#tRight').textContent=String.fromCharCode(65+q.a)+'. '+q.c[q.a];
  $('#tFact').textContent='Alam Mo Ba? '+q.f;
  $('#tScore2').textContent=tData.score;
  show('result');
}
function tNext(){
  tIdx++;
  if(tIdx>=T_Q.length){$('#tFinal').textContent=tData.score+'/'+T_Q.length;
    $('#tBadge').innerHTML=tData.score>=4?'<div class="pill ok" style="margin-top:10px">Pinoy Master Badge</div>':'<div class="pill warn" style="margin-top:10px">Subukan pa!</div>';
    show('done');return;}
  tShow();show('input');
}
function tReset(){tData.score=0;Store.set(T_KEY,tData);tRender();show('input');}
tRender();
""")

# ---------------- GEMINI 8-14 ----------------
define(name="Joke of the Day PRO", icon="\U0001F602", tag="Joke + Punchline reveal", batch="Gemini",
home=r"""
<div class="hero"><div class="mut small">Joke of the Day</div><div class="big" id="jCount">0</div><div class="mut small">Paboritong biro na naka-save</div></div>
<button class="btn" data-go="input">\U0001F602 Ipakita ang Biro</button>
<h3>Kategorya</h3>
<div class="chips" id="jCats">
 <div class="chip" onclick="jCat(this)" data-cat="Knock-Knock">Knock-Knock</div>
 <div class="chip" onclick="jCat(this)" data-cat="Tatay Jokes">Tatay Jokes</div>
 <div class="chip" onclick="jCat(this)" data-cat="Pinoy">Pinoy</div>
</div>
<div id="jFavs" style="margin-top:12px"></div>
""",
input=r"""
<div class="card">
 <div class="mut small" id="jCatLabel">Biro</div>
 <h2 id="jSetup" style="font-size:17px">\u2014</h2>
 <button class="btn" onclick="jReveal()">\U0001F440 Ipakita ang Sagot</button>
</div>
""",
result=r"""
<div class="card">
 <h3 style="margin-top:0">Punchline</h3>
 <h2 id="jPunch" style="font-size:18px">\u2014</h2>
 <div class="row" style="margin-top:12px">
  <button class="btn ghost sm" style="flex:1" onclick="jReact('\U0001F602')">\U0001F602</button>
  <button class="btn ghost sm" style="flex:1" onclick="jReact('\U0001F923')">\U0001F923</button>
  <button class="btn ghost sm" style="flex:1" onclick="jReact('\U0001F44D')">\U0001F44D</button>
 </div>
 <button class="btn ok" style="margin-top:12px" onclick="jSave()">\u2B50 I-save sa Paborito</button>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F602</div>
 <h2>Naka-save na Biro</h2>
 <div id="jSaved"></div>
 <button class="btn ghost" onclick="jNew()">\U0001F3B2 Bagong Biro</button>
</div>
""",
js=r"""
var J_JOKES={
 'Knock-Knock':[{s:'Knock knock! Sino yan?',p:'Noypi! Noypi kayo diyan!'},{s:'Knock knock! Sino yan?',p:'Nene. Nene ka ba? Kasi ikaw ang tinitibok ng puso ko.'}],
 'Tatay Jokes':[{s:'Anong tawag sa batang laging nasa kalye?',p:'Tambay... joke lang, "Sikat" pala!'},{s:'Bakit malungkot ang kalendaryo?',p:'Kasi marami siyang araw pero isa lang ang date.'}],
 'Pinoy':[{s:'Anong sabi ng Pinoy pag wala nang pera?',p:'"Wala akong barya" pero may load.'},{s:'Bakit mataas ang pride ng Pinoy?',p:'Dahil mahilig sa "ako na lang".'}]
};
var J_KEY='mcsn_jokes';var jData=Store.get(J_KEY,[]);var jCur=null,jCat=null;
function jRender(){var el=$('#jCount');el.textContent=jData.length;
  $('#jFavs').innerHTML=jData.length?jData.slice().reverse().map(function(j){return '<div class="item"><div class="ic">\U0001F602</div><div class="grow"><div class="t">'+j.s+'</div><div class="s">'+j.p+'</div></div></div>';}).join(''):'<div class="mut small">Wala pang paborito.</div>';}
function jCat(el){jCat=el.dataset.cat;$$('#jCats .chip').forEach(function(c){c.classList.remove('on');});el.classList.add('on');
  var arr=J_JOKES[jCat],j=arr[Math.floor(Math.random()*arr.length)];jCur={s:j.s,p:j.p,cat:jCat};
  $('#jCatLabel').textContent=jCat;$('#jSetup').textContent=j.s;$('#jPunch').textContent='\u2022 \u2022 \u2022';show('input');}
function jReveal(){if(!jCur){toast('Pumili muna ng kategorya');return;}$('#jPunch').textContent=jCur.p;show('result');}
function jReact(e){toast('Salamat sa reaction '+e);}
function jSave(){if(!jCur)return;jData.push(jCur);Store.set(J_KEY,jData);jRender();
  $('#jSaved').innerHTML='<div class="kv"><span>Biro</span><b>'+jCur.s+'</b></div><div class="kv"><span>Sagot</span><b>'+jCur.p+'</b></div>';toast('Naka-save');show('done');}
function jNew(){jCat=null;$$('#jCats .chip').forEach(function(c){c.classList.remove('on');});show('home');}
jRender();
""")

define(name="Music Playlist Maker PRO", icon="\U0001F3B6", tag="Tracks = Bilang ng Kanta", batch="Gemini",
home=r"""
<div class="hero"><div class="mut small">Aking Playlists</div><div class="big" id="plCount">0</div><div class="mut small">Mga ginawang playlist</div></div>
<button class="btn" data-go="input">\U0001F3B6 Gumawa ng Playlist</button>
<h3>Mga Playlist</h3><div id="plList"></div>
""",
input=r"""
<div class="card">
 <div class="field"><label>Pangalan ng Playlist</label><input id="plName" placeholder="Hal: Roadtrip"></div>
 <div class="field"><label>Kanta</label><input id="plSong" placeholder="Hal: Tadhana - UDD"></div>
 <button class="btn" onclick="plAddTrack()">\u2795 Idagdag sa Listahan</button>
 <div id="plErr"></div>
 <div id="plTracks" style="margin-top:12px"></div>
</div>
""",
result=r"""
<div class="card">
 <div class="kv"><span>Playlist</span><b id="plRName">\u2014</b></div>
 <div class="kv"><span>Bilang ng Tracks</span><b id="plRCount">0</b></div>
 <div id="plRList" style="margin-top:10px"></div>
 <button class="btn ok" onclick="plSave()">\U0001F4BE I-save ang Playlist</button>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F3B6</div>
 <h2>Playlist Card</h2>
 <div class="kv"><span>Pangalan</span><b id="plDName">\u2014</b></div>
 <div class="kv"><span>Tracks</span><b id="plDCount">0</b></div>
 <div id="plDList" style="margin-top:10px"></div>
 <button class="btn ghost" onclick="plNew()">\u2795 Bagong Playlist</button>
</div>
""",
js=r"""
var PL_KEY='mcsn_playlist';var plData=Store.get(PL_KEY,[]);var plTracks=[];
function plRender(){var el=$('#plCount');el.textContent=plData.length;
  $('#plList').innerHTML=plData.length?plData.slice().reverse().map(function(p){return '<div class="item"><div class="ic">\U0001F3B6</div><div class="grow"><div class="t">'+p.name+'</div><div class="s">'+p.tracks.length+' tracks</div></div></div>';}).join(''):'<div class="mut small">Wala pang playlist.</div>';}
function plAddTrack(){
  var n=val('plName'),s=val('plSong');
  if(!n){$('#plErr').innerHTML='<div class="alert err">Ilagay ang pangalan ng playlist</div>';return;}
  if(!s){$('#plErr').innerHTML='<div class="alert err">Ilagay ang kanta</div>';return;}
  $('#plErr').innerHTML='';plTracks.push(s);
  $('#plTracks').innerHTML=plTracks.map(function(t,i){return '<div class="item"><div class="ic">'+(i+1)+'</div><div class="grow"><div class="t">'+t+'</div></div></div>';}).join('');
  $('#plRName').textContent=n;$('#plRCount').textContent=plTracks.length;
  $('#plRList').innerHTML=plTracks.map(function(t){return '<div class="kv"><span>'+t+'</span></div>';}).join('');
  resetForm(['plSong']);toast('Naidagdag: '+s);show('result');
}
function plSave(){var n=val('plName');if(!n||!plTracks.length){toast('Kulang ang datos');return;}
  var p={name:n,tracks:plTracks.slice()};plData.push(p);Store.set(PL_KEY,plData);plRender();
  $('#plDName').textContent=n;$('#plDCount').textContent=plTracks.length;
  $('#plDList').innerHTML=plTracks.map(function(t){return '<div class="kv"><span>'+t+'</span></div>';}).join('');
  plTracks=[];resetForm(['plName','plSong']);$('#plTracks').innerHTML='';toast('Playlist na-save');show('done');
}
function plNew(){plTracks=[];resetForm(['plName','plSong']);$('#plTracks').innerHTML='';show('input');}
plRender();
""")

define(name="Short Story Reader PRO", icon="\U0001F4D6", tag="Night mode + font size", batch="Gemini",
home=r"""
<div class="hero"><div class="mut small">Pocket Library</div><div class="big" id="ssCount">0</div><div class="mut small">Nabasa na</div></div>
<h3>Kategorya</h3>
<div class="chips" id="ssCats">
 <div class="chip" onclick="ssFilter(this)" data-cat="Kilig">Kilig</div>
 <div class="chip" onclick="ssFilter(this)" data-cat="Kababalaghan">Kababalaghan</div>
 <div class="chip" onclick="ssFilter(this)" data-cat="Pamilya">Pamilya</div>
 <div class="chip" onclick="ssFilter(this)" data-cat="Inspirational">Inspirational</div>
</div>
<div id="ssList" style="margin-top:12px"></div>
""",
input=r"""
<div class="card">
 <div class="row" style="justify-content:space-between;align-items:center">
  <div class="mut small" id="ssTitle">\u2014</div>
  <button class="btn ghost sm" onclick="ssFont()">A+</button>
 </div>
 <div id="ssBody" style="font-size:15px;line-height:1.7;margin-top:10px">\u2014</div>
 <button class="btn" style="margin-top:12px" onclick="ssFinish()">Tapusin ang Kwento</button>
</div>
""",
result=r"""
<div class="card">
 <h3 style="margin-top:0">Aral ng Kwento</h3>
 <div class="alert ok" id="ssAral"></div>
 <div class="mut small" style="margin-top:10px">Susunod na basahin: <b id="ssNext">\u2014</b></div>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F4D6</div>
 <h2>Nabasa Na</h2>
 <div class="kv"><span>Kwento</span><b id="ssDoneTitle">\u2014</b></div>
 <div id="ssQuote" class="alert ok" style="margin-top:12px"></div>
 <button class="btn ghost" onclick="show('home')">\U0001F4DA Bumalik sa Library</button>
</div>
""",
js=r"""
var SS_STORIES=[
 {t:'Ang Huling Jeep',c:'Pamilya',m:3,body:'Tuwing gabi, sinusundo ni Mang Tomas ang anak niyang si Ana sa trabaho. Isang gabi, hindi na siya dumating. Naiwan ang lumang jeep na may sulat: "Anak, hinahanap mo ako? Nandito lang ako sa alaala mo."',aral:'Ang pagmamahal ng magulang ay hindi kailanman nawawala.',q:'Mahalin ang pamilya habang nandiyan pa.'},
 {t:'Multo sa CR',c:'Kababalaghan',m:4,body:'Tuwing hatinggabi, may kumakatok sa banyo ng dorm. Isang araw, sinagot ito ng bagong tenant: "Sino yan?" Sumagot ang boses: "Ikaw ba yung umuupa sa kwarto ko dati?" Tumakbo siya palabas at hindi na bumalik.',aral:'Respetuhin ang mga lugar na hindi sa iyo.',q:'Ang takot ay nasa isip lamang.'},
 {t:'Taho sa Umaga',c:'Inspirational',m:3,body:'Araw-araw, alas-singko ng umaga, naririnig ni Lito ang sigaw ng magtataho. Napansin niyang masaya ito kahit maulan. Tinanong niya kung bakit. Sagot nito: "Simple lang ang buhay ko, pero puno ng ngiti ang mga bumibili."',aral:'Ang tunay na kayamanan ay ang kasiyahan sa simpleng bagay.',q:'Maging masaya sa maliliit na bagay.'},
 {t:'Text ni Kuya',c:'Kilig',m:3,body:'Isang gabi, nag-text ang crush ni Maya: "Pwede ba kitang ihatid?" Kinabahan siya pero sumagot: "Sige." Pagdating nito, sabi niya: "Hindi lang kita gustong ihatid. Gusto rin kitang samahan habambuhay."',aral:'Ang pag-ibig ay hindi kailangang pahirapan.',q:'Magsabi ng nararamdaman bago mahuli ang lahat.'}
];
var SS_KEY='mcsn_stories';var ssData=Store.get(SS_KEY,[]);var ssCur=null,ssCat=null,ssFontSize=15;
function ssRender(){var el=$('#ssCount');el.textContent=ssData.length;
  var arr=SS_STORIES.filter(function(s){return !ssCat||s.c===ssCat;});
  $('#ssList').innerHTML=arr.map(function(s,i){var done=ssData.indexOf(s.t)>=0;
    return '<div class="item" onclick="ssOpen('+SS_STORIES.indexOf(s)+')"><div class="ic">\U0001F4D6</div><div class="grow"><div class="t">'+s.t+'</div><div class="s">'+s.c+' \u2022 '+s.m+' min</div></div>'+(done?'<span class="pill ok">Nabasa</span>':'<span class="pill pri">Basahin</span>')+'</div>';}).join('');
}
function ssFilter(el){ssCat=el.dataset.cat;$$('#ssCats .chip').forEach(function(c){c.classList.remove('on');});el.classList.add('on');ssRender();}
function ssOpen(i){ssCur=SS_STORIES[i];$('#ssTitle').textContent=ssCur.t+' \u2022 '+ssCur.c;
  $('#ssBody').style.fontSize=ssFontSize+'px';$('#ssBody').textContent=ssCur.body;show('input');}
function ssFont(){ssFontSize=ssFontSize>=20?13:ssFontSize+1;$('#ssBody').style.fontSize=ssFontSize+'px';toast('Font size: '+ssFontSize+'px');}
function ssFinish(){if(!ssCur)return;var idx=SS_STORIES.indexOf(ssCur);
  $('#ssAral').textContent=ssCur.aral;$('#ssNext').textContent=SS_STORIES[(idx+1)%SS_STORIES.length].t;
  $('#ssDoneTitle').textContent=ssCur.t;$('#ssQuote').textContent='"'+ssCur.q+'"';show('result');}
function ssDone(){if(ssData.indexOf(ssCur.t)<0)ssData.push(ssCur.t);Store.set(SS_KEY,ssData);ssRender();toast('Nabasa na: '+ssCur.t);show('done');}
ssRender();
""")

define(name="Home Cleaning Schedule PRO", icon="\U0001F9F9", tag="Progress = Tapos / Total", batch="Gemini",
home=r"""
<div class="hero"><div class="mut small">Lingguhang Linis</div><div class="big" id="hcPct">0%</div><div class="mut small" id="hcSub">0/0 tapos</div></div>
<button class="btn" data-go="input">\U0001F9F9 Simulan ang Linis</button>
<h3>Toka ngayong linggo</h3><div id="hcList"></div>
""",
input=r"""
<div class="card">
 <div class="field"><label>Parte ng Bahay</label>
  <select id="hcArea"><option>Kusina</option><option>Sala</option><option>Banyo</option><option>Kwarto</option></select></div>
 <div class="field"><label>Gawain</label>
  <select id="hcTask"><option>Pagwawalis</option><option>Paghuhugas</option><option>Pagtatapon ng basura</option><option>Pagpupunas</option></select></div>
 <div class="field"><label>Sino ang naka-toka?</label><input id="hcWho" placeholder="Hal: Ate"></div>
 <button class="btn" onclick="hcAssign()">\u2795 I-toka</button>
 <div id="hcErr"></div>
</div>
""",
result=r"""
<div class="card">
 <h3 style="margin-top:0">Progress ngayong araw</h3>
 <div class="bar"><i id="hcBar" style="width:0%"></i></div>
 <div class="kv" style="margin-top:12px"><span>Tapos na</span><b id="hcDone">0/0</b></div>
 <div id="hcCheck"></div>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\u2728</div>
 <h2>Malinis Na!</h2>
 <div class="kv"><span>Progress</span><b id="hcFinal">100%</b></div>
 <div id="hcToka"></div>
 <button class="btn ghost" onclick="show('input')">\u2795 Dagdag Gawain</button>
</div>
""",
js=r"""
var HC_KEY='mcsn_cleaning';var hcData=Store.get(HC_KEY,[]);
function hcSave(){Store.set(HC_KEY,hcData);}
function hcPct(){if(!hcData.length)return 0;return Math.round(hcData.filter(function(t){return t.done;}).length/hcData.length*100);}
function hcRender(){var p=hcPct();$('#hcPct').textContent=p+'%';
  $('#hcSub').textContent=hcData.filter(function(t){return t.done;}).length+'/'+hcData.length+' tapos';
  $('#hcList').innerHTML=hcData.length?hcData.map(function(t,i){return '<div class="item" onclick="hcToggle('+i+')"><div class="ic">'+(t.done?'\u2705':'\U0001F9F9')+'</div><div class="grow"><div class="t" style="'+(t.done?'text-decoration:line-through;color:var(--mut)':'')+'">'+t.task+'</div><div class="s">'+t.area+' \u2022 '+t.who+'</div></div></div>';}).join(''):'<div class="mut small">Wala pang toka.</div>';}
function hcAssign(){
  var a=$('#hcArea').value,t=$('#hcTask').value,w=val('hcWho');
  if(!w){$('#hcErr').innerHTML='<div class="alert err">Ilagay kung sino ang naka-toka</div>';return;}
  $('#hcErr').innerHTML='';hcData.push({area:a,task:t,who:w,done:false});hcSave();hcRender();
  $('#hcCheck').innerHTML=hcData.map(function(x,i){return '<div class="chk'+(x.done?' on':'')+'" onclick="hcToggle('+i+')"><div class="box">'+(x.done?'\u2714':'')+'</div><div class="grow"><div class="t">'+x.task+'</div><div class="s">'+x.area+' \u2022 '+x.who+'</div></div></div>';}).join('');
  var p=hcPct();$('#hcBar').style.width=p+'%';$('#hcDone').textContent=hcData.filter(function(t){return t.done;}).length+'/'+hcData.length;
  resetForm(['hcWho']);toast('Naka-toka kay '+w);show('result');
}
function hcToggle(i){hcData[i].done=!hcData[i].done;hcSave();hcRender();
  var p=hcPct();$('#hcBar').style.width=p+'%';$('#hcDone').textContent=hcData.filter(function(t){return t.done;}).length+'/'+hcData.length;
  $('#hcCheck').innerHTML=hcData.map(function(x,j){return '<div class="chk'+(x.done?' on':'')+'" onclick="hcToggle('+j+')"><div class="box">'+(x.done?'\u2714':'')+'</div><div class="grow"><div class="t">'+x.task+'</div><div class="s">'+x.area+' \u2022 '+x.who+'</div></div></div>';}).join('');
  if(p===100&&hcData.length){$('#hcFinal').textContent='100%';
    $('#hcToka').innerHTML=hcData.map(function(x){return '<div class="kv"><span>'+x.task+'</span><b>'+x.who+'</b></div>';}).join('');
    toast('Tapos na lahat!');show('done');}else{toast(hcData[i].task+(hcData[i].done?' tapos':' hindi pa'));}}
hcRender();
""")

define(name="Medicine Reminder PRO", icon="\U0001F48A", tag="Umaga / Tanghali / Gabi", batch="Gemini",
home=r"""
<div class="hero"><div class="mut small">Paalala ng Gamot</div><div class="big" id="mdCount">0</div><div class="mut small">Naka-set na gamot</div></div>
<button class="btn" data-go="input">\U0001F48A Magdagdag ng Gamot</button>
<h3>Mga Naka-set</h3><div id="mdList"></div>
""",
input=r"""
<div class="card">
 <div class="field"><label>Pangalan ng Gamot</label><input id="mdName" placeholder="Hal: Biogesic"></div>
 <div class="field"><label>Ilang Piraso</label><input id="mdPcs" type="number" placeholder="Hal: 1"></div>
 <div class="field"><label>Oras</label><select id="mdWhen"><option>Umaga</option><option>Tanghali</option><option>Gabi</option></select></div>
 <div class="field"><label>Tagubilin</label><select id="mdNote"><option>Bago Kumain</option><option>Pagkatapos Kumain</option></select></div>
 <button class="btn" onclick="mdAdd()">I-set ang Paalala</button>
 <div id="mdErr"></div>
</div>
""",
result=r"""
<div class="card center">
 <div style="font-size:44px">\u23F0</div>
 <h2 id="mdNow">Oras na!</h2>
 <div class="kv"><span>Gamot</span><b id="mdRName">\u2014</b></div>
 <div class="kv"><span>Dami</span><b id="mdRPcs">\u2014</b></div>
 <div class="kv"><span>Tagubilin</span><b id="mdRNote">\u2014</b></div>
 <button class="btn ok" onclick="mdTake()">\u2705 Nainom Na</button>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F48A</div>
 <h2>Nainom Na</h2>
 <div id="mdTaken"></div>
 <button class="btn ghost" onclick="show('input')">\u2795 Bagong Gamot</button>
</div>
""",
js=r"""
var MD_KEY='mcsn_meds';var mdData=Store.get(MD_KEY,[]);var mdCur=null;
function mdSave(){Store.set(MD_KEY,mdData);}
function mdRender(){var el=$('#mdCount');el.textContent=mdData.length;
  $('#mdList').innerHTML=mdData.length?mdData.map(function(m){var ic=m.when==='Umaga'?'\U0001F305':(m.when==='Tanghali'?'\u2600\uFE0F':'\U0001F319');
    return '<div class="item"><div class="ic">'+ic+'</div><div class="grow"><div class="t">'+m.name+'</div><div class="s">'+m.when+' \u2022 '+m.pcs+' pcs \u2022 '+m.note+'</div></div></div>';}).join(''):'<div class="mut small">Wala pang gamot.</div>';}
function mdAdd(){
  var n=val('mdName'),p=val('mdPcs');
  if(!n||!p){$('#mdErr').innerHTML='<div class="alert err">Punan ang pangalan at dami</div>';return;}
  $('#mdErr').innerHTML='';mdCur={name:n,pcs:p,when:$('#mdWhen').value,note:$('#mdNote').value};
  mdData.push(mdCur);mdSave();mdRender();
  $('#mdNow').textContent='Oras na ng '+mdCur.when+'!';$('#mdRName').textContent=mdCur.name;
  $('#mdRPcs').textContent=mdCur.pcs+' piraso';$('#mdRNote').textContent=mdCur.note;
  resetForm(['mdName','mdPcs']);toast('Naka-set: '+n);show('result');
}
function mdTake(){if(!mdCur)return;var d=new Date();var t=d.toLocaleTimeString('en-PH',{hour:'2-digit',minute:'2-digit'});
  $('#mdTaken').innerHTML='<div class="kv"><span>'+mdCur.name+'</span><b>\u2705 Nainom Na ('+t+')</b></div>';toast('Nainom na');show('done');}
mdRender();
""")

define(name="Plant Care Guide PRO", icon="\U0001F331", tag="Dilig / Sun / Schedule", batch="Gemini",
home=r"""
<div class="hero"><div class="mut small">Aking Garden</div><div class="big" id="pcCount">0</div><div class="mut small">Mga alagang halaman</div></div>
<button class="btn" data-go="input">\U0001F331 Magdagdag ng Halaman</button>
<h3>My Garden</h3><div id="pcList"></div>
""",
input=r"""
<div class="card">
 <div class="field"><label>Pangalan ng Halaman</label><input id="pcName" placeholder="Hal: Snake Plant"></div>
 <div class="field"><label>Dilig bawat (araw)</label><input id="pcDays" type="number" placeholder="Hal: 3"></div>
 <div class="field"><label>Sun</label><select id="pcSun"><option>Buong Araw</option><option>Kalahating Araw</option><option>Anino lang</option></select></div>
 <button class="btn" onclick="pcAdd()">I-save ang Halaman</button>
 <div id="pcErr"></div>
</div>
""",
result=r"""
<div class="card">
 <div class="kv"><span>Halaman</span><b id="pcRName">\u2014</b></div>
 <div class="kv"><span>Dilig</span><b id="pcRDays">\u2014</b></div>
 <div class="kv"><span>Sun</span><b id="pcRSun">\u2014</b></div>
 <div class="kv"><span>Susunod na Dilig</span><b id="pcRNext">\u2014</b></div>
 <button class="btn ok" onclick="pcWater()">\U0001F4A7 Nadiligan Na Ngayon</button>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F331</div>
 <h2>Plant Card</h2>
 <div class="kv"><span>Halaman</span><b id="pcDName">\u2014</b></div>
 <div class="kv"><span>Huling Dilig</span><b id="pcDDate">\u2014</b></div>
 <div class="kv"><span>Susunod</span><b id="pcDNext">\u2014</b></div>
 <button class="btn ghost" onclick="show('input')">\U0001F4A7 Bagong Halaman</button>
</div>
""",
js=r"""
var PC_KEY='mcsn_plants';var pcData=Store.get(PC_KEY,[]);var pcCur=null;
function pcSave(){Store.set(PC_KEY,pcData);}
function pcNext(p){var d=new Date(p.last);d.setDate(d.getDate()+p.days);return d.toISOString().slice(0,10);}
function pcRender(){var el=$('#pcCount');el.textContent=pcData.length;
  $('#pcList').innerHTML=pcData.length?pcData.map(function(p){var need=new Date(pcNext(p))<=new Date();
    return '<div class="item"><div class="ic">\U0001F331</div><div class="grow"><div class="t">'+p.name+'</div><div class="s">Dilig bawat '+p.days+' araw \u2022 '+p.sun+'</div></div>'+(need?'<span class="pill warn">\U0001F4A7 Diligin</span>':'<span class="pill ok">OK</span>')+'</div>';}).join(''):'<div class="mut small">Wala pang halaman.</div>';}
function pcAdd(){
  var n=val('pcName'),d=parseInt(val('pcDays'),10);
  if(!n||isNaN(d)||d<=0){$('#pcErr').innerHTML='<div class="alert err">Punan ang pangalan at araw</div>';return;}
  $('#pcErr').innerHTML='';pcCur={name:n,days:d,sun:$('#pcSun').value,last:new Date().toISOString().slice(0,10)};
  pcData.push(pcCur);pcSave();pcRender();
  $('#pcRName').textContent=n;$('#pcRDays').textContent='Bawat '+d+' araw';$('#pcRSun').textContent=pcCur.sun;
  $('#pcRNext').textContent=pcNext(pcCur);resetForm(['pcName','pcDays']);toast('Naidagdag: '+n);show('result');
}
function pcWater(){if(!pcCur)return;pcCur.last=new Date().toISOString().slice(0,10);pcSave();pcRender();
  $('#pcDName').textContent=pcCur.name;$('#pcDDate').textContent=pcCur.last;$('#pcDNext').textContent=pcNext(pcCur);
  toast('Nadiligan na');show('done');}
pcRender();
""")

define(name="DIY Cleaning Mix Calculator PRO", icon="\U0001F9FC", tag="Tama sukat + Safety", batch="Gemini",
home=r"""
<div class="hero"><div class="mut small">DIY Panlinis</div><div class="big" id="dcCount">0</div><div class="mut small">Naka-save na recipe</div></div>
<button class="btn" data-go="input">\U0001F9FC Pumili ng Lilinisin</button>
<h3>Mga Naka-save</h3><div id="dcList"></div>
""",
input=r"""
<div class="card">
 <div class="field"><label>Ano ang lilinisin?</label>
  <select id="dcWhat"><option>Mamantikang Kusina</option><option>Salamin</option><option>Mantsa sa Damit</option><option>Amoy sa Banyo</option></select></div>
 <div class="field"><label>Gaano karami?</label>
  <select id="dcSize"><option>1 Spray Bottle</option><option>1 Timba</option></select></div>
 <button class="btn" onclick="dcMix()">Kalkulahin ang Tama</button>
 <div id="dcErr"></div>
</div>
""",
result=r"""
<div class="card">
 <h3 style="margin-top:0">Sukat ng Halo</h3>
 <div id="dcMix"></div>
 <div class="alert warn" id="dcSafety" style="margin-top:10px"></div>
 <button class="btn ok" onclick="dcSave()">\U0001F4BE I-save ang Recipe</button>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F9FC</div>
 <h2>Recipe Saved</h2>
 <div id="dcSaved"></div>
 <button class="btn ghost" onclick="show('input')">\U0001F9FC Bagong Mix</button>
</div>
""",
js=r"""
var DC_RECIPES={
 'Mamantikang Kusina':{1:{Tubig:'1 tasa',Suka:'1/2 tasa',Dishwashing:'1 kutsara'},2:{Tubig:'1 timba',Suka:'2 tasa',Dishwashing:'4 kutsara'},safety:'Iwasang pagsamahin ang suka at bleach \u2014 nakakalason na gas.'},
 'Salamin':{1:{Tubig:'2 tasa',Suka:'2 kutsara'},2:{Tubig:'1 timba',Suka:'1/2 tasa'},safety:'Huwag gamitan ng abrasive na panglinis sa salamin.'},
 'Mantsa sa Damit':{1:{Tubig:'1 tasa',BakingSoda:'2 kutsara',Dishwashing:'1 kutsara'},2:{Tubig:'1 timba',BakingSoda:'1/2 tasa',Dishwashing:'4 kutsara'},safety:'I-test muna sa gilid ng damit bago buong laba.'},
 'Amoy sa Banyo':{1:{Tubig:'1 tasa',Calamansi:'5 piraso',BakingSoda:'1 kutsara'},2:{Tubig:'1 timba',Calamansi:'20 piraso',BakingSoda:'4 kutsara'},safety:'Huwag pagsamahin ang calamansi sa bleach.'}
};
var DC_KEY='mcsn_cleaningmix';var dcData=Store.get(DC_KEY,[]);var dcCur=null;
function dcRender(){var el=$('#dcCount');el.textContent=dcData.length;
  $('#dcList').innerHTML=dcData.length?dcData.slice().reverse().map(function(r){return '<div class="item"><div class="ic">\U0001F9FC</div><div class="grow"><div class="t">'+r.what+'</div><div class="s">'+r.size+'</div></div></div>';}).join(''):'<div class="mut small">Wala pang recipe.</div>';}
function dcMix(){
  var what=$('#dcWhat').value,size=$('#dcSize').value,sz=size==='1 Spray Bottle'?1:2;
  var mix=DC_RECIPES[what][sz];
  $('#dcMix').innerHTML=Object.keys(mix).map(function(k){return '<div class="kv"><span>'+k.replace('BakingSoda','Baking Soda')+'</span><b>'+mix[k]+'</b></div>';}).join('');
  $('#dcSafety').textContent='\u26A0\uFE0F Safety: '+DC_RECIPES[what].safety;
  dcCur={what:what,size:size,mix:mix,safety:DC_RECIPES[what].safety};toast('Nakalkula na');show('result');
}
function dcSave(){if(!dcCur)return;dcData.push(dcCur);Store.set(DC_KEY,dcData);dcRender();
  $('#dcSaved').innerHTML=Object.keys(dcCur.mix).map(function(k){return '<div class="kv"><span>'+k.replace('BakingSoda','Baking Soda')+'</span><b>'+dcCur.mix[k]+'</b></div>';}).join('');
  toast('Recipe saved');show('done');}
dcRender();
""")

# ---------------- GROK BATCH: 5 Trending Apps ----------------
define(name="Bingo Card Maker PRO", icon="\U0001F3B1", tag="Custom bingo card + QR", batch="Grok", lib_file="qrcode.min.js",
home=r"""
<div class="hero"><div class="mut small">Trending Themes</div><div class="big">5</div><div class="mut small">Piliin ang tema ng bingo</div></div>
<h3>Trending Themes</h3>
<div class="chips" id="bgCats">
 <div class="chip" onclick="bgCat(this)" data-cat="Family">Family</div>
 <div class="chip" onclick="bgCat(this)" data-cat="Office">Office</div>
 <div class="chip" onclick="bgCat(this)" data-cat="Online Party">Online Party</div>
 <div class="chip" onclick="bgCat(this)" data-cat="Christmas">Christmas</div>
 <div class="chip" onclick="bgCat(this)" data-cat="Birthday">Birthday</div>
</div>
<button class="btn" data-go="input" style="margin-top:12px">\U0001F3B1 Gumawa ng Card</button>
""",
input=r"""
<div class="card">
 <div class="field"><label>Title ng Card</label><input id="bgTitle" placeholder="Hal: Reyes Family Bingo"></div>
 <div class="field"><label>Free Space</label><select id="bgFree"><option>FREE</option><option>Wala</option></select></div>
 <div class="field"><label>Number Style</label><select id="bgStyle"><option>1-75 Bingo</option><option>1-25 Simple</option></select></div>
 <button class="btn" onclick="bgGen()">\U0001F3B2 Generate Card</button>
 <div id="bgErr"></div>
</div>
""",
result=r"""
<div class="card">
 <div class="center mut small" id="bgRTitle">\u2014</div>
 <div id="bgGrid" style="display:grid;grid-template-columns:repeat(5,1fr);gap:6px;margin:12px 0"></div>
 <div id="bgQR" class="center"></div>
 <button class="btn" onclick="bgSave()">\U0001F5A8 Print / Share</button>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F389</div>
 <h2>Naka-share na!</h2>
 <div class="mut small">"Join our bingo later!"</div>
 <div class="kv"><span>Card</span><b id="bgDoneTitle">\u2014</b></div>
 <button class="btn ghost" onclick="show('input')">\U0001F3B1 Bagong Card</button>
</div>
""",
js=r"""
var BG_KEY='mcsn_bingo';var bgData=Store.get(BG_KEY,[]);var bgCur=null,bgCatSel=null;
function bgCat(el){bgCatSel=el.dataset.cat;$$('#bgCats .chip').forEach(function(c){c.classList.remove('on');});el.classList.add('on');}
function bgGen(){
  var t=val('bgTitle');if(!t){$('#bgErr').innerHTML='<div class="alert err">Ilagay ang title</div>';return;}
  $('#bgErr').innerHTML='';
  var max=$('#bgStyle').value==='1-75 Bingo'?75:25;
  var pool=[];for(var i=1;i<=max;i++)pool.push(i);
  pool.sort(function(){return Math.random()-0.5;});
  var cells=[],k=0;for(var r=0;r<5;r++){for(var c=0;c<5;c++){cells.push((r===2&&c===2&&$('#bgFree').value==='FREE')?'FREE':pool[k++]);}}
  bgCur={title:t,cat:bgCatSel||'Family',cells:cells};
  $('#bgRTitle').textContent=t+' \u2022 '+(bgCatSel||'Family');
  $('#bgGrid').innerHTML=cells.map(function(v){return '<div style="aspect-ratio:1;display:flex;align-items:center;justify-content:center;border-radius:10px;font-weight:700;font-size:13px;background:'+(v==='FREE'?'linear-gradient(135deg,var(--pri),var(--ok))':'var(--card2)')+';border:1px solid var(--line)">'+v+'</div>';}).join('');
  var qr='';if(typeof qrcode!=='undefined'){try{var q=qrcode(0,'M');q.addData('BINGO: '+t);q.make();qr='<img class="qr" style="max-width:140px" src="'+q.createDataURL(5,8)+'">';}catch(e){}}
  $('#bgQR').innerHTML=qr;
  show('result');
}
function bgSave(){if(!bgCur)return;bgData.push({title:bgCur.title,cat:bgCur.cat});Store.set(BG_KEY,bgData);
  $('#bgDoneTitle').textContent=bgCur.title;toast('Card ready to share');show('done');}
""")

define(name="Game Score Tracker PRO", icon="\U0001F3C0", tag="Real-time scoreboard", batch="Grok",
home=r"""
<div class="hero"><div class="mut small">Trending Games</div><div class="big" id="gsCount">0</div><div class="mut small">Natapos na laro</div></div>
<button class="btn" data-go="input">\U0001F3C0 Simulan ang Score</button>
<h3>Mga Laro</h3><div id="gsList"></div>
""",
input=r"""
<div class="card">
 <div class="field"><label>Uri ng Laro</label>
  <select id="gsType"><option>Basketball</option><option>Volleyball</option><option>Mobile Game</option><option>Board Game</option></select></div>
 <div class="field"><label>Team A</label><input id="gsA" placeholder="Hal: Team Red"></div>
 <div class="field"><label>Team B</label><input id="gsB" placeholder="Hal: Team Blue"></div>
 <button class="btn" onclick="gsStart()">Simulan</button>
 <div id="gsErr"></div>
</div>
""",
result=r"""
<div class="card">
 <div class="row center" style="text-align:center">
  <div><div class="mut small" id="gsNameA">A</div><div class="big" id="gsScoreA">0</div>
   <button class="btn sm" style="width:100%" onclick="gsAdd('A',1)">+1</button>
   <button class="btn ghost sm" style="width:100%;margin-top:6px" onclick="gsAdd('A',2)">+2</button></div>
  <div><div class="mut small" id="gsNameB">B</div><div class="big" id="gsScoreB">0</div>
   <button class="btn sm" style="width:100%" onclick="gsAdd('B',1)">+1</button>
   <button class="btn ghost sm" style="width:100%;margin-top:6px" onclick="gsAdd('B',2)">+2</button></div>
 </div>
 <button class="btn ok" style="margin-top:12px" onclick="gsFinish()">\U0001F3C6 Tapusin ang Laro</button>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F3C6</div>
 <h2 id="gsWinner">\u2014</h2>
 <div class="kv"><span id="gsDFinalA">A</span><b id="gsFSA">0</b></div>
 <div class="kv"><span id="gsDFinalB">B</span><b id="gsFSB">0</b></div>
 <div class="mut small" style="margin-top:8px">"GG!"</div>
 <button class="btn ghost" onclick="gsNew()">\u2795 Bagong Laro</button>
</div>
""",
js=r"""
var GS_KEY='mcsn_scores';var gsData=Store.get(GS_KEY,[]);var gsCur=null;
function gsRender(){var el=$('#gsCount');el.textContent=gsData.length;
  $('#gsList').innerHTML=gsData.length?gsData.slice().reverse().map(function(g){return '<div class="item"><div class="ic">\U0001F3C0</div><div class="grow"><div class="t">'+g.a+' '+g.sa+' \u2013 '+g.sb+' '+g.b+'</div><div class="s">'+g.type+' \u2022 Panalo: '+g.winner+'</div></div></div>';}).join(''):'<div class="mut small">Wala pang laro.</div>';}
function gsStart(){
  var a=val('gsA'),b=val('gsB');
  if(!a||!b){$('#gsErr').innerHTML='<div class="alert err">Ilagay ang pangalan ng dalawang team</div>';return;}
  $('#gsErr').innerHTML='';gsCur={type:$('#gsType').value,a:a,b:b,sa:0,sb:0};
  $('#gsNameA').textContent=a;$('#gsNameB').textContent=b;$('#gsScoreA').textContent=0;$('#gsScoreB').textContent=0;
  resetForm(['gsA','gsB']);show('result');
}
function gsAdd(t,n){if(!gsCur)return;if(t==='A')gsCur.sa+=n;else gsCur.sb+=n;
  $('#gsScoreA').textContent=gsCur.sa;$('#gsScoreB').textContent=gsCur.sb;}
function gsFinish(){if(!gsCur)return;
  var w=gsCur.sa===gsCur.sb?'Tabla':(gsCur.sa>gsCur.sb?gsCur.a:gsCur.b);
  gsCur.winner=w;gsData.push(gsCur);Store.set(GS_KEY,gsData);gsRender();
  $('#gsWinner').textContent=w==='Tabla'?'Tabla!':(w+' ang Panalo!');
  $('#gsDFinalA').textContent=gsCur.a;$('#gsFSA').textContent=gsCur.sa;
  $('#gsDFinalB').textContent=gsCur.b;$('#gsFSB').textContent=gsCur.sb;
  toast('Final: '+w);show('done');}
function gsNew(){gsCur=null;resetForm(['gsA','gsB']);show('input');}
gsRender();
""")

define(name="Course TikTok Selling Basics PRO", icon="\U0001F3AC", tag="15-sec video + caption", batch="Grok",
home=r"""
<div class="hero"><div class="mut small">Trending 15-sec Styles</div><div class="big">5</div><div class="mut small">Piliin ang style ng video</div></div>
<h3>Video Formats</h3>
<div id="tkList"></div>
<button class="btn" data-go="input" style="margin-top:12px">\U0001F3AC Gumawa ng Caption</button>
""",
input=r"""
<div class="card">
 <div class="field"><label>Style</label>
  <select id="tkStyle"><option>Hook: Problema-Solusyon</option><option>Before-After</option><option>Unboxing</option><option>Testimonial</option><option>Trend + Product</option></select></div>
 <div class="field"><label>Pangalan ng Produkto</label><input id="tkProd" placeholder="Hal: Sabon Puti"></div>
 <div class="field"><label>Presyo</label><input id="tkPrice" placeholder="Hal: 99"></div>
 <button class="btn" onclick="tkGen()">\U0001F4DD Generate Caption</button>
 <div id="tkErr"></div>
</div>
""",
result=r"""
<div class="card">
 <h3 style="margin-top:0">Ready Caption</h3>
 <div class="alert ok" id="tkCaption" style="line-height:1.7"></div>
 <h3>Hashtags</h3>
 <div class="chips" id="tkTags"></div>
 <button class="btn ok" style="margin-top:12px" onclick="tkCopy()">\U0001F4CB Copy Caption</button>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F680</div>
 <h2>Ready to Post!</h2>
 <div class="mut small">Sample TikTok Preview</div>
 <div class="alert ok" id="tkPreview" style="text-align:left;margin-top:10px"></div>
 <button class="btn ghost" onclick="show('input')">\U0001F3AC Bagong Caption</button>
</div>
""",
js=r"""
var TK_KEY='mcsn_tiktok';var tkData=Store.get(TK_KEY,[]);
var TK_TAGS=['#MCSN','#TikTokSelling','#PinoyNegosyo','#TikTokShopPH','#FYP','#ShopeeFinds','#BudgetFinds'];
function tkRender(){var el=$('#tkList');
  el.innerHTML=TK_TAGS.slice(0,5).map(function(t){return '<div class="item"><div class="ic">\U0001F3AC</div><div class="grow"><div class="t">'+t+'</div><div class="s">15-sec video idea</div></div></div>';}).join('');}
function tkGen(){
  var st=$('#tkStyle').value,p=val('tkProd'),pr=val('tkPrice');
  if(!p||!pr){$('#tkErr').innerHTML='<div class="alert err">Punan ang produkto at presyo</div>';return;}
  $('#tkErr').innerHTML='';
  var cap='\U0001F525 '+(st.indexOf('Hook')===0?'Sobrang sulit nito!':st)+'\n\n'+p+' \u2014 '+(pr.indexOf('\u20B1')===0?pr:'\u20B1'+pr)+' lang!\n\n'+(st.indexOf('Before')===0?'Tingnan ang bago at pagkatapos!':(st.indexOf('Unboxing')===0?'Unboxing natin ngayon!':'Sulit na sulit, subukan na!'))+'\n\nOrder na sa DM o TikTok Shop! \U0001F6D2';
  $('#tkCaption').textContent=cap;
  $('#tkTags').innerHTML=TK_TAGS.map(function(t){return '<div class="chip">'+t+'</div>';}).join('');
  tkData.push({style:st,prod:p,price:pr,caption:cap});Store.set(TK_KEY,tkData);
  $('#tkPreview').textContent=cap;toast('Caption ready');show('result');
}
function tkCopy(){toast('Caption copied!');show('done');}
tkRender();
""")

define(name="Course GCash / Maya Guide PRO", icon="\U0001F4B3", tag="Step-by-step + tips", batch="Grok",
home=r"""
<div class="hero"><div class="mut small">Trending Guides</div><div class="big">4</div><div class="mut small">Safe na cashless tips</div></div>
<h3>Topics</h3>
<div class="chips" id="gcCats">
 <div class="chip" onclick="gcPick(this)" data-cat="Send Money">Send Money</div>
 <div class="chip" onclick="gcPick(this)" data-cat="Pay Bills">Pay Bills</div>
 <div class="chip" onclick="gcPick(this)" data-cat="Business QR">Business QR</div>
 <div class="chip" onclick="gcPick(this)" data-cat="Savings">Savings</div>
</div>
<button class="btn" data-go="input" style="margin-top:12px">\U0001F4B3 Simulan ang Guide</button>
""",
input=r"""
<div class="card">
 <h3 style="margin-top:0" id="gcTopic">Guide</h3>
 <div id="gcChecks"></div>
 <button class="btn" onclick="gcDone()">Tapusin ang Guide</button>
 <div id="gcErr"></div>
</div>
""",
result=r"""
<div class="card">
 <h3 style="margin-top:0">Step-by-step</h3>
 <div id="gcSteps"></div>
 <div class="alert ok" id="gcTip" style="margin-top:10px"></div>
 <button class="btn ok" onclick="gcShare()">\u2705 Done / I-share</button>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F4B3</div>
 <h2>Guide Shared</h2>
 <div class="mut small">"Safe na! Share sa pamilya."</div>
 <div id="gcShared" style="margin-top:10px"></div>
 <button class="btn ghost" onclick="show('home')">\U0001F4B3 Bagong Topic</button>
</div>
""",
js=r"""
var GC_GUIDES={
 'Send Money':{steps:['Buksan ang GCash/Maya app','Pindutin ang "Send Money"','Ilagay ang number o QR ng padadalhan','I-type ang halaga','I-confirm at i-enter ang MPIN'],tip:'Doble-check ang number bago mag-send. Hindi na maibabalik ang maling padala.'},
 'Pay Bills':{steps:['Pumili ng "Pay Bills"','Hanapin ang biller (Meralco, Maynilad)','Ilagay ang account number','I-type ang halaga','I-confirm ang bayad'],tip:'I-save ang resibo (screenshot) bilang patunay ng bayad.'},
 'Business QR':{steps:['Pumili ng "Accept Payment / QR"','I-set ang pangalan ng negosyo','Ipakita ang QR sa customer','Hintayin ang confirmation','I-check ang natanggap sa dashboard'],tip:'Gawing malinaw ang QR \u2014 iwas sa pekeng QR ng scammer.'},
 'Savings':{steps:['Buksan ang "Save Money / GSave"','Pumili ng goal o fund','I-set ang auto-deposit','Mag-ipon kada sahod','I-check ang tubo'],tip:'Magtabi muna ng savings bago gastos \u2014 bayad sa sarili.'}
};
var GC_KEY='mcsn_gcash';var gcCur=null,gcSel=null;
function gcPick(el){gcSel=el.dataset.cat;$$('#gcCats .chip').forEach(function(c){c.classList.remove('on');});el.classList.add('on');
  gcCur=GC_GUIDES[gcSel];$('#gcTopic').textContent=gcSel+' Guide';
  $('#gcChecks').innerHTML=gcCur.steps.map(function(s,i){return '<div class="chk" onclick="gcToggle(this)"><div class="box"></div><div class="grow"><div class="t">'+s+'</div></div></div>';}).join('');
  show('input');}
function gcToggle(el){el.classList.toggle('on');el.querySelector('.box').textContent=el.classList.contains('on')?'\u2714':'';}
function gcDone(){if(!gcCur){$('#gcErr').innerHTML='<div class="alert err">Pumili muna ng topic</div>';return;}
  $('#gcErr').innerHTML='';
  $('#gcSteps').innerHTML=gcCur.steps.map(function(s,i){return '<div class="item"><div class="ic">'+(i+1)+'</div><div class="grow"><div class="t">'+s+'</div></div></div>';}).join('');
  $('#gcTip').textContent='\U0001F4A1 Tip: '+gcCur.tip;show('result');}
function gcShare(){$('#gcShared').innerHTML=gcCur.steps.map(function(s,i){return '<div class="kv"><span>Step '+(i+1)+'</span><b>'+s+'</b></div>';}).join('');toast('Guide shared');show('done');}
""")

define(name="Course Basic English for Work PRO", icon="\U0001F4AC", tag="Ready phrases + examples", batch="Grok",
home=r"""
<div class="hero"><div class="mut small">Trending Lessons</div><div class="big">4</div><div class="mut small">Ready-to-use work English</div></div>
<h3>Lessons</h3>
<div class="chips" id="enCats">
 <div class="chip" onclick="enPick(this)" data-cat="Interview">Interview</div>
 <div class="chip" onclick="enPick(this)" data-cat="Email">Email</div>
 <div class="chip" onclick="enPick(this)" data-cat="Daily Chat">Daily Chat</div>
 <div class="chip" onclick="enPick(this)" data-cat="Customer">Customer</div>
</div>
<button class="btn" data-go="input" style="margin-top:12px">\U0001F4AC Mag-practice</button>
""",
input=r"""
<div class="card">
 <div class="field"><label>Lesson</label>
  <select id="enLesson"></select></div>
 <button class="btn" onclick="enPractice()">I-practice ang Phrase</button>
 <div id="enErr"></div>
</div>
""",
result=r"""
<div class="card">
 <h3 style="margin-top:0">Ready Sentence</h3>
 <div class="alert ok" id="enSentence" style="font-size:15px"></div>
 <div class="mut small" id="enExample" style="margin-top:10px"></div>
 <button class="btn ok" onclick="enSave()">\U0001F4BE I-save ang Phrase</button>
</div>
""",
done=r"""
<div class="card center">
 <div style="font-size:52px">\U0001F4AC</div>
 <h2>Saved!</h2>
 <div class="mut small">"Use this at work!"</div>
 <div id="enSaved" style="margin-top:10px"></div>
 <button class="btn ghost" onclick="show('input')">\U0001F4AC Bagong Phrase</button>
</div>
""",
js=r"""
var EN_PHRASES={
 Interview:['I am a fast learner and I work well under pressure.','I believe my skills match what you are looking for.','Can you tell me more about the role?'],
 Email:['Dear Sir/Madam, I hope this email finds you well.','Please find the attached file for your reference.','Thank you for your prompt response.'],
 'Daily Chat':['Good morning! How are you today?','I will get back to you shortly.','Could you please clarify this for me?'],
 Customer:['Thank you for reaching out to us.','I apologize for the inconvenience.','Is there anything else I can help you with?']
};
var EN_KEY='mcsn_english';var enData=Store.get(EN_KEY,[]);var enCur=null,enCat=null;
function enRender(){var opts=[];Object.keys(EN_PHRASES).forEach(function(k){EN_PHRASES[k].forEach(function(p,i){opts.push('<option value="'+k+'|'+i+'">'+k+': '+p.slice(0,32)+'...</option>');});});
  $('#enLesson').innerHTML=opts.join('');}
function enPick(el){enCat=el.dataset.cat;$$('#enCats .chip').forEach(function(c){c.classList.remove('on');});el.classList.add('on');show('input');}
function enPractice(){
  var v=$('#enLesson').value.split('|'),k=v[0],i=parseInt(v[1],10);enCur=EN_PHRASES[k][i];
  $('#enSentence').textContent=enCur;$('#enExample').textContent='Halimbawa ng paggamit sa '+k+' na sitwasyon.';toast('Practice na!');show('result');
}
function enSave(){if(!enCur)return;enData.push(enCur);Store.set(EN_KEY,enData);
  $('#enSaved').innerHTML='<div class="kv"><span>Phrase</span><b>'+enCur+'</b></div>';toast('Saved');show('done');}
enRender();
""")

# ---------------- BUILD DRIVER ----------------
HUB_TEMPLATE = """<!DOCTYPE html>
<html lang="fil">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MCSN AppFactory - %(count)s Apps</title>
<style>%(css)s
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.appcard{background:var(--glass);border:1px solid var(--brd);border-radius:20px;padding:15px;text-decoration:none;color:var(--txt);display:flex;flex-direction:column;gap:9px;-webkit-backdrop-filter:var(--blur);backdrop-filter:var(--blur);box-shadow:0 10px 30px rgba(0,0,0,.35),inset 0 1px 0 rgba(255,255,255,.14)}
.appcard img{width:46px;height:46px;border-radius:14px;box-shadow:0 8px 20px rgba(0,0,0,.4)}
.appcard .n{font-size:13px;font-weight:700;line-height:1.25}
.appcard .t{font-size:10px;color:var(--mut)}
</style></head>
<body>
<div class="bg"><span></span><span></span><span></span></div>
<div class="wrap">
 <header class="app"><div class="logo" style="display:flex;align-items:center;justify-content:center;font-size:24px">\U0001F3ED</div><div><h1>MCSN AppFactory</h1><div class="tag">%(count)s Standalone Offline HTML Apps</div></div></header>
 <div class="hero"><div class="mut small">Deepseek + Gemini + Grok</div><div class="big">%(count)s Apps</div><div class="mut small">Mobile-first \u2022 Offline \u2022 Vanilla JS</div></div>
 <a class="btn" href="downloads.html" style="text-decoration:none;margin-bottom:10px;display:block;text-align:center">\u2B07 Downloads \u2014 Install + ZIP bawat app</a>
 <a class="btn ghost" href="imahe-overview.html" style="text-decoration:none;margin-bottom:14px;display:block;text-align:center">\U0001F5BC Imahe Overview (4 screenshots bawat app)</a>
 <div class="grid">%(cards)s</div>
 <div class="foot">FOUNDER DECIDES \u2022 REX BUILDS \u2022 SOF COMMUNICATES \u2022 SYSTEM RECORDS</div>
</div>
</body></html>"""

SHOT_LABELS=[("1-home","Home"),("2-ginagamit","Ginagamit"),("3-resulta","Resulta"),("4-tapos","Tapos Na")]

PREVIEW_CSS = BASE_CSS + r"""
.shot{margin-bottom:14px}
.shot .lbl{font-size:12px;color:var(--mut);margin-bottom:6px;font-weight:600}
.frame{position:relative;border:1px dashed var(--line);border-radius:16px;overflow:hidden;background:var(--card);min-height:150px;display:flex;align-items:center;justify-content:center}
.frame img{width:100%;display:block}
.frame .ph{display:none;flex-direction:column;align-items:center;gap:6px;color:var(--mut);font-size:12px;padding:26px}
.frame.empty .ph{display:flex}
.grid4{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.mini .frame{min-height:90px}
.mini .lbl{font-size:10px}
"""

PREVIEW_TEMPLATE = """<!DOCTYPE html>
<html lang="fil">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(name)s - Imahe Preview</title>
<style>%(css)s</style>
</head>
<body>
<div class="wrap">
 <header class="app"><div class="logo">%(icon)s</div><div><h1>%(name)s</h1><div class="tag">Imahe Preview \u2022 %(tag)s</div></div></header>
 <div class="hero"><div class="mut small">App #%(num)s</div><div class="big">4 Screenshots</div><div class="mut small">Home \u2022 Ginagamit \u2022 Resulta \u2022 Tapos Na</div></div>
 %(shots)s
 <div class="card tight mut small">Ilagay ang mga larawan sa <b>images/</b> folder gamit ang pangalan: <b>1-home.png</b>, <b>2-ginagamit.png</b>, <b>3-resulta.png</b>, <b>4-tapos.png</b>. Awtomatikong lalabas dito pag ni-refresh.</div>
 <div class="foot">FOUNDER DECIDES \u2022 REX BUILDS \u2022 SOF COMMUNICATES \u2022 SYSTEM RECORDS</div>
</div>
</body></html>"""

OVERVIEW_TEMPLATE = """<!DOCTYPE html>
<html lang="fil">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Imahe Overview - Extract Image pc by pc</title>
<style>%(css)s
.ovapp{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:12px;margin-bottom:14px}
.ovhead{display:flex;align-items:center;gap:8px;margin-bottom:10px}
.ovhead .e{font-size:20px}
.ovhead .n{font-size:13px;font-weight:700}
.ovhead .i{font-size:10px;color:var(--mut)}
</style>
</head>
<body>
<div class="wrap">
 <header class="app"><div class="logo">\U0001F5BC</div><div><h1>Imahe Overview</h1><div class="tag">Extract Image pc by pc \u2022 %(count)s Apps</div></div></header>
 <div class="hero"><div class="mut small">Kabuuan</div><div class="big">%(count)s Apps</div><div class="mut small">Bawat app: 4 screenshots (Home/Ginagamit/Resulta/Tapos Na)</div></div>
 %(apps)s
 <div class="foot">FOUNDER DECIDES \u2022 REX BUILDS \u2022 SOF COMMUNICATES \u2022 SYSTEM RECORDS</div>
</div>
</body></html>"""

def shots_block(folder_prefix, mini=False):
    out=[]
    for fname,label in SHOT_LABELS:
        out.append('<div class="shot%s"><div class="lbl">%s</div><div class="frame" id="fr-%s"><img src="%simages/%s.png" alt="%s" onerror="this.remove();this.parentNode.classList.add(\'empty\')"><div class="ph">\U0001F5BC<br>%s.png</div></div></div>'%((' mini' if mini else ''),label,fname,folder_prefix,fname,label,fname))
    return ''.join(out)

def build_previews(apps_info):
    for num,app,folder in apps_info:
        html=PREVIEW_TEMPLATE%dict(css=PREVIEW_CSS,name=app['name'],icon=app['icon'],tag=app['tag'],num=num,shots=shots_block(''))
        with open(os.path.join(OUT,folder,"preview.html"),'w',encoding='utf-8') as f:
            f.write(deunicode(html))
    blocks=[]
    for num,app,folder in apps_info:
        blocks.append('<div class="ovapp"><div class="ovhead"><div class="e">%s</div><div><div class="n">%d. %s</div><div class="i">%s \u2022 <a href="%s/preview.html" style="color:var(--pri2)">buksan ang preview</a></div></div></div><div class="grid4">%s</div></div>'%(app['icon'],num,app['name'],app['tag'],folder,shots_block(folder+'/',mini=True)))
    with open(os.path.join(OUT,"imahe-overview.html"),'w',encoding='utf-8') as f:
        f.write(deunicode(OVERVIEW_TEMPLATE%dict(css=PREVIEW_CSS,count=len(apps_info),apps=''.join(blocks))))

DOWNLOADS_TEMPLATE = """<!DOCTYPE html>
<html lang="fil">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MCSN AppFactory - Downloads</title>
<style>%(css)s
.dlcard{background:var(--glass);border:1px solid var(--brd);border-radius:20px;padding:15px;margin-bottom:12px;-webkit-backdrop-filter:var(--blur);backdrop-filter:var(--blur);box-shadow:0 10px 30px rgba(0,0,0,.35),inset 0 1px 0 rgba(255,255,255,.14)}
.dlhead{display:flex;align-items:center;gap:11px;margin-bottom:11px}
.dlhead .e{font-size:24px}
.dlhead .n{font-size:14px;font-weight:700}
.dlhead .t{font-size:11px;color:var(--mut)}
.dlbtns{display:flex;gap:8px;flex-wrap:wrap}
.dlbtns a{flex:1;min-width:130px;text-align:center;text-decoration:none}
</style>
</head>
<body>
<div class="bg"><span></span><span></span><span></span></div>
<div class="wrap">
 <header class="app"><div class="logo" style="display:flex;align-items:center;justify-content:center;font-size:22px">\u2B07</div><div><h1>Downloads</h1><div class="tag">%(count)s Apps \u2022 Installable + ZIP</div></div></header>
 <div class="hero"><div class="mut small">%(count)s Apps \u2022 Bawat isa</div><div class="big">Install + Download</div><div class="mut small">Buksan sa Chrome para sa "Add to Home Screen"</div></div>
 <a class="btn ghost" href="index.html" style="text-decoration:none;margin-bottom:10px">\u2190 Bumalik sa Hub</a>
 <a class="btn" href="downloads/ALL-%(count)s-Apps.zip" style="text-decoration:none;display:block;text-align:center;margin-bottom:14px">\u2B07 DOWNLOAD LAHAT \u2014 1 ZIP (%(count)s apps)</a>
 %(cards)s
 <div class="foot">FOUNDER DECIDES \u2022 REX BUILDS \u2022 SOF COMMUNICATES \u2022 SYSTEM RECORDS</div>
</div>
</body></html>"""

def _hex(c):
    c=c.lstrip('#'); return tuple(int(c[i:i+2],16) for i in (0,2,4))

def _star(d,cx,cy,r,fill):
    import math
    pts=[]
    for i in range(10):
        ang=-math.pi/2+i*math.pi/5
        rr=r if i%2==0 else r*0.42
        pts.append((cx+rr*math.cos(ang),cy+rr*math.sin(ang)))
    d.polygon(pts,fill=fill)

def make_icon(path, size, letter=None, bg1=None, bg2=None, emoji=None, name=None):
    icons.themed_icon(path, size, emoji, name or letter or "MCSN")

def write_pwa(app, folder, d, idx):
    name=app['name']; short=name[:12]
    letter=re.sub(r'[^A-Za-z]','',name)[:1] or str(idx)
    icon_dir=os.path.join(d,"icons"); os.makedirs(icon_dir,exist_ok=True)
    for s in (192,512):
        make_icon(os.path.join(icon_dir,"icon-%d.png"%s), s, letter, emoji=app.get('icon'), name=name)
    manifest={
      "name":name, "short_name":short, "start_url":"./index.html",
      "scope":"./", "display":"standalone", "orientation":"portrait",
      "background_color":"#0f1220", "theme_color":"#0038A8", "lang":"fil",
      "description":"MCSN AppFactory - %s. Offline HTML app."%app['tag'],
      "icons":[
        {"src":"icons/icon-192.png","sizes":"192x192","type":"image/png","purpose":"any maskable"},
        {"src":"icons/icon-512.png","sizes":"512x512","type":"image/png","purpose":"any maskable"}
      ]
    }
    with open(os.path.join(d,"manifest.webmanifest"),'w',encoding='utf-8') as f:
        json.dump(manifest,f,ensure_ascii=False,indent=2)
    sw=("const CACHE='mcsn-%s-v1';\n"
        "const ASSETS=['./','./index.html','./manifest.webmanifest','./icons/icon-192.png','./icons/icon-512.png'];\n"
        "self.addEventListener('install',e=>{self.skipWaiting();e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS)));});\n"
        "self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))));});\n"
        "self.addEventListener('fetch',e=>{e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request).then(resp=>{const cp=resp.clone();caches.open(CACHE).then(c=>c.put(e.request,cp));return resp;}).catch(()=>caches.match('./index.html'))));});\n")%folder
    with open(os.path.join(d,"sw.js"),'w',encoding='utf-8') as f:
        f.write(sw)
    head=('<link rel="manifest" href="manifest.webmanifest">\n'
          '<link rel="icon" href="icons/icon-192.png">\n'
          '<link rel="apple-touch-icon" href="icons/icon-192.png">\n'
          '<meta name="apple-mobile-web-app-capable" content="yes">\n'
          '<meta name="mobile-web-app-capable" content="yes">\n'
          '<meta name="apple-mobile-web-app-title" content="%s">\n'%name)
    idx=idx.replace('</head>', head+'</head>')
    script=("<script>if('serviceWorker' in navigator){window.addEventListener('load',function(){navigator.serviceWorker.register('sw.js').catch(function(){});});}</script>\n")
    idx=idx.replace('</body>', script+'</body>')
    return idx

def slug(name):
    s=name.lower()
    s=re.sub(r'[^a-z0-9]+','-',s).strip('-')
    return s

def deunicode(s):
    s=re.sub(r'\\U([0-9a-fA-F]{8})',lambda m:chr(int(m.group(1),16)),s)
    s=re.sub(r'\\u([0-9a-fA-F]{4})',lambda m:chr(int(m.group(1),16)),s)
    return s

def build():
    if os.path.isdir(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    dl_dir=os.path.join(OUT,"downloads")
    os.makedirs(dl_dir)
    cards=[]
    dl_cards=[]
    apps_info=[]
    for i,app in enumerate(APPS,1):
        folder="%02d-%s"%(i,slug(app['name']))
        apps_info.append((i,app,folder))
        d=os.path.join(OUT,folder)
        os.makedirs(os.path.join(d,"images"))
        libfile=app.get('lib_file')
        libhtml=''
        if libfile:
            libpath=os.path.join(ROOT,libfile)
            if os.path.exists(libpath):
                with open(libpath,encoding='utf-8') as f: libhtml='<script>'+f.read()+'</script>'
        html=page(app)
        if libhtml: html=html.replace('<script>'+RUNTIME_JS+'</script>','<script>'+RUNTIME_JS+'</script>'+libhtml)
        html=deunicode(html)
        html=write_pwa(app,folder,d,html)
        with open(os.path.join(d,"index.html"),'w',encoding='utf-8') as f: f.write(html)
        with open(os.path.join(d,"README.md"),'w',encoding='utf-8') as f:
            f.write("# %s\n\nMCSN AppFactory \u2022 %s Batch (App #%d)\n\n"% (app['name'],app.get('batch','Deepseek'),i))
            f.write("- Screens: Home / Input / Resulta / Tapos Na\n")
            f.write("- Logic: %s\n"% app['tag'])
            f.write("- Offline, mobile-first, vanilla JS (localStorage)\n\n")
            f.write("## Install (PWA)\n")
            f.write("I-serve ang folder na ito (hal. `python3 -m http.server`), buksan sa Chrome, tapos **Add to Home Screen**.\n\n")
            f.write("## Images (para sa Gemini-generated screenshots)\n")
            f.write("Ilagay sa `images/` folder: `1-home.png`, `2-ginagamit.png`, `3-resulta.png`, `4-tapos.png`.\n")
        # per-app ZIP
        zip_name="%s.zip"%folder
        with zipfile.ZipFile(os.path.join(dl_dir,zip_name),'w',zipfile.ZIP_DEFLATED) as z:
            for root,_,files in os.walk(d):
                for fn in files:
                    fp=os.path.join(root,fn)
                    z.write(fp,os.path.join(folder,os.path.relpath(fp,d)))
        cards.append('<a class="appcard" href="%s/index.html"><img src="%s/icons/icon-192.png" alt=""><div class="n">%d. %s</div><div class="t">%s</div></a>'%(folder,folder,i,app['name'],app['tag']))
        dl_cards.append('<div class="dlcard"><div class="dlhead"><img src="%s/icons/icon-192.png" style="width:44px;height:44px;border-radius:13px;box-shadow:0 8px 20px rgba(0,0,0,.4)"><div><div class="n">%d. %s</div><div class="t">%s</div></div></div><div class="dlbtns"><a class="btn" href="%s/index.html">\u25B6 Buksan / Install</a><a class="btn ghost" href="downloads/%s">\u2B07 ZIP</a></div></div>'%(folder,i,app['name'],app['tag'],folder,zip_name))
    with open(os.path.join(OUT,"index.html"),'w',encoding='utf-8') as f:
        f.write(deunicode(HUB_TEMPLATE%dict(css=BASE_CSS,count=len(APPS),cards=''.join(cards))))
    with open(os.path.join(OUT,"downloads.html"),'w',encoding='utf-8') as f:
        f.write(deunicode(DOWNLOADS_TEMPLATE%dict(css=BASE_CSS,count=len(APPS),cards=''.join(dl_cards))))
    # all-in-one bundle of the per-app ZIPs (sits inside downloads/)
    all_name="ALL-%d-Apps.zip"%len(APPS)
    with zipfile.ZipFile(os.path.join(dl_dir,all_name),'w',zipfile.ZIP_DEFLATED) as z:
        for i,app,folder in apps_info:
            z.write(os.path.join(dl_dir,"%s.zip"%folder),"%s.zip"%folder)
    build_previews(apps_info)
    # master ZIP bundle (excludes the nested per-app downloads/ folder)
    zip_path=os.path.join(OUT,"MCSN-AppFactory-%d-Apps.zip"%len(APPS))
    with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
        for root,_,files in os.walk(OUT):
            if os.path.abspath(root).startswith(os.path.abspath(dl_dir)): continue
            for fn in files:
                fp=os.path.join(root,fn)
                z.write(fp,os.path.relpath(fp,OUT))
    print("Built %d apps -> %s"%(len(APPS),OUT))
    print("Per-app ZIPs -> %s (%d)"%(dl_dir,len(APPS)))
    print("Master ZIP -> %s"%zip_path)

if __name__=="__main__":
    build()
