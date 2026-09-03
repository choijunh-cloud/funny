const NS="http://www.w3.org/2000/svg";
const C={s1:"#BD871C",s2:"#00AB92",s3:"#9F7ED6",s4:"#D56E78",s5:"#00A2CE",
         up:"#E0574A",down:"#4A8FE0",ink:"#E8ECF5",ink2:"#9AA6BE",ink3:"#64708A",
         line:"#1F2942",line2:"#2C3852",surf:"#0F1524",surf2:"#141B2E"};
const MONO='"JetBrains Mono",monospace', SANS='"Noto Sans KR",sans-serif';
function svg(w,h){const s=document.createElementNS(NS,"svg");
  s.setAttribute("viewBox","0 0 "+w+" "+h);s.setAttribute("width",w);s.setAttribute("height",h);
  s.setAttribute("font-family",MONO);return s;}
function el(p,n,a){const e=document.createElementNS(NS,n);for(const k in a)e.setAttribute(k,a[k]);p.appendChild(e);return e;}
function tx(p,x,y,s,o){o=o||{};const t=el(p,"text",{x:x,y:y,fill:o.fill||C.ink2,
  "font-size":o.fs||10.5,"text-anchor":o.ta||"start","font-family":o.ff||MONO,
  "font-weight":o.fw||400,"letter-spacing":o.ls||0});
  if(o.rot)t.setAttribute("transform","rotate("+o.rot+" "+x+" "+y+")");
  t.textContent=s;return t;}
function mount(id,s){const n=document.getElementById(id);if(n)n.appendChild(s);}
function fmt(v,d){return v.toLocaleString("en-US",{minimumFractionDigits:d||0,maximumFractionDigits:d||0});}
function sgn(v,d){return (v>0?"+":"")+fmt(v,d);}

/* ══ KPI ══ */
const KPI=[
 {k:"확률가중 연말",v:"7,383",s:"v1 7,338 → +45pt"},
 {k:"인상확률",v:"50%",s:"잭슨홀前 35 → 9/3 63 → 50"},
 {k:"S3 꼬리",v:"13%",s:"v1 20% → 7%p 축소"},
 {k:"S1 상단",v:"7,960",s:"v1 8,255 · 매물벽 −295"},
 {k:"하방 방어",v:"+2.15%p",s:"S3에서 지수보다 덜 빠진다"},
 {k:"포트 초과",v:"+0.24%p",s:"+1.09 → +0.84 → +0.24"},
 {k:"누적 판정",v:"21건",s:"확정9 부분6 기각3 미확인3"}];
(function(){const g=document.getElementById("kpis");
 KPI.forEach(function(d,i){const c=document.createElement("div");c.className="kpi";
  c.innerHTML='<div class="k">'+d.k+'</div><div class="v" style="color:'+
   [C.s2,C.s1,C.s2,C.s4,C.s2,C.s4,C.s5][i]+'">'+d.v+'</div><div class="s">'+d.s+'</div>';
  g.appendChild(c);});})();

/* ══ 00·1 델타 슬로프 ══ */
(function(){
 const D=[{n:"인상확률",a:63,b:50,u:"%",good:"down"},
          {n:"S3 꼬리확률",a:20,b:13,u:"%",good:"down"},
          {n:"확률가중 연말",a:7338,b:7383,u:"",good:"up",sc:1},
          {n:"S1 상단",a:8255,b:7960,u:"",good:"up",sc:1},
          {n:"브렌트",a:96,b:96,u:"$",good:"down"}];
 const W=520,L=118,R=118,T=52,RH=40,H=T+D.length*RH+34,s=svg(W,H);
 const pw=W-L-R;
 tx(s,L,T-28,"9/2~9/3",{ta:"middle",fill:C.ink3,fs:10,ff:SANS});
 tx(s,L+pw,T-28,"9/4~9/5",{ta:"middle",fill:C.ink3,fs:10,ff:SANS});
 D.forEach(function(d,i){
  const y=T+i*RH, ch=d.b-d.a, same=Math.abs(ch)<1e-9;
  const col= same?C.ink3 : (d.good==="up" ? (ch>0?C.s2:C.s4) : (ch<0?C.s2:C.s4));
  tx(s,L-12,y+4,d.n,{ta:"end",fill:C.ink,fs:11,ff:SANS,fw:500});
  el(s,"line",{x1:L,x2:L+pw,y1:y,y2:y,stroke:same?C.line:col,"stroke-width":same?1.2:2.2,
      "stroke-dasharray":same?"3 3":""});
  el(s,"circle",{cx:L,cy:y,r:4.5,fill:C.surf,stroke:C.ink3,"stroke-width":1.8});
  el(s,"circle",{cx:L+pw,cy:y,r:5.5,fill:same?C.surf:col,stroke:same?C.ink3:col,"stroke-width":1.8});
  tx(s,L,y-11,(d.sc?fmt(d.a):d.a+d.u),{ta:"middle",fill:C.ink3,fs:10});
  tx(s,L+pw,y-11,(d.sc?fmt(d.b):d.b+d.u),{ta:"middle",fill:col,fs:10.5,fw:700});
  tx(s,L+pw+12,y+4,same?"불변":(sgn(ch,0)+(d.sc?"pt":d.u+"p")),{fill:col,fs:10.5,fw:700});});
 tx(s,0,H-10,"초록 = 지수에 우호적 방향 · 회색 점선 = 변화 없음",{fill:C.ink3,fs:9.5,ff:SANS});
 mount("c-delta",s);})();

/* ══ 00·2 인상확률 경로 ══ */
(function(){
 const D=[{n:"잭슨홀 前",v:35,d:"8월 하순"},{n:"9/3 (표본일)",v:63,d:"매파 반영 정점"},
          {n:"월러 발언 後",v:50,d:"9/4~9/5"}];
 const W=520,H=248,L=62,R=112,T=42,B=52,s=svg(W,H),pw=W-L-R,ph=H-T-B;
 const X=i=>L+pw*i/(D.length-1), Y=v=>T+ph*(1-(v-20)/(50));
 [20,35,50,65].forEach(function(v){
   el(s,"line",{x1:L,x2:L+pw,y1:Y(v),y2:Y(v),stroke:C.line,"stroke-width":1});
   tx(s,L-8,Y(v)+3.5,v+"%",{ta:"end",fill:C.ink3,fs:9.5});});
 el(s,"line",{x1:L,x2:L+pw,y1:Y(50),y2:Y(50),stroke:C.line2,"stroke-width":1.4,"stroke-dasharray":"4 3"});
 let d="";D.forEach(function(p,i){d+=(i?"L":"M")+X(i)+" "+Y(p.v);});
 el(s,"path",{d:d,fill:"none",stroke:C.s1,"stroke-width":2.6});
 D.forEach(function(p,i){
  el(s,"circle",{cx:X(i),cy:Y(p.v),r:i===2?7:5.5,fill:i===2?C.s1:C.surf,stroke:C.s1,"stroke-width":2.2});
  tx(s,X(i),Y(p.v)-14,p.v+"%",{ta:"middle",fill:i===2?C.s1:C.ink,fs:12,fw:700});
  tx(s,X(i),H-30,p.n,{ta:"middle",fill:C.ink2,fs:10,ff:SANS});
  tx(s,X(i),H-17,p.d,{ta:"middle",fill:C.ink3,fs:9,ff:SANS});});
 // 표본 방향 표시
 el(s,"path",{d:"M"+(X(0)+8)+" "+(Y(35)-22)+"L"+(X(1)-8)+" "+(Y(63)-22),
   stroke:C.s4,"stroke-width":1.2,"stroke-dasharray":"3 2",fill:"none"});
 tx(s,(X(0)+X(1))/2,Y(49)-26,"+28%p 시장이 매파로",{ta:"middle",fill:C.s4,fs:9.5,ff:SANS});
 tx(s,X(2)+12,Y(56)+4,"−13%p",{fill:C.s2,fs:11,fw:700});
 tx(s,X(2)+12,Y(56)+18,"월러·윌리엄스",{fill:C.ink3,fs:9,ff:SANS});
 tx(s,0,20,"9월 FOMC 인상 확률 (FedWatch)",{fill:C.ink3,fs:10,ff:SANS});
 mount("c-hikepath",s);})();

/* ══ 00·3 자기채점 ══ */
(function(){
 const D=[{t:"“이 표본엔 인상 시나리오 대응이 없다”",r:"패",c:C.s4,w:"시장이 인상확률 63%까지 갔다. 경고가 아니라 대비를 했어야 했다."},
          {t:"“9,300 고점론은 같은 표본의 채권 논리로 반박된다”",r:"승",c:C.s2,w:"9/4~9/5 어느 방송도 9,300을 재주장하지 않았다."},
          {t:"“브로드컴 시소론은 인과가 틀렸다”",r:"승",c:C.s2,w:"가이던스 −0.66% 미스가 원인. 이후 방송도 시소 언급 없음."},
          {t:"“PER 68~159배 종목은 코어가 될 수 없다”",r:"승",c:C.s2,w:"삼성전기·두산에너빌리티. 전력 테마는 맞았으나 밸류는 여전히 극단."},
          {t:"“유가가 정책을 통해 지수를 움직인다”",r:"패",c:C.s4,w:"월러가 그 경로를 명시적으로 끊었다. 모형 척추 수정."},
          {t:"“연말 7,338 ±”",r:"미결",c:C.ink3,w:"12월까지 판정 불가."}];
 const W=880,L=0,MID=470,RX=545,T=40,RH=54,H=T+D.length*RH+40,s=svg(W,H);
 tx(s,0,20,"문서1~3의 명시적 주장",{fill:C.ink3,fs:10,ff:SANS});
 tx(s,MID+18,20,"판정",{fill:C.ink3,fs:10,ff:SANS});
 tx(s,RX,20,"근거",{fill:C.ink3,fs:10,ff:SANS});
 D.forEach(function(d,i){
  const y=T+i*RH;
  el(s,"line",{x1:0,x2:W,y1:y-14,y2:y-14,stroke:C.line,"stroke-width":1});
  el(s,"rect",{x:0,y:y-14,width:3,height:RH,fill:d.c,opacity:.75});
  tx(s,12,y+5,d.t,{fill:C.ink,fs:11.5,ff:SANS});
  el(s,"rect",{x:MID+18,y:y-7,width:34,height:19,fill:"none",stroke:d.c,"stroke-width":1.3,rx:2});
  tx(s,MID+35,y+6,d.r,{ta:"middle",fill:d.c,fs:11,ff:SANS,fw:700});
  const ws=d.w, half=Math.ceil(ws.length/2);
  let cut=ws.lastIndexOf(" ",half); if(cut<10)cut=half;
  tx(s,RX,y+1,ws.slice(0,cut),{fill:C.ink3,fs:10,ff:SANS});
  tx(s,RX,y+15,ws.slice(cut+1),{fill:C.ink3,fs:10,ff:SANS});});
 const yb=T+D.length*RH+6;
 el(s,"line",{x1:0,x2:W,y1:yb-14,y2:yb-14,stroke:C.line2,"stroke-width":1});
 tx(s,12,yb+6,"승 3",{fill:C.s2,fs:11.5,ff:SANS,fw:700});
 tx(s,72,yb+6,"패 2",{fill:C.s4,fs:11.5,ff:SANS,fw:700});
 tx(s,132,yb+6,"미결 1",{fill:C.ink3,fs:11.5,ff:SANS,fw:700});
 tx(s,RX,yb+6,"두 패는 모두 '유가·금리' 축에서 나왔다 — 그 축을 다시 짠 이유다",{fill:C.s4,fs:10,ff:SANS});
 mount("c-selfscore",s);})();

/* ══ 00·4 유가 고착 ══ */
(function(){
 const W=520,H=250,s=svg(W,H);
 // 유가는 그대로, 두 경로가 갈라진다
 const x0=70, y0=64;
 el(s,"circle",{cx:x0,cy:y0,r:26,fill:"none",stroke:C.s1,"stroke-width":2});
 tx(s,x0,y0-3,"96",{ta:"middle",fill:C.s1,fs:16,fw:700});
 tx(s,x0,y0+12,"브렌트",{ta:"middle",fill:C.ink3,fs:9,ff:SANS});
 tx(s,x0,y0+38,"이란→쿠웨이트",{ta:"middle",fill:C.ink3,fs:9,ff:SANS});
 // 경로 A: 원가 (살아있음)
 el(s,"path",{d:"M"+(x0+28)+" "+(y0-8)+" C 180 "+(y0-8)+", 200 46, 300 46",stroke:C.s2,"stroke-width":2.4,fill:"none"});
 el(s,"path",{d:"M296 41 L306 46 L296 51 Z",fill:C.s2});
 el(s,"rect",{x:310,y:28,width:196,height:38,fill:C.surf2,stroke:C.s2,"stroke-width":1.2});
 tx(s,318,45,"기업 원가 · 항공유 · 연료비",{fill:C.s2,fs:10.5,ff:SANS,fw:500});
 tx(s,318,59,"살아 있음 — 직접 효과",{fill:C.ink3,fs:9.5,ff:SANS});
 // 경로 B: 정책 (끊김)
 el(s,"path",{d:"M"+(x0+28)+" "+(y0+8)+" C 170 "+(y0+8)+", 172 140, 214 140",stroke:C.s4,"stroke-width":2.4,fill:"none"});
 el(s,"path",{d:"M244 140 C 268 140, 276 140, 300 140",stroke:C.s4,"stroke-width":2.4,fill:"none","stroke-dasharray":"4 4",opacity:.4});
 // 절단 표시
 el(s,"line",{x1:221,y1:126,x2:237,y2:154,stroke:C.s4,"stroke-width":2.4});
 el(s,"line",{x1:237,y1:126,x2:221,y2:154,stroke:C.s4,"stroke-width":2.4});
 tx(s,229,168,"절단",{ta:"middle",fill:C.s4,fs:10,ff:SANS,fw:700});
 el(s,"rect",{x:310,y:122,width:196,height:38,fill:C.surf2,stroke:C.line2,"stroke-width":1.2,opacity:.55});
 tx(s,318,139,"PCE → 연준 → 금리",{fill:C.ink3,fs:10.5,ff:SANS,fw:500});
 tx(s,318,153,"차단 — 정책단에서 제외",{fill:C.s4,fs:9.5,ff:SANS});
 // 수치
 el(s,"line",{x1:0,x2:W,y1:196,y2:196,stroke:C.line,"stroke-width":1});
 const N=[["헤드라인 PCE","3.70%",C.s4],["인하 문턱 π","2.65%",C.s2],["유가 −21% 전이","−0.74%p",C.s1],["전이 후 잔여 갭","−0.31%p",C.s4]];
 N.forEach(function(n,i){const x=i*(W/4);
  tx(s,x+4,214,n[0],{fill:C.ink3,fs:9.5,ff:SANS});
  tx(s,x+4,232,n[1],{fill:n[2],fs:14,fw:700});});
 tx(s,0,246,"전이계수: PCE 에너지비중 4.0% × 유가→소매 0.7 × 간접 1.25  (내 계수)",{fill:C.ink3,fs:9,ff:SANS});
 mount("c-oilstuck",s);})();

/* ══ 01·1 소스맵 ══ */
(function(){
 const AX=["거시·금리","반도체","수급","종목·밸류"];
 const SRC=[
  {n:"증시각도기",v:[3,1,4,2],d:"9/2"},{n:"종목 라이브",v:[1,2,3,5],d:"9/2"},
  {n:"문남중 대신 ①②",v:[6,1,1,1],d:"9/3"},{n:"윤OO 메리츠",v:[4,2,2,2],d:"9/3"},
  {n:"강관우 더프리미어",v:[2,1,3,4],d:"9/3"},{n:"노근창 세미콘",v:[1,6,0,3],d:"9/3"},
  {n:"김민수 레모니스",v:[2,2,3,3],d:"9/3"},{n:"이영수 HSL",v:[1,7,1,2],d:"9/4"},
  {n:"한상희의 시선",v:[6,1,2,1],d:"9/4"},{n:"반도체 심층",v:[0,9,0,2],d:"9/5"},
  {n:"박명숙 월가",v:[3,3,2,3],d:"9/5"}];
 const COL=[C.s1,C.s5,C.s3,C.s2];
 const W=880,L=132,R=90,T=52,RH=27,H=T+SRC.length*RH+54,s=svg(W,H);
 const pw=W-L-R, mx=12;
 AX.forEach(function(a,i){
  el(s,"rect",{x:L+i*84,y:14,width:9,height:9,fill:COL[i]});
  tx(s,L+i*84+13,22,a,{fill:C.ink2,fs:10,ff:SANS});});
 [0,4,8,12].forEach(function(v){
  el(s,"line",{x1:L+pw*v/mx,x2:L+pw*v/mx,y1:T-12,y2:T+SRC.length*RH-12,stroke:C.line,"stroke-width":1});
  tx(s,L+pw*v/mx,T-18,v,{ta:"middle",fill:C.ink3,fs:9});});
 SRC.forEach(function(d,i){
  const y=T+i*RH; let acc=0;
  tx(s,L-10,y+4,d.n,{ta:"end",fill:C.ink,fs:10.5,ff:SANS});
  tx(s,L-10,y+15,d.d,{ta:"end",fill:C.ink3,fs:8.5,ff:SANS});
  d.v.forEach(function(v,j){
   if(v>0){el(s,"rect",{x:L+pw*acc/mx,y:y-6,width:pw*v/mx,height:13,fill:COL[j],opacity:.82});}
   acc+=v;});
  tx(s,L+pw*acc/mx+8,y+4,acc,{fill:C.ink2,fs:10,fw:500});});
 const TOT=[0,0,0,0]; SRC.forEach(d=>d.v.forEach((v,j)=>TOT[j]+=v));
 el(s,"line",{x1:0,x2:W,y1:T+SRC.length*RH,y2:T+SRC.length*RH,stroke:C.line2,"stroke-width":1});
 tx(s,L-10,T+SRC.length*RH+18,"축 합계",{ta:"end",fill:C.ink3,fs:10,ff:SANS});
 TOT.forEach(function(v,j){tx(s,L+j*84,T+SRC.length*RH+18,AX[j]+" "+v,{fill:COL[j],fs:10.5,fw:700,ff:SANS});});
 tx(s,0,H-8,"단위: 검증 가능한 숫자 제시 횟수 · 수급 축 "+TOT[2]+"건이 가장 얇다 → 9/4 급락을 설명하지 못한 이유",{fill:C.ink3,fs:9.5,ff:SANS});
 mount("c-srcmap",s);})();

/* ══ 01·2 현금비중 ══ */
(function(){
 const D=[{n:"한상희",c:30,d:"주식 70 : 현금 30"},{n:"윤OO 메리츠",c:40,d:"60 : 40"},
          {n:"종목 라이브",c:45,d:"현금 40~50%"},{n:"김민수 레모니스",c:10,d:"현금 10%+"}];
 const W=520,L=112,R=132,T=40,RH=40,H=T+D.length*RH+42,s=svg(W,H);
 const pw=W-L-R;
 [0,25,50,75].forEach(function(v){
  el(s,"line",{x1:L+pw*v/75,x2:L+pw*v/75,y1:T-12,y2:T+D.length*RH-14,stroke:C.line,"stroke-width":1});
  tx(s,L+pw*v/75,T-18,v+"%",{ta:"middle",fill:C.ink3,fs:9});});
 const srt=D.slice().sort((a,b)=>a.c-b.c);
 srt.forEach(function(d,i){
  const y=T+i*RH, x=L+pw*d.c/75;
  tx(s,L-10,y+4,d.n,{ta:"end",fill:C.ink,fs:11,ff:SANS});
  el(s,"line",{x1:L,x2:x,y1:y,y2:y,stroke:C.s2,"stroke-width":2,opacity:.35});
  el(s,"circle",{cx:x,cy:y,r:6,fill:C.s2});
  tx(s,x+11,y+4,d.c+"%",{fill:C.s2,fs:11.5,fw:700});
  tx(s,x+11,y+17,d.d,{fill:C.ink3,fs:9,ff:SANS});});
 const mn=Math.min.apply(null,D.map(d=>d.c)), mx2=Math.max.apply(null,D.map(d=>d.c));
 el(s,"line",{x1:L+pw*mn/75,x2:L+pw*mx2/75,y1:T+D.length*RH+2,y2:T+D.length*RH+2,stroke:C.s4,"stroke-width":1.4});
 tx(s,L+pw*(mn+mx2)/2/75,T+D.length*RH+18,"스프레드 "+(mx2-mn)+"%p — 같은 데이터, 정반대 실행",{ta:"middle",fill:C.s4,fs:9.5,ff:SANS});
 mount("c-cash",s);})();

/* ══ 02·1 전이 사슬 v2 ══ */
(function(){
 const W=880,H=340,s=svg(W,H);
 const LAY=[
  {n:"① 촉발",items:[["브렌트 96$",C.s1],["이란·쿠웨이트",C.s1],["관세",C.s1]],y:52},
  {n:"② 전이",items:[["PCE 3.7%",C.s4],["코어 3.3%",C.s4],["절사평균 2.2%",C.s2]],y:132},
  {n:"③ 가격",items:[["EPS 1,300",C.s5],["fwd PER 5.7x",C.s5],["10Y 4.80%",C.s5]],y:212},
  {n:"④ 진폭",items:[["160조 매물벽",C.s3],["기타법인 흡수",C.s3],["신용 33조",C.s3]],y:292}];
 const BX=176,BW=210,GAP=14;
 LAY.forEach(function(l,li){
  tx(s,0,l.y+5,l.n,{fill:C.ink,fs:12,ff:SANS,fw:700});
  tx(s,0,l.y+21,["유가·지정학","물가·정책","밸류에이션","수급"][li],{fill:C.ink3,fs:9,ff:SANS});
  l.items.forEach(function(it,i){
   const x=BX+i*(BW+GAP);
   el(s,"rect",{x:x,y:l.y-16,width:BW,height:34,fill:C.surf2,stroke:it[1],"stroke-width":1.2,opacity:.95});
   tx(s,x+12,l.y+5,it[0],{fill:it[1],fs:11.5,ff:SANS,fw:500});});});
 // 층간 화살표
 function arrow(y1,y2,x,col,dash,op){
  el(s,"line",{x1:x,x2:x,y1:y1,y2:y2-8,stroke:col,"stroke-width":2,"stroke-dasharray":dash||"",opacity:op||1});
  el(s,"path",{d:"M"+(x-5)+" "+(y2-9)+"L"+x+" "+(y2-2)+"L"+(x+5)+" "+(y2-9)+"Z",fill:col,opacity:op||1});}
 // 1->2 절단
 [0,1,2].forEach(function(i){const x=BX+i*(BW+GAP)+BW/2;
   arrow(52+18,132-16,x,C.s4,"5 4",.32);});
 const cx=BX+BW/2+ (BW+GAP);
 el(s,"rect",{x:cx-96,y:82,width:192,height:26,fill:C.surf,stroke:C.s4,"stroke-width":1.4});
 tx(s,cx,99,"✕  정책단 절단 (월러·윌리엄스)",{ta:"middle",fill:C.s4,fs:10.5,ff:SANS,fw:700});
 // 2->3, 3->4 정상
 [0,1,2].forEach(function(i){const x=BX+i*(BW+GAP)+BW/2;
   arrow(132+18,212-16,x,C.s5,"",.75);
   arrow(212+18,292-16,x,C.s3,"",.75);});
 // 우측 감쇄율
 tx(s,W-2,99,"감쇄 100% → 0",{ta:"end",fill:C.s4,fs:10,ff:SANS,fw:700});
 tx(s,W-2,180,"전달률 유지",{ta:"end",fill:C.s5,fs:10,ff:SANS});
 tx(s,W-2,258,"전달률 유지",{ta:"end",fill:C.s3,fs:10,ff:SANS});
 tx(s,0,H-8,"굵은 실선 = 살아 있는 배선 · 점선+✕ = 이번 주에 끊긴 배선.  ①은 여전히 기업 원가(③)로는 직접 연결된다.",{fill:C.ink3,fs:9.5,ff:SANS});
 // ①->③ 우회 경로
 el(s,"path",{d:"M"+(BX-10)+" 52 C 110 52, 110 212, "+(BX-10)+" 212",stroke:C.s2,"stroke-width":1.6,fill:"none","stroke-dasharray":"3 3"});
 el(s,"path",{d:"M"+(BX-15)+" 207 L"+(BX-6)+" 212 L"+(BX-15)+" 217 Z",fill:C.s2});
 tx(s,104,136,"원가",{ta:"middle",fill:C.s2,fs:9.5,ff:SANS,rot:-90});
 mount("c-chain",s);})();

/* ══ 02·2 월러 조건문 ══ */
(function(){
 const W=520,H=246,L=60,R=76,T=64,B=56,s=svg(W,H),pw=W-L-R,ph=H-T-B;
 const mn=2.4,mx=3.6;
 const X=v=>L+pw*(v-mn)/(mx-mn);
 [2.4,2.8,3.2,3.6].forEach(function(v){
  el(s,"line",{x1:X(v),x2:X(v),y1:T-10,y2:T+ph,stroke:C.line,"stroke-width":1});
  tx(s,X(v),T+ph+16,v.toFixed(1)+"%",{ta:"middle",fill:C.ink3,fs:9.5});});
 // 문턱
 el(s,"rect",{x:L,y:T-10,width:X(2.8)-L,height:ph+10,fill:C.s2,opacity:.09});
 el(s,"line",{x1:X(2.8),x2:X(2.8),y1:T-10,y2:T+ph,stroke:C.s2,"stroke-width":2});
 tx(s,X(2.8),T-18,"월러 문턱 2.8%",{ta:"middle",fill:C.s2,fs:10.5,ff:SANS,fw:700});
 tx(s,L+6,T+ph-6,"← 동결 지지 구간",{fill:C.s2,fs:9.5,ff:SANS});
 // 현재 코어
 const cur=3.3;
 el(s,"circle",{cx:X(cur),cy:T+28,r:7,fill:C.s4});
 tx(s,X(cur),T+12,"현재 코어 3.3%",{ta:"middle",fill:C.s4,fs:10.5,ff:SANS,fw:700});
 el(s,"line",{x1:X(2.8),x2:X(cur),y1:T+52,y2:T+52,stroke:C.s1,"stroke-width":1.6,"stroke-dasharray":"3 3"});
 tx(s,(X(2.8)+X(cur))/2,T+68,"−0.50%p 필요",{ta:"middle",fill:C.s1,fs:10.5,fw:700});
 // 인하 문턱(문서1)
 el(s,"line",{x1:X(2.65),x2:X(2.65),y1:T+82,y2:T+ph,stroke:C.s3,"stroke-width":1.4,"stroke-dasharray":"4 3"});
 tx(s,X(2.65)-6,T+96,"실질금리 인하선 2.65",{ta:"end",fill:C.s3,fs:9.5,ff:SANS});
 tx(s,0,20,"월러: “코어가 2.8%로 나오면 9월 동결을 지지” + “에너지·관세는 지속적 물가압력 아님”",{fill:C.ink,fs:10.5,ff:SANS});
 tx(s,0,36,"윌리엄스도 전일 같은 취지. 두 사람은 서열 2·3위다.",{fill:C.ink3,fs:9.5,ff:SANS});
 tx(s,0,H-8,"동결 문턱(2.8)이 인하 문턱(2.65)보다 위에 있다 → 동결이 먼저, 인하는 그 다음",{fill:C.ink3,fs:9.5,ff:SANS});
 mount("c-waller",s);})();

/* ══ 02·3 PCE 4지표 ══ */
(function(){
 const D=[{n:"헤드라인 PCE",v:3.70},{n:"코어 PCE",v:3.30},{n:"중위 CPI",v:2.70},{n:"절사평균 PCE",v:2.20}];
 const TH=2.65;
 const W=520,L=118,R=104,T=62,RH=42,H=T+D.length*RH+40,s=svg(W,H);
 const pw=W-L-R, mn=1.8,mx=4.0;
 const X=v=>L+pw*(v-mn)/(mx-mn);
 [2.0,2.5,3.0,3.5,4.0].forEach(function(v){
  el(s,"line",{x1:X(v),x2:X(v),y1:T-14,y2:T+D.length*RH-16,stroke:C.line,"stroke-width":1});
  tx(s,X(v),T-20,v.toFixed(1),{ta:"middle",fill:C.ink3,fs:9});});
 el(s,"rect",{x:L,y:T-14,width:X(TH)-L,height:D.length*RH-2,fill:C.s2,opacity:.08});
 el(s,"line",{x1:X(TH),x2:X(TH),y1:T-14,y2:T+D.length*RH-16,stroke:C.s2,"stroke-width":2});
 D.forEach(function(d,i){
  const y=T+i*RH, ok=d.v<TH, col=ok?C.s2:C.s4, gap=d.v-TH;
  tx(s,L-10,y+4,d.n,{ta:"end",fill:ok?C.ink:C.ink2,fs:11,ff:SANS,fw:ok?700:400});
  el(s,"line",{x1:X(TH),x2:X(d.v),y1:y,y2:y,stroke:col,"stroke-width":2.2,opacity:.5});
  el(s,"circle",{cx:X(d.v),cy:y,r:6.5,fill:col});
  tx(s,X(d.v)+(ok?-13:13),y+4,d.v.toFixed(2),{ta:ok?"end":"start",fill:col,fs:11.5,fw:700});
  tx(s,W-2,y+4,(gap>0?"+":"")+gap.toFixed(2)+"%p",{ta:"end",fill:col,fs:10.5});});
 tx(s,X(TH),T+D.length*RH+16,"인하 명분선 2.65%",{ta:"middle",fill:C.s2,fs:10,ff:SANS,fw:700});
 tx(s,0,H-8,"실질중립 3.10 − 2.00 = 1.10% → 정책금리 3.75 기준 π < 2.65%가 인하 명분선",{fill:C.ink3,fs:9.5,ff:SANS});
 tx(s,0,20,"프레임 의존성 5회차 검출 — 절사평균은 이미 조건 충족, 헤드라인은 −1.05%p 미달",{fill:C.s1,fs:10,ff:SANS});
 mount("c-pce",s);})();

/* ══ 02·4 FOMC 표 산술 ══ */
(function(){
 const W=520,H=270,s=svg(W,H);
 const R=12,CX=170,CY=118,RAD=76;
 // 12개 표를 원형 배치: 이사 7 + 지역총재 5
 const SEATS=[];
 for(let i=0;i<12;i++){const a=-Math.PI/2+i*2*Math.PI/12;
   SEATS.push({x:CX+RAD*Math.cos(a),y:CY+RAD*Math.sin(a),gov:i<7});}
 el(s,"circle",{cx:CX,cy:CY,r:RAD,fill:"none",stroke:C.line,"stroke-width":1,"stroke-dasharray":"3 3"});
 SEATS.forEach(function(p,i){
  const dis = i>=7 && i<10;   // 7월 반대 3인 = 지역총재
  el(s,"circle",{cx:p.x,cy:p.y,r:11,fill:dis?C.s4:(p.gov?C.surf2:C.surf),
    stroke:dis?C.s4:(p.gov?C.s5:C.ink3),"stroke-width":1.8});
  tx(s,p.x,p.y+4,p.gov?"이":"총",{ta:"middle",fill:dis?C.surf:(p.gov?C.s5:C.ink3),fs:9.5,ff:SANS,fw:700});});
 tx(s,CX,CY-6,"12표",{ta:"middle",fill:C.ink,fs:19,fw:700});
 tx(s,CX,CY+10,"과반 7표",{ta:"middle",fill:C.ink3,fs:9.5,ff:SANS});
 // 범례 + 산술
 const LX=286;
 const LG=[["이사 (의장 포함)",7,C.s5],["지역 연준 총재",5,C.ink3],["7월 반대표 (전원 총재)",3,C.s4]];
 LG.forEach(function(g,i){
  el(s,"circle",{cx:LX+7,cy:44+i*24,r:6,fill:i===2?C.s4:C.surf2,stroke:g[2],"stroke-width":1.6});
  tx(s,LX+20,44+i*24+4,g[0],{fill:C.ink2,fs:10,ff:SANS});
  tx(s,W-2,44+i*24+4,g[1]+"표",{ta:"end",fill:g[2],fs:11,fw:700});});
 el(s,"line",{x1:LX,x2:W,y1:126,y2:126,stroke:C.line2,"stroke-width":1});
 const STEP=[["매파 승리에 필요",7,C.ink],["지역총재 최대 동원",5,C.ink2],["→ 부족분 = 이사",2,C.s4]];
 STEP.forEach(function(g,i){
  tx(s,LX,148+i*24,g[0],{fill:i===2?C.s4:C.ink3,fs:10,ff:SANS,fw:i===2?700:400});
  tx(s,W-2,148+i*24,(i===2?"+":"")+g[1]+"명",{ta:"end",fill:g[2],fs:11.5,fw:700});});
 el(s,"rect",{x:LX,y:222,width:W-LX,height:34,fill:C.surf2,stroke:C.s4,"stroke-width":1.2});
 tx(s,LX+10,236,"의장이 임명한 이사 최소 2~3명이",{fill:C.s4,fs:10,ff:SANS});
 tx(s,LX+10,249,"의장에게 반대표를 던져야 성립",{fill:C.s4,fs:10,ff:SANS,fw:700});
 tx(s,0,H-6,"불가능이 아니라 낮은 확률 — 방송의 “매파 우세” 주장은 이 산술을 통과해야 한다",{fill:C.ink3,fs:9.5,ff:SANS});
 mount("c-vote",s);})();

/* ══ 02·5 상충 ══ */
(function(){
 const W=520,H=232,s=svg(W,H);
 const A={x:14,y:44,w:222,h:88,t:"잭슨홀 매파 전환",c:C.s4,
   l:["“인상 옵션 살아있다”","서열 1위 발화","FedWatch 35 → 63%"]};
 const B={x:284,y:44,w:222,h:88,t:"월러·윌리엄스 비둘기",c:C.s2,
   l:["“코어 2.8이면 동결”","서열 2·3위 발화","FedWatch 63 → 50%"]};
 [A,B].forEach(function(g){
  el(s,"rect",{x:g.x,y:g.y,width:g.w,height:g.h,fill:C.surf2,stroke:g.c,"stroke-width":1.4});
  tx(s,g.x+12,g.y+21,g.t,{fill:g.c,fs:11.5,ff:SANS,fw:700});
  g.l.forEach(function(t,i){tx(s,g.x+12,g.y+42+i*17,"· "+t,{fill:C.ink2,fs:10,ff:SANS});});});
 // 충돌
 el(s,"line",{x1:A.x+A.w,x2:B.x,y1:88,y2:88,stroke:C.s1,"stroke-width":1.6,"stroke-dasharray":"4 3"});
 el(s,"circle",{cx:260,cy:88,r:17,fill:C.surf,stroke:C.s1,"stroke-width":1.8});
 tx(s,260,93,"⚡",{ta:"middle",fs:14});
 tx(s,260,26,"같은 주 · 같은 연준 · 정반대 신호",{ta:"middle",fill:C.ink,fs:11,ff:SANS,fw:500});
 // 판정선
 el(s,"line",{x1:0,x2:W,y1:160,y2:160,stroke:C.line,"stroke-width":1});
 tx(s,0,180,"판정자",{fill:C.ink3,fs:10,ff:SANS});
 tx(s,68,180,"다음 코어 PCE 발표",{fill:C.ink,fs:11,ff:SANS,fw:700});
 tx(s,0,200,"2.8% 이하 → 월러 승 · 동결 · S1 확률 상승",{fill:C.s2,fs:10,ff:SANS});
 tx(s,0,217,"3.2% 이상 → 잭슨홀 승 · 인상 재점화 · S3 부활",{fill:C.s4,fs:10,ff:SANS});
 tx(s,W-2,180,"2.8 ~ 3.2 = 미결",{ta:"end",fill:C.ink3,fs:10,ff:SANS});
 mount("c-clash",s);})();

/* ══ 03·1 시나리오 v1 vs v2 ══ */
(function(){
 const D=[{k:"S1",n:"데탕트",p1:30,p2:34,l1:8255,l2:7960,c:C.s2},
          {k:"S2",n:"지연",p1:35,p2:36,l1:7250,l2:7250,c:C.s1},
          {k:"S3",n:"스태그",p1:20,p2:13,l1:6000,l2:6100,c:C.s4},
          {k:"S4",n:"공급함정",p1:15,p2:17,l1:7493,l2:7493,c:C.s3}];
 const W=880,L=118,MID=440,T=68,RH=60,H=T+D.length*RH+62,s=svg(W,H);
 const pwA=MID-L-40, pwB=W-MID-70;
 const XA=v=>L+pwA*v/40;
 const lo=5800,hi=8400, XB=v=>MID+30+pwB*(v-lo)/(hi-lo);
 tx(s,L,18,"확률 (%)",{fill:C.ink3,fs:10,ff:SANS});
 tx(s,MID+30,18,"지수 레벨",{fill:C.ink3,fs:10,ff:SANS});
 [0,10,20,30,40].forEach(function(v){
  el(s,"line",{x1:XA(v),x2:XA(v),y1:T-16,y2:T+D.length*RH-24,stroke:C.line,"stroke-width":1});
  tx(s,XA(v),T-22,v,{ta:"middle",fill:C.ink3,fs:9});});
 [6000,6579,7000,8000].forEach(function(v){
  el(s,"line",{x1:XB(v),x2:XB(v),y1:T-16,y2:T+D.length*RH-24,stroke:v===6579?C.line2:C.line,"stroke-width":v===6579?1.4:1});
  tx(s,XB(v),T-22,v===6579?"기준 6,579":fmt(v),{ta:"middle",fill:v===6579?C.ink2:C.ink3,fs:9});});
 D.forEach(function(d,i){
  const y=T+i*RH;
  tx(s,L-12,y+1,d.k+" "+d.n,{ta:"end",fill:d.c,fs:11.5,ff:SANS,fw:700});
  // 확률 덤벨
  el(s,"line",{x1:XA(d.p1),x2:XA(d.p2),y1:y,y2:y,stroke:d.c,"stroke-width":2.4,opacity:.55});
  el(s,"circle",{cx:XA(d.p1),cy:y,r:4.5,fill:C.surf,stroke:C.ink3,"stroke-width":1.6});
  el(s,"circle",{cx:XA(d.p2),cy:y,r:6,fill:d.c});
  tx(s,XA(d.p1),y-13,d.p1+"%",{ta:"middle",fill:C.ink3,fs:9.5});
  tx(s,XA(d.p2),y+22,d.p2+"%",{ta:"middle",fill:d.c,fs:11,fw:700});
  // 레벨 덤벨
  const same=d.l1===d.l2;
  el(s,"line",{x1:XB(d.l1),x2:XB(d.l2),y1:y,y2:y,stroke:same?C.line2:d.c,"stroke-width":2.4,opacity:.55});
  el(s,"circle",{cx:XB(d.l1),cy:y,r:4.5,fill:C.surf,stroke:C.ink3,"stroke-width":1.6});
  el(s,"circle",{cx:XB(d.l2),cy:y,r:6,fill:same?C.surf:d.c,stroke:same?C.ink3:d.c,"stroke-width":1.6});
  tx(s,XB(d.l2)+(d.l2<d.l1?-12:12),y+4,fmt(d.l2),{ta:d.l2<d.l1?"end":"start",fill:same?C.ink3:d.c,fs:10.5,fw:700});
  if(!same)tx(s,XB(d.l1),y-13,fmt(d.l1),{ta:"middle",fill:C.ink3,fs:9.5});});
 el(s,"line",{x1:MID,x2:MID,y1:T-30,y2:T+D.length*RH-20,stroke:C.line2,"stroke-width":1});
 el(s,"line",{x1:0,x2:W,y1:T+D.length*RH-12,y2:T+D.length*RH-12,stroke:C.line2,"stroke-width":1});
 tx(s,L-12,T+D.length*RH+10,"확률가중",{ta:"end",fill:C.ink,fs:11,ff:SANS,fw:700});
 tx(s,XB(7338),T+D.length*RH+8,"7,338",{ta:"middle",fill:C.ink3,fs:10.5});
 el(s,"line",{x1:XB(7338),x2:XB(7383),y1:T+D.length*RH+17,y2:T+D.length*RH+17,stroke:C.s2,"stroke-width":2});
 tx(s,XB(7383),T+D.length*RH+34,"7,383",{ta:"middle",fill:C.s2,fs:13,fw:700});
 tx(s,0,H-8,"작은 회색 점 = v1 · 큰 색 점 = v2.  꼬리(S3)를 7%p 줄여 S1 +4, S4 +2, S2 +1로 나눴다.",{fill:C.ink3,fs:9.5,ff:SANS});
 mount("c-scen",s);})();

/* ══ 03·2 매물벽 → PER 유도 ══ */
(function(){
 const W=520,H=280,s=svg(W,H);
 const STEP=[
  {t:"7,000pt 위 개인 매수분",v:"160조",c:C.s4,d:"삼성전자 + SK하이닉스"},
  {t:"× 출회율 40%  (내 가정)",v:"64조",c:C.s1,d:"본전 회복 시 전량이 아니라 일부"},
  {t:"÷ 일평균거래대금 66.7조 × 흡수 25%",v:"3.84일",c:C.s1,d:"16.7조/일이 매물을 받는다"},
  {t:"× 감쇄 0.06x/일  (내 계수)",v:"−0.23x",c:C.s4,d:"멀티플 확장 지연"}];
 const BW=W, RH=44;
 STEP.forEach(function(p,i){
  const y=26+i*RH;
  el(s,"rect",{x:0,y:y-14,width:3,height:34,fill:p.c});
  tx(s,12,y+1,p.t,{fill:C.ink2,fs:10.5,ff:SANS});
  tx(s,12,y+15,p.d,{fill:C.ink3,fs:9,ff:SANS});
  tx(s,W-2,y+4,p.v,{ta:"end",fill:p.c,fs:14,fw:700});
  if(i<STEP.length-1){el(s,"path",{d:"M"+(W/2-5)+" "+(y+22)+"L"+(W/2)+" "+(y+29)+"L"+(W/2+5)+" "+(y+22)+"Z",fill:C.line2});}});
 // 결론 바
 const yb=214;
 el(s,"line",{x1:0,x2:W,y1:yb-16,y2:yb-16,stroke:C.line2,"stroke-width":1});
 const L2=118,R2=66,pw=W-L2-R2;
 const X=v=>L2+pw*(v-5.6)/(7.4-5.6);
 [5.6,6.0,6.4,6.8,7.2].forEach(function(v){
  el(s,"line",{x1:X(v),x2:X(v),y1:yb,y2:yb+34,stroke:C.line,"stroke-width":1});
  tx(s,X(v),yb+48,v.toFixed(1)+"x",{ta:"middle",fill:C.ink3,fs:9});});
 tx(s,L2-10,yb+21,"S1 fwd PER",{ta:"end",fill:C.ink,fs:10.5,ff:SANS,fw:700});
 el(s,"line",{x1:X(6.12),x2:X(6.35),y1:yb+17,y2:yb+17,stroke:C.s4,"stroke-width":3});
 el(s,"circle",{cx:X(6.35),cy:yb+17,r:5,fill:C.surf,stroke:C.ink3,"stroke-width":1.8});
 el(s,"circle",{cx:X(6.12),cy:yb+17,r:6.5,fill:C.s4});
 tx(s,X(6.35),yb+7,"6.35x → 8,255",{ta:"middle",fill:C.ink3,fs:9.5});
 tx(s,X(6.12),yb+34,"6.12x → 7,960",{ta:"middle",fill:C.s4,fs:10.5,fw:700});
 tx(s,0,H-4,"EPS 1,300 고정 · 지수 = EPS × PER.  상단을 눈대중으로 깎지 않고 멀티플에서 유도했다.",{fill:C.ink3,fs:9.5,ff:SANS});
 mount("c-wall",s);})();

/* ══ 03·3 팬차트 ══ */
(function(){
 const W=880,H=352,L=58,R=142,T=42,B=48,s=svg(W,H),pw=W-L-R,ph=H-T-B;
 const base=6579.19;
 const SC=[{k:"S1",n:"데탕트",p:34,v:7960,c:C.s2},{k:"S4",n:"공급함정",p:17,v:7493,c:C.s3},
           {k:"S2",n:"지연",p:36,v:7250,c:C.s1},{k:"S3",n:"스태그",p:13,v:6100,c:C.s4}];
 const lo=5850,hi=8250;
 const Y=v=>T+ph*(1-(v-lo)/(hi-lo));
 const N=8; const X=i=>L+pw*i/N;
 [6000,6500,7000,7500,8000].forEach(function(v){
  el(s,"line",{x1:L,x2:L+pw,y1:Y(v),y2:Y(v),stroke:C.line,"stroke-width":1});
  tx(s,L-8,Y(v)+3.5,fmt(v),{ta:"end",fill:C.ink3,fs:9.5});});
 // 경로 (지수함수적 수렴, 예시)
 SC.forEach(function(sc){
  let d="M"+X(0)+" "+Y(base);
  for(let i=1;i<=N;i++){const t=i/N; const v=base+(sc.v-base)*Math.pow(t,0.85);
    d+="L"+X(i)+" "+Y(v);}
  el(s,"path",{d:d,fill:"none",stroke:sc.c,"stroke-width":1+sc.p/14,opacity:.85});
  el(s,"circle",{cx:X(N),cy:Y(sc.v),r:3+sc.p/9,fill:sc.c});
  tx(s,X(N)+11,Y(sc.v)-3,fmt(sc.v),{fill:sc.c,fs:12,fw:700});
  tx(s,X(N)+11,Y(sc.v)+11,sc.k+" "+sc.n+" "+sc.p+"%",{fill:C.ink3,fs:9,ff:SANS});});
 // 기대값
 const ev=7383;
 el(s,"line",{x1:L,x2:X(N),y1:Y(ev),y2:Y(ev),stroke:C.ink,"stroke-width":1.6,"stroke-dasharray":"5 4"});
 tx(s,L+8,Y(ev)-8,"확률가중 7,383  (+12.2%)",{fill:C.ink,fs:11,ff:SANS,fw:700});
 el(s,"line",{x1:L,x2:X(N),y1:Y(base),y2:Y(base),stroke:C.line2,"stroke-width":1.2});
 tx(s,L+8,Y(base)+14,"기준 6,579 (9/3)",{fill:C.ink3,fs:9.5,ff:SANS});
 ["9월","10월","11월","12월"].forEach(function(m,i){
  tx(s,X(i*2+2),H-24,m,{ta:"middle",fill:C.ink3,fs:10,ff:SANS});});
 tx(s,0,20,"선 굵기 = 확률 · 경로 곡률은 예시이며 시점 예측이 아니다",{fill:C.ink3,fs:9.5,ff:SANS});
 tx(s,0,H-8,"최대상방 +1,381 (7,960) : 최대하방 −479 (6,100) = 2.88 : 1  ·  v1은 2.89 : 1 — 비대칭은 거의 그대로다",{fill:C.ink3,fs:9.5,ff:SANS});
 mount("c-fan",s);})();

/* ══ 03·4 회복 캘린더 ══ */
(function(){
 const W=520,H=210,L=52,R=52,T=68,s=svg(W,H),pw=W-L-R;
 const D0=new Date(2026,6,23), D1=new Date(2026,8,3),
       D12=new Date(2026,10,26), D18=new Date(2027,0,7);
 const t0=D0.getTime(), tN=D18.getTime()+8*864e5;
 const X=d=>L+pw*(d.getTime()-t0)/(tN-t0);
 el(s,"line",{x1:L,x2:L+pw,y1:T,y2:T,stroke:C.line2,"stroke-width":1.4});
 // 하락 구간
 el(s,"rect",{x:X(D0),y:T-13,width:X(D1)-X(D0),height:26,fill:C.s4,opacity:.2});
 tx(s,(X(D0)+X(D1))/2,T+4,"6주 하락",{ta:"middle",fill:C.s4,fs:10.5,ff:SANS,fw:700});
 // 회복 구간
 el(s,"rect",{x:X(D1),y:T-13,width:X(D12)-X(D1),height:26,fill:C.s2,opacity:.2});
 el(s,"rect",{x:X(D12),y:T-13,width:X(D18)-X(D12),height:26,fill:C.s2,opacity:.1});
 tx(s,(X(D1)+X(D12))/2,T+4,"12주",{ta:"middle",fill:C.s2,fs:10.5,ff:SANS,fw:700});
 tx(s,(X(D12)+X(D18))/2,T+4,"~18주",{ta:"middle",fill:C.s2,fs:10,ff:SANS});
 [[D0,"7/23","고점 (역산)",C.ink3,-1],[D1,"9/3","기준일 6,579",C.ink,-1],
  [D12,"11/26","12주 도달",C.s2,1],[D18,"1/7","18주 도달",C.s2,1]].forEach(function(m){
  const x=X(m[0]);
  el(s,"line",{x1:x,x2:x,y1:T-13,y2:T+(m[4]>0?40:-30),stroke:m[3],"stroke-width":1.2,"stroke-dasharray":"3 2"});
  el(s,"circle",{cx:x,cy:T,r:4,fill:m[3]});
  const yy=m[4]>0?T+54:T-38;
  tx(s,x,yy,m[1],{ta:"middle",fill:m[3],fs:11,fw:700});
  tx(s,x,yy+13,m[2],{ta:"middle",fill:C.ink3,fs:9,ff:SANS});});
 tx(s,0,20,"“6주 내렸으면 12~18주 오른다” — 방송의 경험칙을 날짜로 환산",{fill:C.ink,fs:10.5,ff:SANS});
 tx(s,0,H-24,"주의: 이 규칙에는 표본 수·조건부 확률이 제시되지 않았다. 검증 불가한 경험칙으로 분류한다.",{fill:C.s1,fs:9.5,ff:SANS});
 tx(s,0,H-8,"다만 도달점 11/26은 12월 FOMC 직전이고, 1/7은 4분기 실적 시즌 초입이다 — 우연이 아닐 수 있다.",{fill:C.ink3,fs:9.5,ff:SANS});
 mount("c-recover",s);})();

/* ══ 04·1 랙 전력 사다리 ══ */
(function(){
 const D=[{n:"클라우드 서버",y:"2016~18",v:10},{n:"Hopper",y:"2022~23",v:40},
          {n:"Blackwell",y:"2024~25",v:120},{n:"Blackwell Ultra",y:"2025",v:150},
          {n:"Rubin Ultra NVL576",y:"차기",v:600}];
 const W=520,L=132,R=76,T=44,RH=40,H=T+D.length*RH+38,s=svg(W,H);
 const pw=W-L-R;
 [0,150,300,450,600].forEach(function(v){
  el(s,"line",{x1:L+pw*v/600,x2:L+pw*v/600,y1:T-14,y2:T+D.length*RH-16,stroke:C.line,"stroke-width":1});
  tx(s,L+pw*v/600,T-20,v,{ta:"middle",fill:C.ink3,fs:9});});
 D.forEach(function(d,i){
  const y=T+i*RH, w=pw*d.v/600, last=i===D.length-1;
  tx(s,L-10,y+1,d.n,{ta:"end",fill:last?C.s5:C.ink,fs:10.5,ff:SANS,fw:last?700:400});
  tx(s,L-10,y+14,d.y,{ta:"end",fill:C.ink3,fs:8.5,ff:SANS});
  el(s,"rect",{x:L,y:y-9,width:Math.max(w,2),height:19,fill:last?C.s5:C.s5,opacity:last?1:.42});
  tx(s,L+w+9,y+5,d.v+"kW",{fill:last?C.s5:C.ink2,fs:11,fw:last?700:500});});
 tx(s,L,T+D.length*RH+6,"10kW → 600kW",{fill:C.ink3,fs:10,ff:SANS});
 tx(s,L+120,T+D.length*RH+6,"60배",{fill:C.s5,fs:15,fw:700});
 tx(s,0,H-6,"전력이 늘면 기판 층수·MLCC 탑재량·전력반도체가 같이 늘어난다 — 이번 사이클의 물량 근거",{fill:C.ink3,fs:9.5,ff:SANS});
 mount("c-power",s);})();

/* ══ 04·2 메모리 비중 ══ */
(function(){
 const W=520,H=232,s=svg(W,H);
 const CX1=132,CX2=384,CY=104,RAD=58;
 function donut(cx,lab,pct,col,sub){
  const r=RAD, c=2*Math.PI*r;
  el(s,"circle",{cx:cx,cy:CY,r:r,fill:"none",stroke:C.line2,"stroke-width":17});
  el(s,"circle",{cx:cx,cy:CY,r:r,fill:"none",stroke:col,"stroke-width":17,
    "stroke-dasharray":(c*pct/100)+" "+c,transform:"rotate(-90 "+cx+" "+CY+")","stroke-linecap":"butt"});
  tx(s,cx,CY+2,pct+"%",{ta:"middle",fill:col,fs:21,fw:700});
  tx(s,cx,CY+19,"메모리",{ta:"middle",fill:C.ink3,fs:9,ff:SANS});
  tx(s,cx,CY-r-16,lab,{ta:"middle",fill:C.ink,fs:11,ff:SANS,fw:500});
  tx(s,cx,CY+r+24,sub,{ta:"middle",fill:C.ink3,fs:9,ff:SANS});}
 donut(CX1,"이전 사이클",13,C.ink3,"학습(train) 중심");
 donut(CX2,"현재",30,C.s5,"디코드·KV캐시 중심");
 el(s,"path",{d:"M212 104 L292 104",stroke:C.s5,"stroke-width":2});
 el(s,"path",{d:"M288 99 L298 104 L288 109 Z",fill:C.s5});
 tx(s,252,92,"+17%p",{ta:"middle",fill:C.s5,fs:11,fw:700});
 el(s,"line",{x1:0,x2:W,y1:190,y2:190,stroke:C.line,"stroke-width":1});
 tx(s,0,208,"전이 경로",{fill:C.ink3,fs:10,ff:SANS});
 tx(s,74,208,"추론 확산 → 디코드 단계 → KV캐시 폭증 → HBM만으론 부족 → 범용 DRAM 흡수",{fill:C.ink2,fs:10,ff:SANS});
 tx(s,0,224,"작년 9월부터의 범용 DRAM 가격 상승을 이 경로가 설명한다  ·  좌측 13%는 “10%대 초반”의 수치화(눈대중)",{fill:C.ink3,fs:9.5,ff:SANS});
 mount("c-memshare",s);})();

/* ══ 04·3 CXMT 명목 vs 유효 ══ */
(function(){
 const W=520,H=266,L=120,R=88,T=66,RH=42,s=svg(W,H);
 const pw=W-L-R, mx=40;
 const D=[{n:"현재 명목 capa",v:30,e:12},{n:"연말 명목 capa",v:36,e:14.4},
          {n:"마이크론 (기준)",v:36,e:36,ref:1}];
 [0,10,20,30,40].forEach(function(v){
  el(s,"line",{x1:L+pw*v/mx,x2:L+pw*v/mx,y1:T-16,y2:T+D.length*RH-18,stroke:C.line,"stroke-width":1});
  tx(s,L+pw*v/mx,T-22,v,{ta:"middle",fill:C.ink3,fs:9});});
 D.forEach(function(d,i){
  const y=T+i*RH;
  tx(s,L-10,y+4,d.n,{ta:"end",fill:d.ref?C.ink3:C.ink,fs:10.5,ff:SANS});
  el(s,"rect",{x:L,y:y-10,width:pw*d.v/mx,height:20,fill:d.ref?C.ink3:C.s4,opacity:.28});
  el(s,"rect",{x:L,y:y-10,width:pw*d.e/mx,height:20,fill:d.ref?C.ink3:C.s4,opacity:.9});
  tx(s,L+pw*d.v/mx+8,y+4,d.v+"만장",{fill:C.ink3,fs:10});
  if(!d.ref)tx(s,L+pw*d.e/mx-8,y+4,d.e.toFixed(1),{ta:"end",fill:"#0B101C",fs:10.5,fw:700});});
 el(s,"rect",{x:0,y:12,width:11,height:11,fill:C.s4,opacity:.9});
 tx(s,16,21,"유효 (굿다이 40%)",{fill:C.ink2,fs:10,ff:SANS});
 el(s,"rect",{x:150,y:12,width:11,height:11,fill:C.s4,opacity:.28});
 tx(s,166,21,"명목",{fill:C.ink3,fs:10,ff:SANS});
 el(s,"line",{x1:0,x2:W,y1:T+D.length*RH+2,y2:T+D.length*RH+2,stroke:C.line,"stroke-width":1});
 tx(s,0,T+D.length*RH+22,"연말 명목으로는 마이크론과 동급 — 유효로는 40% 수준. 60%가 버려진다.",{fill:C.ink,fs:10.5,ff:SANS});
 tx(s,0,T+D.length*RH+38,"단, 수율은 60→80이 90→95보다 쉽고 AI가 그 개선을 가속한다 — 격차는 좁혀지는 쪽이다.",{fill:C.s1,fs:9.5,ff:SANS});
 tx(s,0,H-6,"HBM3 상반기 양산, HBM3E 내년 목표 = 두 세대 뒤 → 한 세대 뒤로 좁히려는 중.  중국 내수 한정은 2028년경까지로 관측.",{fill:C.ink3,fs:9,ff:SANS});
 mount("c-cxmt",s);})();

/* ══ 04·4 CXMT 경제성 ══ */
(function(){
 const W=520,H=274,s=svg(W,H);
 const L=112,R=92,T=54,RH=40,pw=W-L-R;
 const D=[{n:"빅3 영업이익률",v:78,c:C.s2,d:"76~80% 범위 중앙"},
          {n:"CXMT 영업이익률",v:50,c:C.s1,d:"방송: 약 50%"},
          {n:"CXMT 순이익률",v:51.7,c:C.s1,d:"15조 ÷ 29조 (계산)"}];
 [0,25,50,75,100].forEach(function(v){
  el(s,"line",{x1:L+pw*v/100,x2:L+pw*v/100,y1:T-16,y2:T+D.length*RH-18,stroke:C.line,"stroke-width":1});
  tx(s,L+pw*v/100,T-22,v+"%",{ta:"middle",fill:C.ink3,fs:9});});
 D.forEach(function(d,i){
  const y=T+i*RH;
  tx(s,L-10,y+1,d.n,{ta:"end",fill:C.ink,fs:10.5,ff:SANS});
  tx(s,L-10,y+14,d.d,{ta:"end",fill:C.ink3,fs:8.5,ff:SANS});
  el(s,"line",{x1:L,x2:L+pw*d.v/100,y1:y,y2:y,stroke:d.c,"stroke-width":2,opacity:.4});
  el(s,"circle",{cx:L+pw*d.v/100,cy:y,r:6.5,fill:d.c});
  tx(s,L+pw*d.v/100+11,y+4,d.v.toFixed(1)+"%",{fill:d.c,fs:11.5,fw:700});});
 el(s,"line",{x1:L+pw*50/100,x2:L+pw*78/100,y1:T+D.length*RH,y2:T+D.length*RH,stroke:C.s4,"stroke-width":1.6});
 tx(s,L+pw*64/100,T+D.length*RH+16,"28%p 격차",{ta:"middle",fill:C.s4,fs:10.5,fw:700});
 el(s,"line",{x1:0,x2:W,y1:T+D.length*RH+30,y2:T+D.length*RH+30,stroke:C.line,"stroke-width":1});
 tx(s,0,T+D.length*RH+50,"DDR5 원가가 빅3보다 30% 비싼데도 흑자다.",{fill:C.ink,fs:11,ff:SANS,fw:500});
 tx(s,0,T+D.length*RH+66,"→ 기술 우위가 아니라 품귀의 증거. 가격이 정상화되면 이 이익률은 먼저 무너진다.",{fill:C.s1,fs:10,ff:SANS});
 tx(s,0,H-6,"판정: 위협은 실재하나 시점은 2028년 이후. 범용 DRAM에 하방 요인, HBM에는 아직 무관.",{fill:C.ink3,fs:9.5,ff:SANS});
 mount("c-cxecon",s);})();

/* ══ 04·5 HBM 점유율 ══ */
(function(){
 const W=520,H=248,s=svg(W,H);
 const L=104,R=104,T=54,RH=44,pw=W-L-R;
 const D=[{n:"SK하이닉스",q1:null,q2:58,c:C.s5,d:"하락 중"},
          {n:"삼성전자",q1:21,q2:35,c:C.s2,d:"21% → 30%대 중반"},
          {n:"마이크론",q1:null,q2:21,c:C.s3,d:"—"}];
 [0,20,40,60].forEach(function(v){
  el(s,"line",{x1:L+pw*v/60,x2:L+pw*v/60,y1:T-16,y2:T+D.length*RH-20,stroke:C.line,"stroke-width":1});
  tx(s,L+pw*v/60,T-22,v+"%",{ta:"middle",fill:C.ink3,fs:9});});
 D.forEach(function(d,i){
  const y=T+i*RH;
  tx(s,L-10,y+1,d.n,{ta:"end",fill:C.ink,fs:10.5,ff:SANS,fw:500});
  tx(s,L-10,y+14,d.d,{ta:"end",fill:C.ink3,fs:8.5,ff:SANS});
  if(d.q1!==null){
    el(s,"line",{x1:L+pw*d.q1/60,x2:L+pw*d.q2/60,y1:y,y2:y,stroke:d.c,"stroke-width":2.6,opacity:.55});
    el(s,"circle",{cx:L+pw*d.q1/60,cy:y,r:4.5,fill:C.surf,stroke:C.ink3,"stroke-width":1.6});
    tx(s,L+pw*d.q1/60,y-11,"Q1 "+d.q1,{ta:"middle",fill:C.ink3,fs:9});
  } else { el(s,"line",{x1:L,x2:L+pw*d.q2/60,y1:y,y2:y,stroke:d.c,"stroke-width":2,opacity:.28}); }
  el(s,"circle",{cx:L+pw*d.q2/60,cy:y,r:6.5,fill:d.c});
  tx(s,L+pw*d.q2/60+11,y+4,d.q2+"%",{fill:d.c,fs:11.5,fw:700});});
 el(s,"line",{x1:0,x2:W,y1:T+D.length*RH-4,y2:T+D.length*RH-4,stroke:C.line2,"stroke-width":1});
 tx(s,0,T+D.length*RH+16,"세 숫자의 합",{fill:C.ink3,fs:10,ff:SANS});
 tx(s,120,T+D.length*RH+16,"114%",{fill:C.s4,fs:15,fw:700});
 tx(s,180,T+D.length*RH+16,"— 최소 하나는 분기·기준이 다르다",{fill:C.s4,fs:10,ff:SANS});
 tx(s,0,T+D.length*RH+36,"모순을 평균으로 덮지 않고 그대로 표시한다. 순위는 신뢰하되 수준은 신뢰하지 않는다.",{fill:C.ink3,fs:9.5,ff:SANS});
 tx(s,0,H-6,"방향만 채택: SK 하락 · 삼성 급등 · 마이크론 정체.  삼성의 한 분기 +14%p는 이 사이클에서 가장 큰 점유율 이동이다.",{fill:C.ink3,fs:9,ff:SANS});
 mount("c-hbm",s);})();

/* ══ 04·6 NVHBM ══ */
(function(){
 const W=520,H=316,s=svg(W,H);
 // 상단: 핀 속도 요구
 const L=112,R=94,T=52,RH=34,pw=W-L-R;
 const D=[{n:"HBM4 표준",v:10,c:C.ink3},{n:"삼성 현재",v:11.7,c:C.s2},{n:"NVHBM 요구",v:17.5,c:C.s4}];
 [8,12,16,20].forEach(function(v){
  el(s,"line",{x1:L+pw*(v-8)/12,x2:L+pw*(v-8)/12,y1:T-16,y2:T+D.length*RH-18,stroke:C.line,"stroke-width":1});
  tx(s,L+pw*(v-8)/12,T-22,v,{ta:"middle",fill:C.ink3,fs:9});});
 D.forEach(function(d,i){
  const y=T+i*RH;
  tx(s,L-10,y+4,d.n,{ta:"end",fill:C.ink,fs:10.5,ff:SANS});
  el(s,"line",{x1:L,x2:L+pw*(d.v-8)/12,y1:y,y2:y,stroke:d.c,"stroke-width":2,opacity:.4});
  el(s,"circle",{cx:L+pw*(d.v-8)/12,cy:y,r:6,fill:d.c});
  tx(s,L+pw*(d.v-8)/12+10,y+4,d.v+"Gbps",{fill:d.c,fs:10.5,fw:700});});
 tx(s,0,20,"적층은 8단 고정 · 속도만 올린다 → 경쟁축이 '몇 단'에서 '얼마나 빠른가'로 이동",{fill:C.ink,fs:10.5,ff:SANS});
 tx(s,L,T+D.length*RH+2,"삼성 기준 +49.6% 필요",{fill:C.s4,fs:10,fw:700});
 // 하단: 베이스다이 조달
 el(s,"line",{x1:0,x2:W,y1:T+D.length*RH+18,y2:T+D.length*RH+18,stroke:C.line2,"stroke-width":1});
 const yb=T+D.length*RH+40;
 tx(s,0,yb,"베이스 다이 파운드리",{fill:C.ink3,fs:10,ff:SANS});
 const B=[{n:"삼성전자",v:"자사 4nm",c:C.s2,s:"내재화 — 속도 튜닝 자유도 최대"},
          {n:"SK하이닉스",v:"TSMC 12nm",c:C.s1,s:"인텔 이원화 추진 중"},
          {n:"마이크론",v:"자사 팹",c:C.s4,s:"내재화이나 성능 열위"}];
 B.forEach(function(b,i){
  const y=yb+22+i*30;
  el(s,"rect",{x:0,y:y-12,width:3,height:24,fill:b.c});
  tx(s,11,y+4,b.n,{fill:C.ink,fs:11,ff:SANS,fw:500});
  tx(s,102,y+4,b.v,{fill:b.c,fs:10.5,fw:700});
  tx(s,196,y+4,b.s,{fill:C.ink3,fs:9.5,ff:SANS});});
 tx(s,0,H-6,"승부처가 파운드리로 옮겨가면 유일한 내재화 선단 공정 보유자가 유리해진다 — 이것이 삼성 비중을 동률로 올린 근거",{fill:C.ink3,fs:9,ff:SANS});
 mount("c-nvhbm",s);})();

/* ══ 05·1 매물벽 ══ */
(function(){
 const W=520,H=262,L=52,R=52,T=42,B=66,s=svg(W,H),pw=W-L-R,ph=H-T-B;
 const lo=6000,hi=7800;
 const X=v=>L+pw*(v-lo)/(hi-lo);
 // 매물 분포 (INF: 7,000 위에 집중)
 const BINS=[];
 for(let v=6000;v<7800;v+=100){
   const m = v<7000 ? 0.08 : Math.exp(-Math.pow((v-7250)/380,2));
   BINS.push({v:v,m:m});}
 const mx=Math.max.apply(null,BINS.map(b=>b.m));
 BINS.forEach(function(b){
  const h=ph*b.m/mx, x=X(b.v), w=pw/BINS.length-1.5;
  el(s,"rect",{x:x,y:T+ph-h,width:w,height:h,fill:b.v<7000?C.ink3:C.s4,opacity:b.v<7000?.3:.72});});
 el(s,"line",{x1:L,x2:L+pw,y1:T+ph,y2:T+ph,stroke:C.line2,"stroke-width":1.2});
 [6000,6579,7000,7500,7800].forEach(function(v){
  el(s,"line",{x1:X(v),x2:X(v),y1:T+ph,y2:T+ph+5,stroke:C.line2,"stroke-width":1});
  tx(s,X(v),T+ph+18,fmt(v),{ta:"middle",fill:v===6579?C.ink:C.ink3,fs:9.5,fw:v===6579?700:400});});
 el(s,"line",{x1:X(6579),x2:X(6579),y1:T,y2:T+ph,stroke:C.ink,"stroke-width":1.4,"stroke-dasharray":"4 3"});
 tx(s,X(6579)-6,T+12,"현재",{ta:"end",fill:C.ink,fs:10,ff:SANS});
 el(s,"line",{x1:X(7000),x2:X(7000),y1:T,y2:T+ph,stroke:C.s4,"stroke-width":1.4});
 tx(s,X(7000)+6,T+12,"7,000 — 매물 시작선",{fill:C.s4,fs:10,ff:SANS,fw:700});
 el(s,"line",{x1:X(7500),x2:X(7500),y1:T,y2:T+ph,stroke:C.s2,"stroke-width":1.2,"stroke-dasharray":"3 3"});
 tx(s,X(7500)+6,T+ph-8,"7,500 개인 복귀선",{fill:C.s2,fs:9.5,ff:SANS});
 const N=[["묻힌 금액","160조",C.s4],["시총 대비","2.95%",C.s1],["8월 거래대금","2.4일치",C.s1],["흡수 소요","3.84일",C.s2]];
 N.forEach(function(n,i){const x=i*(W/4);
  tx(s,x+2,H-26,n[0],{fill:C.ink3,fs:9,ff:SANS});
  tx(s,x+2,H-10,n[1],{fill:n[2],fs:13,fw:700});});
 tx(s,0,20,"삼성전자 + SK하이닉스 개인 순매수 누적 · 분포 형태는 내 추정 (INF), 총액·비율은 방송·계산",{fill:C.ink3,fs:9.5,ff:SANS});
 mount("c-buried",s);})();

/* ══ 05·2 3주체 동시매도 ══ */
(function(){
 const W=520,H=300,s=svg(W,H);
 const CX=250,CY=148,R0=98,R1=44;
 const SELL=[{n:"개인",a:180},{n:"외국인",a:-90},{n:"기관",a:0}];
 SELL.forEach(function(sv){
  const ang=sv.a*Math.PI/180;
  const x0=CX+R0*Math.cos(ang), y0=CY+R0*Math.sin(ang);
  const x1=CX+R1*Math.cos(ang), y1=CY+R1*Math.sin(ang);
  const bw=64,bh=26;
  const sx=x0-(sv.a===180?-bw/2:(sv.a===0?bw/2:0));
  el(s,"line",{x1:x0,y1:y0,x2:x1,y2:y1,stroke:C.s4,"stroke-width":2.4});
  el(s,"path",{d:"M"+(x1-7*Math.cos(ang)+4.5*Math.sin(ang))+" "+(y1-7*Math.sin(ang)-4.5*Math.cos(ang))+
                 "L"+x1+" "+y1+
                 "L"+(x1-7*Math.cos(ang)-4.5*Math.sin(ang))+" "+(y1-7*Math.sin(ang)+4.5*Math.cos(ang))+"Z",fill:C.s4});
  el(s,"rect",{x:x0-bw/2,y:y0-bh/2,width:bw,height:bh,fill:C.surf2,stroke:C.s4,"stroke-width":1.2});
  tx(s,x0,y0+5,sv.n,{ta:"middle",fill:C.s4,fs:11,ff:SANS,fw:500});
  tx(s,x0,y0+bh/2+13,"순매도",{ta:"middle",fill:C.ink3,fs:9,ff:SANS});});
 el(s,"circle",{cx:CX,cy:CY,r:R1-4,fill:C.surf2,stroke:C.s2,"stroke-width":2});
 tx(s,CX,CY-2,"기타법인",{ta:"middle",fill:C.s2,fs:11.5,ff:SANS,fw:700});
 tx(s,CX,CY+14,"전량 흡수",{ta:"middle",fill:C.ink2,fs:9.5,ff:SANS});
 tx(s,0,20,"2026년 9월 4일 — 세 주체가 동시에 팔았고 기타법인 한 주체가 전부 받았다",{fill:C.ink,fs:10.5,ff:SANS});
 el(s,"line",{x1:0,x2:W,y1:238,y2:238,stroke:C.line,"stroke-width":1});
 tx(s,0,256,"기타법인의 정체 = 자사주 매입 (방송 해석)",{fill:C.ink2,fs:10.5,ff:SANS});
 tx(s,0,272,"“한국 증시 사상 처음”이라는 표현은 검증하지 못했다 — 주장으로만 기록한다",{fill:C.s1,fs:9.5,ff:SANS});
 tx(s,0,292,"함의: 밸류업 자사주가 새 최종 매수자라면 S3 바닥이 v1보다 높아야 한다 → 6,000 → 6,100 상향 근거",{fill:C.ink3,fs:9,ff:SANS});
 mount("c-3sellers",s);})();

/* ══ 05·3 급락 원인 심판 ══ */
(function(){
 const D=[{n:"실적·가이던스 훼손",v:"기각",c:C.s4,w:"9/4 개별 악재 없음. 미국장은 오히려 S&P +1%"},
          {n:"금리·물가 서프라이즈",v:"기각",c:C.s4,w:"같은 날 월러 발언은 완화 방향이었다"},
          {n:"엔캐리 청산",v:"보류",c:C.s1,w:"아시아 동반 하락과 정합. 다만 직접 증거 없음"},
          {n:"금융투자 ETF 물량",v:"채택",c:C.s2,w:"14시 집중, 종목 무차별, 6,400 방어 — 프로그램 성격"}];
 const W=880,L=0,MID=252,RX=330,T=42,RH=42,H=T+D.length*RH+40,s=svg(W,H);
 tx(s,0,20,"급락 원인 후보",{fill:C.ink3,fs:10,ff:SANS});
 tx(s,MID,20,"판정",{fill:C.ink3,fs:10,ff:SANS});
 tx(s,RX,20,"근거",{fill:C.ink3,fs:10,ff:SANS});
 D.forEach(function(d,i){
  const y=T+i*RH;
  el(s,"line",{x1:0,x2:W,y1:y-14,y2:y-14,stroke:C.line,"stroke-width":1});
  el(s,"rect",{x:0,y:y-14,width:3,height:RH,fill:d.c,opacity:.8});
  tx(s,12,y+5,d.n,{fill:C.ink,fs:11.5,ff:SANS});
  el(s,"rect",{x:MID,y:y-6,width:38,height:19,fill:"none",stroke:d.c,"stroke-width":1.3,rx:2});
  tx(s,MID+19,y+7,d.v,{ta:"middle",fill:d.c,fs:10.5,ff:SANS,fw:700});
  tx(s,RX,y+5,d.w,{fill:C.ink3,fs:10,ff:SANS});});
 const y2=T+D.length*RH+4;
 el(s,"line",{x1:0,x2:W,y1:y2-14,y2:y2-14,stroke:C.line2,"stroke-width":1});
 tx(s,0,y2+6,"외국인 개별주식선물 +20만 계약 순매수 전환",{fill:C.s2,fs:11,ff:SANS,fw:500});
 tx(s,RX,y2+6,"현물을 팔면서 선물을 샀다 = 방향 전환이 아니라 형태 전환",{fill:C.ink3,fs:10,ff:SANS});
 tx(s,0,H-6,"판정은 내 추론이다 — 방송은 후보를 나열했을 뿐 어느 것도 기각하지 않았다",{fill:C.ink3,fs:9.5,ff:SANS});
 mount("c-crash",s);})();

/* ══ 05·4 신용잔고 이자 ══ */
(function(){
 const W=520,H=238,s=svg(W,H);
 const L=64,R=64,T=54,ph=92,pw=W-L-R;
 // 잔고 x 금리 격자
 const RATES=[6,7,8,9,10];
 const BAL=[25,29,33,37];
 const cw=pw/RATES.length, rh=ph/BAL.length;
 BAL.forEach(function(b,i){
  RATES.forEach(function(r,j){
   const v=b*r/100, on=(b===33&&r===9);
   const t=(v-1.5)/(3.7-1.5);
   el(s,"rect",{x:L+j*cw,y:T+i*rh,width:cw-2,height:rh-2,
     fill:C.s2,opacity:.12+t*0.72,stroke:on?C.ink:"none","stroke-width":on?2:0});
   tx(s,L+j*cw+cw/2-1,T+i*rh+rh/2+4,v.toFixed(2),{ta:"middle",fill:on?"#0B101C":C.ink,fs:10,fw:on?700:400});});
  tx(s,L-8,T+i*rh+rh/2+4,b+"조",{ta:"end",fill:b===33?C.ink:C.ink3,fs:9.5,fw:b===33?700:400});});
 RATES.forEach(function(r,j){tx(s,L+j*cw+cw/2-1,T-8,r+"%",{ta:"middle",fill:r===9?C.ink:C.ink3,fs:9.5,fw:r===9?700:400});});
 tx(s,0,20,"신용융자 잔고 × 이자율 = 연간 이자수익 (조원)",{fill:C.ink,fs:10.5,ff:SANS});
 tx(s,L,T-24,"이자율 →",{fill:C.ink3,fs:9,ff:SANS});
 tx(s,0,T+ph/2,"잔고",{fill:C.ink3,fs:9,ff:SANS});
 el(s,"line",{x1:0,x2:W,y1:T+ph+16,y2:T+ph+16,stroke:C.line,"stroke-width":1});
 tx(s,0,T+ph+36,"현재 조합 33조 × 9% =",{fill:C.ink2,fs:11,ff:SANS});
 tx(s,166,T+ph+36,"연 2.97조",{fill:C.s2,fs:15,fw:700});
 tx(s,0,T+ph+54,"거래대금이 반토막 나도 이 수익은 남는다. 잔고가 25조로 줄어야 2.25조 — −24%.",{fill:C.ink3,fs:9.5,ff:SANS});
 tx(s,0,H-6,"→ 증권주는 거래대금 베팅이 아니라 잔고 × 금리 베팅이다. 한국금융지주의 논리를 베타에서 캐리로 교체한다.",{fill:C.s1,fs:9.5,ff:SANS});
 mount("c-credit",s);})();

/* ══ 06·1 종목 순위·비중 ══ */
(function(){
 const P=[
 {r:1,n:"SK하이닉스",code:"000660",bk:"반도체",bc:C.s5,o:12.0,w:13.5,px:1596000,eps:349342,tp:2300000,src:"5/5"},
 {r:2,n:"삼성전자",code:"005930",bk:"반도체",bc:C.s5,o:12.0,w:13.5,px:250000,eps:48339,tp:320000,src:"5/5"},
 {r:3,n:"한국금융지주",code:"071050",bk:"반도체",bc:C.s5,o:8.0,w:9.0,px:186600,eps:50012,tp:245000,src:"1/5"},
 {r:4,n:"SK스퀘어",code:"402340",bk:"반도체",bc:C.s5,o:8.0,w:9.0,px:981000,eps:327000,tp:1330000,src:"1/5"},
 {r:5,n:"KB금융",code:"105560",bk:"짧은듀레이션",bc:C.s2,o:10.0,w:12.5,px:null,eps:null,tp:null,src:"3/5"},
 {r:6,n:"현대모비스",code:"012330",bk:"짧은듀레이션",bc:C.s2,o:10.0,w:12.5,px:423500,eps:45652,tp:525000,src:"1/5"},
 {r:7,n:"HD현대일렉트릭",code:"267260",bk:"헤지",bc:C.s3,o:12.0,w:12.0,px:706000,eps:26440,tp:860000,src:"1/5"},
 {r:8,n:"LIG넥스원",code:"079550",bk:"헤지",bc:C.s3,o:8.0,w:8.0,px:null,eps:null,tp:null,src:"0/5"},
 {r:9,n:"대한항공",code:"003490",bk:"유가↓",bc:C.s1,o:11.0,w:5.5,px:null,eps:null,tp:null,src:"4/5"},
 {r:10,n:"한국전력",code:"015760",bk:"유가↓",bc:C.s1,o:9.0,w:4.5,px:null,eps:null,tp:null,src:"3/5"}];
 const W=880,L=0,T=58,RH=38,H=T+P.length*RH+56,s=svg(W,H);
 const CN=176, CB=272, CW1=372, CW2=470, CPER=560, CUP=648, CBAR=700;
 const hdr=[[12,"종목"],[CN,"코드"],[CB,"버킷"],[CW1,"v2"],[CW2,"v3"],[CPER,"PER"],[CUP,"상승여력"],[CBAR,"비중 v2 → v3"]];
 hdr.forEach(h=>tx(s,h[0],26,h[1],{fill:C.ink3,fs:9.5,ff:SANS}));
 el(s,"line",{x1:0,x2:W,y1:36,y2:36,stroke:C.line2,"stroke-width":1});
 const pw=W-CBAR-20, mxw=14;
 P.forEach(function(p,i){
  const y=T+i*RH;
  el(s,"line",{x1:0,x2:W,y1:y+16,y2:y+16,stroke:C.line,"stroke-width":1});
  tx(s,0,y+4,p.r,{fill:C.ink3,fs:10});
  tx(s,20,y+4,p.n,{fill:C.ink,fs:11.5,ff:SANS,fw:500});
  tx(s,CN,y+4,p.code,{fill:C.ink3,fs:9.5});
  el(s,"rect",{x:CB,y:y-8,width:9,height:9,fill:p.bc});
  tx(s,CB+14,y+4,p.bk,{fill:p.bc,fs:9.5,ff:SANS});
  tx(s,CW1+22,y+4,p.o.toFixed(1),{ta:"end",fill:C.ink3,fs:10});
  const dw=p.w-p.o, dc=dw>0.05?C.s2:(dw<-0.05?C.s4:C.ink3);
  tx(s,CW2+22,y+4,p.w.toFixed(1),{ta:"end",fill:dc,fs:10.5,fw:700});
  const per=p.px?p.px/p.eps:null, up=p.tp?(p.tp/p.px-1)*100:null;
  tx(s,CPER+30,y+4,per?per.toFixed(1)+"x":"n/a",{ta:"end",fill:per?(per<10?C.s2:C.s1):C.ink3,fs:10});
  tx(s,CUP+40,y+4,up?sgn(up,0)+"%":"n/a",{ta:"end",fill:up?C.s2:C.ink3,fs:10});
  // 비중 막대
  el(s,"line",{x1:CBAR,x2:CBAR+pw*p.o/mxw,y1:y,y2:y,stroke:C.ink3,"stroke-width":1.4,opacity:.55});
  el(s,"circle",{cx:CBAR+pw*p.o/mxw,cy:y,r:3.5,fill:C.surf,stroke:C.ink3,"stroke-width":1.4});
  el(s,"line",{x1:CBAR+pw*p.o/mxw,x2:CBAR+pw*p.w/mxw,y1:y,y2:y,stroke:dc,"stroke-width":2.4});
  el(s,"circle",{cx:CBAR+pw*p.w/mxw,cy:y,r:5.5,fill:dc});});
 const y2=T+P.length*RH+6;
 el(s,"line",{x1:0,x2:W,y1:y2-6,y2:y2-6,stroke:C.line2,"stroke-width":1});
 tx(s,0,y2+12,"교체 0건 · 순위 이동 2건 (HD현대일렉트릭 9→7, 대한항공 7→9) · 비중 이동 8건",{fill:C.ink,fs:10.5,ff:SANS});
 tx(s,0,y2+30,"규칙: 숫자가 규칙을 깬 종목만 교체한다. 이틀치 방송으로 이름을 바꾸면 모형이 아니라 뉴스추종이다.",{fill:C.s1,fs:9.5,ff:SANS});
 tx(s,0,y2+46,"PER = 현재가 ÷ 2026E EPS (봇C 2차출처, 미검증) · n/a = 출처 미확보 · 상승여력 = 봇C 목표가 기준",{fill:C.ink3,fs:9,ff:SANS});
 mount("c-rank",s);})();

/* ══ 06·2 유가 버킷 감쇄 ══ */
(function(){
 const W=520,H=272,s=svg(W,H);
 const L=112,R=118,T=62,RH=36,pw=W-L-R;
 const D=[{n:"S1 데탕트",a:30.9,b:17.0,c:C.s2},{n:"S2 지연",a:5.0,b:2.8,c:C.s1},
          {n:"S3 스태그",a:-18.2,b:-18.2,c:C.s4},{n:"S4 공급함정",a:8.0,b:8.0,c:C.s3}];
 const mn=-22,mx=34;
 const X=v=>L+pw*(v-mn)/(mx-mn);
 [-20,-10,0,10,20,30].forEach(function(v){
  el(s,"line",{x1:X(v),x2:X(v),y1:T-16,y2:T+D.length*RH-18,stroke:v===0?C.line2:C.line,"stroke-width":v===0?1.4:1});
  tx(s,X(v),T-22,(v>0?"+":"")+v,{ta:"middle",fill:C.ink3,fs:9});});
 D.forEach(function(d,i){
  const y=T+i*RH, same=Math.abs(d.a-d.b)<.01;
  tx(s,L-10,y+4,d.n,{ta:"end",fill:C.ink,fs:10.5,ff:SANS});
  el(s,"line",{x1:X(d.a),x2:X(d.b),y1:y,y2:y,stroke:same?C.line2:C.s4,"stroke-width":2.6});
  el(s,"circle",{cx:X(d.a),cy:y,r:4.5,fill:C.surf,stroke:C.ink3,"stroke-width":1.6});
  el(s,"circle",{cx:X(d.b),cy:y,r:6,fill:same?C.surf:d.c,stroke:same?C.ink3:d.c,"stroke-width":1.6});
  tx(s,W-58,y+4,same?"—":sgn(d.a,1),{ta:"end",fill:C.ink3,fs:9.5});
  tx(s,W-2,y+4,sgn(d.b,1),{ta:"end",fill:same?C.ink3:d.c,fs:11,fw:700});});
 tx(s,W-58,T-22,"이전",{ta:"end",fill:C.ink3,fs:9,ff:SANS});
 tx(s,W-2,T-22,"이후",{ta:"end",fill:C.ink3,fs:9,ff:SANS});
 el(s,"line",{x1:0,x2:W,y1:T+D.length*RH-6,y2:T+D.length*RH-6,stroke:C.line,"stroke-width":1});
 tx(s,0,T+D.length*RH+14,"버킷 기대수익",{fill:C.ink3,fs:10,ff:SANS});
 tx(s,110,T+D.length*RH+14,"+11.29%",{fill:C.ink3,fs:12});
 tx(s,180,T+D.length*RH+14,"→",{fill:C.ink3,fs:12});
 tx(s,202,T+D.length*RH+14,"+5.76%",{fill:C.s4,fs:14,fw:700});
 tx(s,274,T+D.length*RH+14,"거의 반토막",{fill:C.s4,fs:10,ff:SANS});
 tx(s,0,20,"유가 하락이 '금리 인하'로 번역되던 경로가 사라지고",{fill:C.ink,fs:10.5,ff:SANS});
 tx(s,0,36,"'연료비 절감'만 남는다",{fill:C.ink,fs:10.5,ff:SANS});
 tx(s,0,H-22,"감쇄계수 0.55는 내 가정 — S1·S2의 정책 기여분만 제거하고 원가 기여분은 보존했다.",{fill:C.ink3,fs:9,ff:SANS});
 tx(s,0,H-8,"S3·S4는 원래 원가 논리라 불변. 그래서 두 행은 점이 겹친다.",{fill:C.ink3,fs:9,ff:SANS});
 mount("c-oilbucket",s);})();

/* ══ 06·3 가중 후보 ══ */
(function(){
 const D=[{n:"A 문서2 계승",w:"40/20/20/20",e:11.69,s3:-6.29},
          {n:"B 유가축소·헤지유지",w:"40/25/10/25",e:12.14,s3:-3.64},
          {n:"C 채택",w:"45/25/10/20",e:12.47,s3:-5.13,on:1},
          {n:"D 공격",w:"50/20/10/20",e:12.82,s3:-5.96}];
 const IE=12.22, IS=-7.28;
 const W=520,H=308,L=70,R=70,T=64,B=96,s=svg(W,H),pw=W-L-R,ph=H-T-B;
 const xmn=11.3,xmx=13.2, ymn=-8.4,ymx=-2.8;
 const X=v=>L+pw*(v-xmn)/(xmx-xmn), Y=v=>T+ph*(1-(v-ymn)/(ymx-ymn));
 [11.5,12.0,12.5,13.0].forEach(function(v){
  el(s,"line",{x1:X(v),x2:X(v),y1:T,y2:T+ph,stroke:C.line,"stroke-width":1});
  tx(s,X(v),T+ph+16,"+"+v.toFixed(1)+"%",{ta:"middle",fill:C.ink3,fs:9});});
 [-8,-7,-6,-5,-4,-3].forEach(function(v){
  el(s,"line",{x1:L,x2:L+pw,y1:Y(v),y2:Y(v),stroke:C.line,"stroke-width":1});
  tx(s,L-8,Y(v)+3.5,v+"%",{ta:"end",fill:C.ink3,fs:9});});
 el(s,"rect",{x:X(IE),y:T,width:L+pw-X(IE),height:Y(IS)-T,fill:C.s2,opacity:.07});
 el(s,"line",{x1:X(IE),x2:X(IE),y1:T,y2:T+ph,stroke:C.s4,"stroke-width":1.4,"stroke-dasharray":"4 3"});
 el(s,"line",{x1:L,x2:L+pw,y1:Y(IS),y2:Y(IS),stroke:C.s4,"stroke-width":1.4,"stroke-dasharray":"4 3"});
 tx(s,L+pw,T-10,"기대·하방 동시 우위 구역",{ta:"end",fill:C.s2,fs:9.5,ff:SANS});
 tx(s,X(IE)-5,T+ph-6,"지수 +12.22",{ta:"end",fill:C.s4,fs:9.5});
 tx(s,L+3,Y(IS)+13,"지수 −7.28",{fill:C.s4,fs:9.5});
 D.forEach(function(d){
  const x=X(d.e), y=Y(d.s3);
  el(s,"circle",{cx:x,cy:y,r:d.on?8:5.5,fill:d.on?C.s2:C.surf,stroke:d.on?C.s2:C.ink2,"stroke-width":2});
  tx(s,x,y-(d.on?15:13),d.n,{ta:"middle",fill:d.on?C.s2:C.ink2,fs:10,ff:SANS,fw:d.on?700:400});
  tx(s,x,y+(d.on?24:21),d.w,{ta:"middle",fill:C.ink3,fs:9});});
 tx(s,0,18,"가로 = 확률가중 기대수익 · 세로 = S3 하방 (위로 갈수록 얕다)",{fill:C.ink3,fs:9.5,ff:SANS});
 tx(s,0,36,"비중 표기 = 반도체 / 짧은듀레이션 / 유가↓ / 헤지",{fill:C.ink3,fs:9.5,ff:SANS});
 el(s,"line",{x1:0,x2:W,y1:T+ph+32,y2:T+ph+32,stroke:C.line,"stroke-width":1});
 tx(s,0,T+ph+52,"A는 하방만 이기고 기대에서 진다. D는 기대만 크고 하방 여유가 얇다.",{fill:C.ink3,fs:9.5,ff:SANS});
 tx(s,0,T+ph+68,"C만 두 축 모두 지수 위 — 기대 +0.24%p, 하방 +2.15%p.",{fill:C.s2,fs:10,ff:SANS});
 tx(s,0,T+ph+84,"초과수익은 작지만 방향이 맞다. 이 정도가 재가중 이후 정직하게 남는 몫이다.",{fill:C.ink3,fs:9.5,ff:SANS});
 mount("c-cands",s);})();

/* ══ 06·4 반도체 상한 불변 ══ */
(function(){
 const W=520,H=250,L=58,R=76,T=44,B=52,s=svg(W,H),pw=W-L-R,ph=H-T-B;
 const WS=[20,30,40,50,60];
 const V1=[-4.13,-5.87,-7.60,-9.33,-11.07], I1=-8.80;
 const V2=[-3.42,-4.86,-6.29,-7.72,-9.16],  I2=-7.28;
 const mn=-12,mx=-3;
 const X=i=>L+pw*i/(WS.length-1), Y=v=>T+ph*(1-(v-mn)/(mx-mn));
 [-12,-10,-8,-6,-4].forEach(function(v){
  el(s,"line",{x1:L,x2:L+pw,y1:Y(v),y2:Y(v),stroke:C.line,"stroke-width":1});
  tx(s,L-8,Y(v)+3.5,v+"%",{ta:"end",fill:C.ink3,fs:9});});
 [[V1,I1,C.ink3,"v1"],[V2,I2,C.s5,"v2"]].forEach(function(g){
  let d="";g[0].forEach(function(v,i){d+=(i?"L":"M")+X(i)+" "+Y(v);});
  el(s,"path",{d:d,fill:"none",stroke:g[2],"stroke-width":2.2,opacity:g[3]==="v1"?.6:1});
  g[0].forEach(function(v,i){el(s,"circle",{cx:X(i),cy:Y(v),r:4,fill:g[3]==="v1"?C.surf:g[2],stroke:g[2],"stroke-width":1.8});});
  el(s,"line",{x1:L,x2:L+pw,y1:Y(g[1]),y2:Y(g[1]),stroke:g[2],"stroke-width":1.2,"stroke-dasharray":"4 3",opacity:.7});
  tx(s,L+pw+6,Y(g[1])+3.5,"지수 "+g[1],{fill:g[2],fs:9.5});});
 // 교차점 46.9%
 const xc=L+pw*(46.9-20)/40;
 el(s,"line",{x1:xc,x2:xc,y1:T,y2:T+ph,stroke:C.s1,"stroke-width":1.6});
 tx(s,xc,T-8,"상한 46.9%",{ta:"middle",fill:C.s1,fs:10.5,ff:SANS,fw:700});
 WS.forEach(function(w,i){tx(s,X(i),T+ph+16,w+"%",{ta:"middle",fill:C.ink3,fs:10});});
 tx(s,L,20,"● v2",{fill:C.s5,fs:10,ff:SANS});
 tx(s,L+44,20,"○ v1",{fill:C.ink3,fs:10,ff:SANS});
 tx(s,0,H-22,"두 곡선이 각자의 지수선을 같은 x에서 뚫는다 — 확률을 바꿔도 상한은 그대로다.",{fill:C.ink,fs:10,ff:SANS});
 tx(s,0,H-6,"상한이 확률이 아니라 버킷 계수의 비율에서 나오기 때문. 재가중에 대해 구조적으로 강건한 유일한 숫자.",{fill:C.ink3,fs:9,ff:SANS});
 mount("c-semicap",s);})();

/* ══ 06·5 지수 대비 ══ */
(function(){
 const R=[{k:"S1",n:"데탕트",p1:28.0,p2:23.0,i1:25.5,i2:22.51,c:C.s2},
          {k:"S2",n:"지연",p1:11.4,p2:11.4,i1:10.2,i2:10.20,c:C.s1},
          {k:"S3",n:"스태그",p1:-7.2,p2:-6.0,i1:-8.8,i2:-7.28,c:C.s4},
          {k:"S4",n:"공급함정",p1:11.2,p2:11.2,i1:13.9,i2:13.89,c:C.s3},
          {k:"기대",n:"확률가중",p1:12.63,p2:13.07,i1:11.54,i2:12.22,c:C.ink,b:1}];
 const W=880,L=118,R2=190,T=62,RH=42,H=T+R.length*RH+52,s=svg(W,H);
 const pw=W-L-R2, mn=-12,mx=30;
 const X=v=>L+pw*(v-mn)/(mx-mn);
 [-10,0,10,20,30].forEach(function(v){
  el(s,"line",{x1:X(v),x2:X(v),y1:T-16,y2:T+R.length*RH-18,stroke:v===0?C.line2:C.line,"stroke-width":v===0?1.4:1});
  tx(s,X(v),T-22,(v>0?"+":"")+v,{ta:"middle",fill:C.ink3,fs:9});});
 tx(s,0,18,"◆ 포트 v2",{fill:C.s2,fs:10,ff:SANS});
 tx(s,72,18,"◇ 지수 v2",{fill:C.ink3,fs:10,ff:SANS});
 tx(s,W-R2+30,18,"초과분  v1 → v2",{fill:C.ink3,fs:10,ff:SANS});
 R.forEach(function(r,i){
  const y=T+i*RH;
  if(r.b)el(s,"line",{x1:0,x2:W,y1:y-16,y2:y-16,stroke:C.line2,"stroke-width":1});
  tx(s,L-12,y+4,r.k+" "+r.n,{ta:"end",fill:r.c,fs:11,ff:SANS,fw:r.b?700:500});
  const d1=r.p1-r.i1, d2=r.p2-r.i2;
  el(s,"line",{x1:X(r.i2),x2:X(r.p2),y1:y,y2:y,stroke:d2>0?C.s2:C.s4,"stroke-width":2.4,opacity:.6});
  el(s,"path",{d:"M"+X(r.i2)+" "+(y-5)+"L"+(X(r.i2)+5)+" "+y+"L"+X(r.i2)+" "+(y+5)+"L"+(X(r.i2)-5)+" "+y+"Z",
    fill:C.surf,stroke:C.ink3,"stroke-width":1.5});
  el(s,"path",{d:"M"+X(r.p2)+" "+(y-6.5)+"L"+(X(r.p2)+6.5)+" "+y+"L"+X(r.p2)+" "+(y+6.5)+"L"+(X(r.p2)-6.5)+" "+y+"Z",
    fill:r.c});
  const lft=Math.min(X(r.p2),X(r.i2))-12, rgt=Math.max(X(r.p2),X(r.i2))+12;
  tx(s,r.p2<0?lft:rgt,y+4,sgn(r.p2,1),{ta:r.p2<0?"end":"start",fill:r.c,fs:10.5,fw:700});
  // 초과분 v1 -> v2
  const bx=W-R2+30, bw=110, sx=v=>bx+bw*(v+2)/6;
  el(s,"line",{x1:sx(0),x2:sx(0),y1:y-13,y2:y+13,stroke:C.line2,"stroke-width":1});
  el(s,"line",{x1:sx(d1),x2:sx(d2),y1:y,y2:y,stroke:Math.abs(d2)<Math.abs(d1)?C.s4:C.s2,"stroke-width":2});
  el(s,"circle",{cx:sx(d1),cy:y,r:3.5,fill:C.surf,stroke:C.ink3,"stroke-width":1.4});
  el(s,"circle",{cx:sx(d2),cy:y,r:5,fill:Math.abs(d2)<Math.abs(d1)?C.s4:C.s2});
  tx(s,W-2,y+4,sgn(d2,2),{ta:"end",fill:Math.abs(d2)<Math.abs(d1)?C.s4:C.s2,fs:10,fw:700});});
 tx(s,0,H-24,"S1 초과 +2.5 → +0.5, 기대 초과 +1.09 → +0.84.  S3 방어 우위도 +1.60 → +1.32로 얇아졌다.",{fill:C.ink,fs:10.5,ff:SANS});
 tx(s,0,H-8,"꼬리 확률을 깎으면 헤지의 값어치가 같이 깎인다 — 내가 내 손으로 내 포트폴리오의 알파를 줄인 셈이다.",{fill:C.s4,fs:9.5,ff:SANS});
 mount("c-vsidx",s);})();

/* ══ 06·6 PBR ↔ PER ══ */
(function(){
 const D=[{n:"삼성전자",px:250000,pbr:1.5,bps:166667,lo:333333,hi:416667,tp:320000,tpb:1.92},
          {n:"SK하이닉스",px:1596000,pbr:1.7,bps:938824,lo:1877647,hi:2347059,tp:2300000,tpb:2.45}];
 const W=520,H=290,L=94,R=64,T=76,RH=86,s=svg(W,H),pw=W-L-R;
 const mn=1.0,mx=2.8;
 const X=v=>L+pw*(v-mn)/(mx-mn);
 [1.0,1.5,2.0,2.5].forEach(function(v){
  el(s,"line",{x1:X(v),x2:X(v),y1:T-16,y2:T+D.length*RH-30,stroke:C.line,"stroke-width":1});
  tx(s,X(v),T-22,v.toFixed(1)+"x",{ta:"middle",fill:C.ink3,fs:9});});
 el(s,"rect",{x:X(2.0),y:T-16,width:X(2.5)-X(2.0),height:D.length*RH-14,fill:C.s2,opacity:.09});
 tx(s,X(2.25),T-38,"호황 PBR 밴드 2.0~2.5x",{ta:"middle",fill:C.s2,fs:10,ff:SANS,fw:700});
 D.forEach(function(d,i){
  const y=T+i*RH;
  tx(s,L-10,y+4,d.n,{ta:"end",fill:C.ink,fs:11,ff:SANS,fw:500});
  tx(s,L-10,y+18,"BPS "+fmt(Math.round(d.bps/10000),1)+"만",{ta:"end",fill:C.ink3,fs:8.5,ff:SANS});
  el(s,"line",{x1:X(d.pbr),x2:X(2.5),y1:y,y2:y,stroke:C.line2,"stroke-width":1.4,"stroke-dasharray":"3 3"});
  el(s,"circle",{cx:X(d.pbr),cy:y,r:6,fill:C.s1});
  tx(s,X(d.pbr)-12,y+4,"현재 "+d.pbr+"x",{ta:"end",fill:C.s1,fs:10,fw:700});
  const inb=d.tpb>=2.0&&d.tpb<=2.5, col=inb?C.s2:C.s4;
  el(s,"circle",{cx:X(d.tpb),cy:y,r:7,fill:"none",stroke:col,"stroke-width":2.4});
  el(s,"circle",{cx:X(d.tpb),cy:y,r:2.5,fill:col});
  tx(s,X(d.tpb),y+22,"봇C 목표 "+d.tpb.toFixed(2)+"x",{ta:"middle",fill:col,fs:10,fw:700});
  tx(s,X(d.tpb),y+35,inb?"밴드 안":"밴드 아래 −0.08x",{ta:"middle",fill:col,fs:9,ff:SANS});
  // 밴드 하단/상단 가격
  tx(s,X(2.0),y+48,fmt(Math.round(d.lo/10000))+"만",{ta:"middle",fill:C.ink3,fs:9});
  tx(s,X(2.5),y+48,fmt(Math.round(d.hi/10000))+"만",{ta:"middle",fill:C.ink3,fs:9});});
 tx(s,0,20,"두 프레임이 만난다 — PER로 뽑은 목표가가 PBR 밴드 안에 떨어지는가",{fill:C.ink,fs:10.5,ff:SANS});
 tx(s,0,H-20,"SK하이닉스 2.45x = 밴드 상단 근처, 삼성전자 1.92x = 밴드 진입 직전.",{fill:C.ink3,fs:9.5,ff:SANS});
 tx(s,0,H-5,"→ 봇C 목표가는 두 프레임에서 모두 방어된다. 다만 SK는 상단이라 추가 여유가 얇다.",{fill:C.s1,fs:9.5,ff:SANS});
 mount("c-pbr",s);})();

/* ══ 07·1 누적 판정 ══ */
(function(){
 const D=[
  {t:"9/2 −4.00% 하락폭",v:"확정",s:"원장 6,835.80 → 6,562.43로 정확히 재현"},
  {t:"브로드컴 가이던스 미스 −0.66%",v:"확정",s:"34.8B vs 컨센 35.03B"},
  {t:"실질중립 3.1−2.0=1.10%",v:"확정",s:"산술 검증"},
  {t:"인상확률 63% (9/3)",v:"확정",s:"9/4 방송이 50%로 인용, 경로 정합"},
  {t:"CXMT 순이익률 51.7%",v:"확정",s:"15조 ÷ 29조"},
  {t:"랙 전력 60배",v:"확정",s:"10 → 600kW"},
  {t:"신용잔고 이자 2.97조",v:"확정",s:"33조 × 9%"},
  {t:"FOMC 12표 중 7표 필요",v:"확정",s:"7월 반대 3인 전원 지역총재"},
  {t:"디아이 003160 = 코스피",v:"확정",s:"봇A 오분류 정정 (문서3)"},
  {t:"고점 9,300",v:"부분",s:"산술은 맞으나 같은 표본의 채권논리와 충돌"},
  {t:"12M fwd PER 5.7x",v:"부분",s:"EPS 추정치 출처 불명"},
  {t:"HBM 점유율 3사",v:"부분",s:"합계 114% — 기준 불일치"},
  {t:"CXMT capa 30→36만장",v:"부분",s:"굿다이 40% 반영 시 유효 12→14.4만장"},
  {t:"6주 하락 → 12~18주 회복",v:"부분",s:"표본 수·조건부 확률 미제시"},
  {t:"기타법인 3주체 흡수 '사상 처음'",v:"부분",s:"주장은 기록, 사실 확인 불가"},
  {t:"브로드컴-엔비디아 시소",v:"기각",s:"숫자는 맞고 인과가 틀림"},
  {t:"4Q 인하 (헤드라인 PCE 근거)",v:"기각",s:"쓴 지표로는 −1.05%p 미달"},
  {t:"삼성전기·두산 코어 편입",v:"기각",s:"PER 68x·159x — 내 문서3 자기수정"},
  {t:"9/4 급락 = 엔캐리 청산",v:"미확인",s:"정합하나 직접 증거 없음"},
  {t:"삼성 파운드리 × 엔비디아 (Groq)",v:"미확인",s:"물량 5배 주장 검증 불가"},
  {t:"연말 7,383",v:"미확인",s:"12월까지 판정 불가"}];
 const CL={"확정":C.s2,"부분":C.s1,"기각":C.s4,"미확인":C.ink3};
 const W=880,T=68,RH=26,H=T+D.length*RH+18,s=svg(W,H);
 const CNT={}; D.forEach(d=>CNT[d.v]=(CNT[d.v]||0)+1);
 let ax=0;
 ["확정","부분","기각","미확인"].forEach(function(k){
  const w=(W)*CNT[k]/D.length;
  el(s,"rect",{x:ax,y:14,width:w-2,height:20,fill:CL[k],opacity:.82});
  tx(s,ax+8,28,k+" "+CNT[k],{fill:"#0B101C",fs:11,ff:SANS,fw:700});
  ax+=w;});
 tx(s,0,50,"누적 21건 — 문서1의 14건에 이번 회차 7건 추가",{fill:C.ink3,fs:10,ff:SANS});
 D.forEach(function(d,i){
  const y=T+i*RH;
  el(s,"line",{x1:0,x2:W,y1:y+9,y2:y+9,stroke:C.line,"stroke-width":1});
  el(s,"rect",{x:0,y:y-9,width:3,height:18,fill:CL[d.v]});
  tx(s,12,y+4,d.t,{fill:C.ink,fs:11,ff:SANS});
  el(s,"rect",{x:330,y:y-8,width:44,height:17,fill:"none",stroke:CL[d.v],"stroke-width":1.1,rx:2});
  tx(s,352,y+4,d.v,{ta:"middle",fill:CL[d.v],fs:9.5,ff:SANS,fw:700});
  tx(s,392,y+4,d.s,{fill:C.ink3,fs:10,ff:SANS});});
 mount("c-ledger",s);})();

/* ══ 07·2 자기수정 ══ */
(function(){
 const D=[{d:"문서3",t:"삼성전기 제외",w:"PER 68x — 내 규칙 위반"},
          {d:"문서3",t:"두산에너빌리티 제외",w:"PER 159x — 내 규칙 위반"},
          {d:"문서3",t:"디아이 코스피 확인",w:"내가 통째로 누락했다"},
          {d:"문서4",t:"유가→정책 경로 삭제",w:"모형 척추 수정"},
          {d:"문서4",t:"'인상 대비 없음' 경고 → 패",w:"경고만 하고 대비를 안 했다"}];
 const W=520,T=42,RH=42,H=T+D.length*RH+22,s=svg(W,H);
 tx(s,0,20,"내가 스스로 뒤집은 것들",{fill:C.ink3,fs:10,ff:SANS});
 D.forEach(function(d,i){
  const y=T+i*RH, nw=d.d==="문서4";
  el(s,"line",{x1:0,x2:W,y1:y-13,y2:y-13,stroke:C.line,"stroke-width":1});
  el(s,"rect",{x:0,y:y-13,width:3,height:RH,fill:nw?C.s4:C.s3,opacity:.8});
  el(s,"rect",{x:12,y:y-8,width:38,height:17,fill:"none",stroke:nw?C.s4:C.s3,"stroke-width":1.1,rx:2});
  tx(s,31,y+4,d.d,{ta:"middle",fill:nw?C.s4:C.s3,fs:9,ff:SANS,fw:700});
  tx(s,60,y+1,d.t,{fill:C.ink,fs:11,ff:SANS});
  tx(s,60,y+16,d.w,{fill:C.ink3,fs:9.5,ff:SANS});});
 mount("c-selfcorr",s);})();

/* ══ 07·3 오류 유형 ══ */
(function(){
 const D=[{n:"프레임 의존 (지표 선택이 결론을 결정)",v:5,c:C.s1},
          {n:"인과 오지정 (숫자는 맞고 원인이 틀림)",v:3,c:C.s4},
          {n:"출처 불일치 (합·기준이 안 맞음)",v:3,c:C.s3},
          {n:"표본 내 자기모순 (같은 방송이 서로 반박)",v:2,c:C.s5},
          {n:"검증 불가 경험칙 (표본 수 미제시)",v:2,c:C.ink3}];
 const W=520,L=254,R=54,T=62,RH=36,H=T+D.length*RH+38,s=svg(W,H);
 const pw=W-L-R;
 [0,2,4,6].forEach(function(v){
  el(s,"line",{x1:L+pw*v/6,x2:L+pw*v/6,y1:T-14,y2:T+D.length*RH-16,stroke:C.line,"stroke-width":1});
  tx(s,L+pw*v/6,T-20,v,{ta:"middle",fill:C.ink3,fs:9});});
 D.forEach(function(d,i){
  const y=T+i*RH;
  tx(s,L-10,y+4,d.n,{ta:"end",fill:C.ink2,fs:10,ff:SANS});
  el(s,"rect",{x:L,y:y-8,width:pw*d.v/6,height:17,fill:d.c,opacity:.82});
  tx(s,L+pw*d.v/6+8,y+4,d.v+"회",{fill:d.c,fs:10.5,fw:700});});
 tx(s,0,18,"기각 3 + 부분 6 + 미확인 3 = 12건에서 검출",{fill:C.ink3,fs:10,ff:SANS});
 tx(s,0,33,"한 건이 두 유형에 걸치면 양쪽에 계상 → 합 15",{fill:C.ink3,fs:9,ff:SANS});
 tx(s,0,H-20,"프레임 의존이 압도적 1위 — 어느 지표를 쓰느냐가 결론을 만든다.",{fill:C.ink,fs:10,ff:SANS});
 tx(s,0,H-5,"대응: 물가는 4개 지표를 항상 병기하고, 단일 지표로 정책을 논하는 주장은 자동으로 '부분'으로 강등한다.",{fill:C.ink3,fs:9,ff:SANS});
 mount("c-errtype",s);})();

/* ══ 08·1 캘린더 ══ */
(function(){
 const EV=[{m:9,d:17,n:"9월 FOMC",w:"동결 여부 · 월러 문턱 판정",c:C.s4,big:1},
           {m:9,d:26,n:"8월 코어 PCE",w:"2.8% 이하면 월러 승",c:C.s4,big:1},
           {m:10,d:8,n:"3Q 잠정실적",w:"삼성 HBM 점유율 확인",c:C.s5},
           {m:10,d:29,n:"10월 FOMC",w:"인상·인하 방향 확정",c:C.s4,big:1},
           {m:11,d:26,n:"12주 회복 도달점",w:"경험칙 검증일",c:C.s2},
           {m:12,d:10,n:"12월 FOMC",w:"연간 정책 마감",c:C.s4,big:1},
           {m:1,d:7,n:"18주 회복 도달점",w:"경험칙 상한",c:C.s2}];
 const W=880,L=64,R=64,T=190,H=372,s=svg(W,H);
 const pw=W-L-R;
 const t0=new Date(2026,8,1).getTime(), t1=new Date(2027,0,16).getTime();
 const X=(m,d)=>{const y=(m===1)?2027:2026;
   return L+pw*(new Date(y,m-1,d).getTime()-t0)/(t1-t0);};
 el(s,"line",{x1:L,x2:L+pw,y1:T,y2:T,stroke:C.line2,"stroke-width":1.4});
 [[9,"9월"],[10,"10월"],[11,"11월"],[12,"12월"],[1,"1월"]].forEach(function(m){
  const x=X(m[0],1);
  el(s,"line",{x1:x,x2:x,y1:T-5,y2:T+5,stroke:C.line2,"stroke-width":1});
  tx(s,x,T+22,m[1],{ta:"middle",fill:C.ink3,fs:10.5,ff:SANS});});
 // 위 4개 / 아래 3개로 분리, 각각 계단식 3단
 const UP=[0,2,4,6], DN=[1,3,5];
 UP.forEach(function(idx,k){
  const e=EV[idx], x=X(e.m,e.d), h=48+(k%3)*40;
  el(s,"line",{x1:x,x2:x,y1:T-2,y2:T-h,stroke:e.c,"stroke-width":1.2,"stroke-dasharray":"3 2"});
  el(s,"circle",{cx:x,cy:T,r:e.big?6:4.5,fill:e.big?e.c:C.surf,stroke:e.c,"stroke-width":2});
  el(s,"rect",{x:x-84,y:T-h-30,width:168,height:34,fill:C.surf2,stroke:e.c,"stroke-width":1.1});
  tx(s,x,T-h-16,e.n,{ta:"middle",fill:e.c,fs:11,ff:SANS,fw:e.big?700:500});
  tx(s,x,T-h-3,e.w,{ta:"middle",fill:C.ink3,fs:9,ff:SANS});
  tx(s,x,T-14,(e.m===1?"1/":e.m+"/")+e.d,{ta:"middle",fill:C.ink3,fs:9});});
 DN.forEach(function(idx,k){
  const e=EV[idx], x=X(e.m,e.d), h=46+(k%3)*40;
  el(s,"line",{x1:x,x2:x,y1:T+2,y2:T+h,stroke:e.c,"stroke-width":1.2,"stroke-dasharray":"3 2"});
  el(s,"circle",{cx:x,cy:T,r:e.big?6:4.5,fill:e.big?e.c:C.surf,stroke:e.c,"stroke-width":2});
  el(s,"rect",{x:x-84,y:T+h-4,width:168,height:34,fill:C.surf2,stroke:e.c,"stroke-width":1.1});
  tx(s,x,T+h+11,e.n,{ta:"middle",fill:e.c,fs:11,ff:SANS,fw:e.big?700:500});
  tx(s,x,T+h+24,e.w,{ta:"middle",fill:C.ink3,fs:9,ff:SANS});
  tx(s,x,T+38,(e.m===1?"1/":e.m+"/")+e.d,{ta:"middle",fill:C.ink3,fs:9});});
 tx(s,0,14,"큰 점 = 모형을 죽일 수 있는 날 (4회) · 작은 점 = 방향만 확인하는 날 (3회)",{fill:C.ink3,fs:10,ff:SANS});
 tx(s,0,H-6,"FOMC·PCE 일정은 통상 주기에서 복원한 추정일이다 (INF) — 실제 일정은 공식 발표로 확인할 것",{fill:C.s1,fs:9.5,ff:SANS});
 mount("c-cal",s);})();

/* ══ 08·2 반증 조건 ══ */
(function(){
 const F=[
  ["코어 PCE가 3.2% 이상으로 나온다","월러 문턱이 무너진다 → S3 확률 13% → 22%로 되돌린다","S3",C.s4],
  ["연준이 9월 또는 10월에 실제로 금리를 올린다","완화 전제가 전부 무효 → 모형 전면 재작성","전면",C.s4],
  ["브렌트가 110달러를 넘고 연준이 다시 에너지를 언급한다","절단이 취소된다 → v1 사슬 복원","척추",C.s4],
  ["코스피가 6,400 아래에서 이틀 이상 종가를 만든다","박스권 하단 방어 실패 → S3 레벨 6,100 → 5,800","레벨",C.s4],
  ["삼성전자 HBM 점유율이 다음 분기 30% 아래로 되돌아간다","삼성 비중 동률 근거 소멸 → SK 단독 우위 복귀","종목",C.s1],
  ["CXMT가 HBM3E 양산을 올해 안에 발표한다","2028년 전제가 깨진다 → 반도체 버킷 상한 하향","버킷",C.s1],
  ["기타법인 순매수가 3주 연속 순매도로 돌아선다","최종 매수자 소멸 → S3 바닥 상향 근거 철회","레벨",C.s1],
  ["코스피가 7,500을 넘고도 개인 순매수가 안 돌아온다","160조 매물벽 모형이 틀렸다 → S1 상단 재산정","상단",C.s3]];
 const box=document.getElementById("c-falsify");
 let h='<div class="scrollx"><table><thead><tr><th style="width:36%">조건 (관측 가능)</th><th style="width:44%">참이면 무엇이 바뀌는가</th><th>영향</th></tr></thead><tbody>';
 F.forEach(function(f){
  h+='<tr><td style="color:'+C.ink+'">'+f[0]+'</td><td style="color:'+C.ink2+'">'+f[1]+
     '</td><td><span class="chip" style="border-color:'+f[3]+';color:'+f[3]+'">'+f[2]+'</span></td></tr>';});
 h+='</tbody></table></div>';
 box.innerHTML=h;})();
