import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Battle City", page_icon="🛡️", layout="wide")

st.markdown(
    """
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .block-container {padding: 0.5rem 1rem 0 1rem; max-width: 100%;}
    </style>
    """,
    unsafe_allow_html=True,
)

GAME = r'''<!DOCTYPE html>
<html lang="uz">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no">
<title>Battle City – 5 o'yinchi</title>
<style>
*{box-sizing:border-box}
body{margin:0;background:#151515;color:#eee;font-family:system-ui,sans-serif;display:flex;flex-direction:column;align-items:center;min-height:100vh;padding:10px;-webkit-user-select:none;user-select:none}
h1{margin:8px 0;font-size:22px;letter-spacing:2px;color:#f5d400}
.box{background:#222;border:2px solid #444;border-radius:10px;padding:18px;max-width:380px;width:100%;text-align:center}
button,input{font:inherit;padding:10px 14px;border-radius:8px;border:2px solid #555;background:#2d2d2d;color:#eee;margin:4px;touch-action:manipulation}
button{cursor:pointer;background:#f5d400;color:#111;border-color:#f5d400;font-weight:700}
button:disabled{opacity:.4}
input{width:110px;text-align:center;text-transform:uppercase;letter-spacing:3px}
#code{font-size:34px;letter-spacing:6px;color:#f5d400;font-weight:700}
#game{display:none;flex-direction:column;align-items:center}
canvas{background:#000;image-rendering:pixelated;width:min(96vw,calc(100vh - 130px));height:auto;aspect-ratio:1;border:3px solid #444}
#hud{display:flex;flex-wrap:wrap;gap:6px 14px;justify-content:center;font-size:14px;margin:6px 0;max-width:96vw}
.dot{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:4px}
#pad{display:none;position:fixed;bottom:8px;left:0;right:0;justify-content:space-between;padding:0 14px;pointer-events:none}
#pad>div{pointer-events:auto}
#pad button{width:56px;height:56px;font-size:22px;margin:3px;padding:0;opacity:.75}
@media (pointer:coarse){#pad{display:flex}canvas{width:min(96vw,calc(100vh - 290px))}}
small{color:#999}
</style>
</head>
<body>
<h1>BATTLE CITY</h1>

<div id="menu" class="box">
  <p>5 tagacha o'yinchi birga dushman tanklarga qarshi va shtabni himoya qiladi.</p>
  <button id="mk">Xona yaratish</button>
  <hr style="border-color:#444;margin:14px 0">
  <input id="in" maxlength="4" placeholder="KOD">
  <button id="jn">Qo'shilish</button>
  <p id="msg" style="color:#ff8c8c;min-height:20px"></p>
  <small>Boshqaruv: strelkalar yoki WASD, o'q uzish — Space yoki J</small>
</div>

<div id="lobby" class="box" style="display:none">
  <div>Xona kodi:</div>
  <div id="code">----</div>
  <p>Do'stlarga shu kodni yuboring</p>
  <p id="cnt">O'yinchilar: 1/5</p>
  <button id="start">O'yinni boshlash</button>
  <p id="wait" style="display:none">Host o'yinni boshlashini kuting...</p>
</div>

<div id="game">
  <div id="hud"></div>
  <canvas id="c"></canvas>
  <button id="again" style="display:none">Qayta boshlash</button>
</div>

<div id="pad">
  <div><button data-k="l">◀</button><button data-k="u">▲</button><button data-k="d">▼</button><button data-k="r">▶</button></div>
  <div><button data-k="f" style="width:84px;height:84px;background:#e44;border-color:#e44;color:#fff">🔥</button></div>
</div>

<script src="https://unpkg.com/peerjs@1.5.4/dist/peerjs.min.js"></script>
<script>
const T=16,N=26,W=N*T,DX=[0,1,0,-1],DY=[-1,0,1,0];
const COL=['#f5d400','#4fd16a','#4aa3ff','#ff8c3a','#d86bff'];
const SP=[0,64,128,256,320];
const $=id=>document.getElementById(id);
const cv=$('c'),ctx=cv.getContext('2d');cv.width=cv.height=W;
let S=null,R=null,grid=null,peer=null,conn=null,conns={},me=-1,isHost=false,CODE='',fc=0,looping=false;

function show(id){['menu','lobby'].forEach(s=>$(s).style.display=s===id?'':'none');$('game').style.display=id==='game'?'flex':'none'}

/* ---------- MAP ---------- */
function mkMap(){
  const g=new Array(N*N).fill(0);
  const f=(x,y,w,h,v)=>{for(let j=y;j<y+h;j++)for(let i=x;i<x+w;i++)if(i>=0&&j>=0&&i<N&&j<N)g[j*N+i]=v};
  for(let y=3;y<=15;y+=4)for(let x=2;x<=22;x+=4){const k=(x/4|0)+(y>>2);f(x,y,2,2,k%4===0?2:1)}
  f(8,19,2,2,3);f(16,19,2,2,3);f(0,9,2,4,4);f(24,9,2,4,4);
  f(11,23,4,1,1);f(11,24,1,2,1);f(14,24,1,2,1);f(12,24,2,2,5);
  return g;
}

/* ---------- HOST LOGIC ---------- */
function addPlayer(slot){
  S.p[slot]={slot,x:SP[slot],y:384,d:0,alive:true,lives:3,score:0,m:-1,f:false,cd:0,inv:150,rt:0};
  if(S.run)S.left+=5;
}
function newGame(){
  S.g=mkMap();S.gv++;S.e=[];S.b=[];S.sp=60;S.st='play';S.run=true;
  const ps=Object.values(S.p);S.left=10+6*ps.length;
  for(const p of ps)Object.assign(p,{x:SP[p.slot],y:384,d:0,alive:true,lives:3,score:0,cd:0,inv:150});
}
function blocked(x,y,self){
  if(x<0||y<0||x+32>W||y+32>W)return true;
  for(let ty=y/T|0;ty<=(y+31.9)/T|0;ty++)for(let tx=x/T|0;tx<=(x+31.9)/T|0;tx++){
    const v=S.g[ty*N+tx];if(v===1||v===2||v===3||v===5)return true}
  for(const o of S.e.concat(Object.values(S.p).filter(p=>p.alive)))
    if(o!==self&&Math.abs(o.x-x)<32&&Math.abs(o.y-y)<32)return true;
  return false;
}
function step(t,sp){
  const nx=t.x+DX[t.d]*sp,ny=t.y+DY[t.d]*sp;
  if(!blocked(nx,ny,t)){t.x=nx;t.y=ny;return true}return false;
}
function turn(t,d){
  if(d===t.d)return;
  if(d%2!==t.d%2){
    const sx=d%2===0?Math.round(t.x/32)*32:t.x,sy=d%2===1?Math.round(t.y/32)*32:t.y;
    if(!blocked(sx,sy,t)){t.x=sx;t.y=sy}
  }
  t.d=d;
}
function shoot(t,o){S.b.push({x:t.x+16+DX[t.d]*16,y:t.y+16+DY[t.d]*16,d:t.d,o})}

function tick(){
  if(S.st!=='play')return;
  const ps=Object.values(S.p);
  for(const p of ps){
    if(!p.alive){if(p.lives>0&&--p.rt<=0){p.alive=true;p.x=SP[p.slot];p.y=384;p.d=0;p.inv=150}continue}
    if(p.inv>0)p.inv--;if(p.cd>0)p.cd--;
    if(p.m>=0){turn(p,p.m);step(p,1.6)}
    if(p.f&&p.cd<=0&&!S.b.some(b=>b.o===p.slot)){shoot(p,p.slot);p.cd=15}
  }
  if(--S.sp<=0){
    S.sp=150;
    if(S.left>0&&S.e.length<4+ps.length){
      const sx=[0,192,384][Math.random()*3|0];
      if(!blocked(sx,0,null)){S.e.push({x:sx,y:0,d:2,cd:60});S.left--}
    }
  }
  for(const e of S.e){
    if(e.cd>0)e.cd--;
    if(Math.random()<0.012||!step(e,0.9)){turn(e,Math.random()<0.45?2:Math.random()*4|0)}
    if(e.cd<=0&&Math.random()<0.03){shoot(e,'e');e.cd=50}
  }
  for(let i=S.b.length-1;i>=0;i--){
    const b=S.b[i];let dead=false;
    for(let s=0;s<2&&!dead;s++){
      b.x+=DX[b.d]*2;b.y+=DY[b.d]*2;
      if(b.x<0||b.y<0||b.x>=W||b.y>=W){dead=true;break}
      for(const k of [-5,0,5]){
        const tx=(b.x+(b.d%2?0:k))/T|0,ty=(b.y+(b.d%2?k:0))/T|0;
        if(tx<0||ty<0||tx>=N||ty>=N)continue;
        const v=S.g[ty*N+tx];
        if(v===1){S.g[ty*N+tx]=0;S.gv++;dead=true}
        else if(v===2)dead=true;
        else if(v===5){for(let q=0;q<S.g.length;q++)if(S.g[q]===5)S.g[q]=6;S.gv++;S.st='lose';dead=true}
      }
      if(dead)break;
      if(b.o==='e'){
        for(const p of ps)if(p.alive&&p.inv<=0&&Math.abs(b.x-p.x-16)<16&&Math.abs(b.y-p.y-16)<16){p.alive=false;p.lives--;p.rt=90;dead=true;break}
      }else{
        for(let j=0;j<S.e.length;j++){const e=S.e[j];
          if(Math.abs(b.x-e.x-16)<16&&Math.abs(b.y-e.y-16)<16){S.e.splice(j,1);if(S.p[b.o])S.p[b.o].score+=100;dead=true;break}}
      }
    }
    if(dead)S.b.splice(i,1);
  }
  if(S.st==='play'){
    if(S.left===0&&S.e.length===0)S.st='win';
    else if(ps.every(p=>!p.alive&&p.lives<=0))S.st='lose';
  }
}
function snap(){
  return{p:Object.values(S.p).map(p=>[p.slot,Math.round(p.x),Math.round(p.y),p.d,p.alive?1:0,p.lives,p.score,p.inv>0?1:0]),
    e:S.e.map(e=>[Math.round(e.x),Math.round(e.y),e.d]),b:S.b.map(b=>[b.x,b.y]),st:S.st,l:S.left+S.e.length};
}
let lastGv=-1;
function broadcast(){
  const m={t:'s',s:Object.assign({},R)};
  if(S.gv!==lastGv||fc%60===0){m.s.g=S.g.join('');lastGv=S.gv}
  for(const k in conns)if(conns[k].open)conns[k].send(m);
}
function loop(){
  if(looping)return;looping=true;
  setInterval(()=>{
    tick();
    if(++fc%3===0&&S.run){R=snap();grid=S.g;render();broadcast()}
  },1000/60);
}

/* ---------- NETWORK ---------- */
function lobbyUpdate(){
  const n=Object.keys(S.p).length;
  $('cnt').textContent="O'yinchilar: "+n+"/5";
  for(const k in conns)if(conns[k].open)conns[k].send({t:'lobby',n});
}
function createRoom(){
  isHost=true;me=0;
  S={p:{},g:mkMap(),gv:1,e:[],b:[],left:0,sp:0,st:'lobby',run:false};
  CODE=Array.from({length:4},()=>'ABCDEFGHJKMNPQRSTUVWXYZ23456789'[Math.random()*31|0]).join('');
  peer=new Peer('bcity26-'+CODE);
  peer.on('error',e=>{
    if(e.type==='unavailable-id'){peer.destroy();createRoom()}
    else $('msg').textContent='Xato: '+e.type;
  });
  peer.on('open',()=>{
    addPlayer(0);$('code').textContent=CODE;$('wait').style.display='none';$('start').style.display='';
    show('lobby');lobbyUpdate();
  });
  peer.on('connection',c=>{
    c.on('open',()=>{
      const slot=[1,2,3,4].find(s=>!S.p[s]);
      if(slot===undefined){c.send({t:'full'});setTimeout(()=>c.close(),300);return}
      conns[slot]=c;addPlayer(slot);c.send({t:'hello',slot});lastGv=-1;lobbyUpdate();
      c.on('data',m=>{if(m.t==='in'&&S.p[slot]){S.p[slot].m=m.m;S.p[slot].f=!!m.f}});
      c.on('close',()=>{delete conns[slot];delete S.p[slot];lobbyUpdate()});
    });
  });
}
function joinRoom(code){
  isHost=false;peer=new Peer();
  peer.on('error',e=>$('msg').textContent=e.type==='peer-unavailable'?"Bunday xona topilmadi":'Xato: '+e.type);
  peer.on('open',()=>{
    conn=peer.connect('bcity26-'+code,{reliable:true});
    conn.on('data',m=>{
      if(m.t==='hello'){me=m.slot;$('code').textContent=code;$('start').style.display='none';$('wait').style.display='';show('lobby')}
      else if(m.t==='lobby')$('cnt').textContent="O'yinchilar: "+m.n+"/5";
      else if(m.t==='full'){show('menu');$('msg').textContent="Xona to'lgan (5/5)"}
      else if(m.t==='s'){
        R=m.s;if(R.g)grid=R.g.split('').map(Number);
        if($('game').style.display==='none')show('game');
        render();
      }
    });
    conn.on('close',()=>{document.body.innerHTML='<h2 style="color:#ff8c8c">Host bilan aloqa uzildi. Sahifani yangilang (F5).</h2>'});
  });
}
$('mk').onclick=()=>{$('msg').textContent='';createRoom()};
$('jn').onclick=()=>{const c=$('in').value.trim().toUpperCase();if(c.length!==4){$('msg').textContent='4 belgili kodni kiriting';return}$('msg').textContent='';joinRoom(c)};
$('start').onclick=()=>{newGame();loop();show('game')};
$('again').onclick=()=>{newGame()};

/* ---------- INPUT ---------- */
const stack=[],IDX={u:0,r:1,d:2,l:3};let fire=false;
const KM={ArrowUp:'u',w:'u',W:'u',ArrowDown:'d',s:'d',S:'d',ArrowLeft:'l',a:'l',A:'l',ArrowRight:'r',d:'r',D:'r',' ':'f',j:'f',J:'f'};
function press(k,on){
  if(k==='f')fire=on;
  else{const i=stack.indexOf(k);if(i>=0)stack.splice(i,1);if(on)stack.push(k)}
  const m=stack.length?IDX[stack[stack.length-1]]:-1;
  if(isHost){if(S&&S.p[0]){S.p[0].m=m;S.p[0].f=fire}}
  else if(conn&&conn.open)conn.send({t:'in',m,f:fire});
}
addEventListener('keydown',e=>{if(e.target.tagName==='INPUT')return;const k=KM[e.key];if(k){e.preventDefault();if(!e.repeat)press(k,true)}});
addEventListener('keyup',e=>{const k=KM[e.key];if(k)press(k,false)});
document.querySelectorAll('#pad button').forEach(b=>{
  const k=b.dataset.k;
  b.addEventListener('pointerdown',e=>{e.preventDefault();press(k,true)});
  ['pointerup','pointercancel','pointerleave'].forEach(ev=>b.addEventListener(ev,()=>press(k,false)));
});

/* ---------- RENDER ---------- */
function tank(x,y,d,col,inv){
  ctx.save();ctx.translate(x+16,y+16);ctx.rotate(d*Math.PI/2);
  ctx.fillStyle='#333';ctx.fillRect(-14,-14,6,28);ctx.fillRect(8,-14,6,28);
  ctx.fillStyle=col;ctx.fillRect(-8,-11,16,22);
  ctx.fillStyle='rgba(255,255,255,.35)';ctx.beginPath();ctx.arc(0,0,5,0,7);ctx.fill();
  ctx.fillStyle=col;ctx.fillRect(-2,-17,4,13);
  if(inv){ctx.strokeStyle='#fff';ctx.lineWidth=2;ctx.beginPath();ctx.arc(0,0,19,0,7);ctx.stroke()}
  ctx.restore();
}
function render(){
  if(!grid||!R)return;
  ctx.fillStyle='#000';ctx.fillRect(0,0,W,W);
  for(let i=0;i<grid.length;i++){
    const v=grid[i];if(!v)continue;
    const x=i%N*T,y=(i/N|0)*T;
    if(v===1){ctx.fillStyle='#b5502d';ctx.fillRect(x,y,T,T);ctx.fillStyle='#e0a080';ctx.fillRect(x,y+7,T,1);ctx.fillRect(x+7,y,1,7);ctx.fillRect(x+3,y+8,1,8)}
    else if(v===2){ctx.fillStyle='#9aa4ad';ctx.fillRect(x,y,T,T);ctx.fillStyle='#e8eef2';ctx.fillRect(x+2,y+2,T-4,T-4);ctx.fillStyle='#9aa4ad';ctx.fillRect(x+5,y+5,6,6)}
    else if(v===3){ctx.fillStyle='#1f4fd0';ctx.fillRect(x,y,T,T);ctx.fillStyle='#6fa0ff';ctx.fillRect(x+2,y+4,6,2);ctx.fillRect(x+8,y+10,6,2)}
    else if(v===5&&i===24*N+12){ctx.fillStyle='#555';ctx.fillRect(x,y,32,32);ctx.fillStyle='#f5d400';ctx.font='26px sans-serif';ctx.textAlign='center';ctx.fillText('★',x+16,y+26)}
    else if(v===6){ctx.fillStyle='#331';ctx.fillRect(x,y,T,T)}
  }
  for(const e of R.e)tank(e[0],e[1],e[2],'#c9c9c9');
  for(const p of R.p)if(p[4])tank(p[1],p[2],p[3],COL[p[0]],p[7]&&(fc&2||true));
  ctx.fillStyle='#fff';for(const b of R.b)ctx.fillRect(b[0]-2,b[1]-2,4,4);
  for(let i=0;i<grid.length;i++)if(grid[i]===4){ctx.fillStyle='#1f7a2f';ctx.fillRect(i%N*T,(i/N|0)*T,T,T);ctx.fillStyle='#2fb046';ctx.fillRect(i%N*T+3,(i/N|0)*T+3,4,4);ctx.fillRect(i%N*T+9,(i/N|0)*T+9,4,4)}
  if(R.st!=='play'){
    ctx.fillStyle='rgba(0,0,0,.65)';ctx.fillRect(0,W/2-40,W,80);
    ctx.fillStyle=R.st==='win'?'#4fd16a':'#ff5555';ctx.font='bold 34px sans-serif';ctx.textAlign='center';
    ctx.fillText(R.st==='win'?"G'ALABA!":"O'YIN TUGADI",W/2,W/2+12);
  }
  $('again').style.display=isHost&&R.st!=='play'?'':'none';
  $('hud').innerHTML=R.p.slice().sort((a,b)=>a[0]-b[0]).map(p=>
    `<span><span class="dot" style="background:${COL[p[0]]}"></span>${p[0]+1}${p[0]===me?' (siz)':''}: ❤${p[5]} ★${p[6]}</span>`).join('')+`<span>Dushman: ${R.l}</span>`;
}
</script>
</body>
</html>
'''

components.html(GAME, height=860, scrolling=False)
st.caption("Boshqaruv: strelkalar / WASD, o'q uzish: Space yoki J. Avval o'yin oynasini bir marta bosing.")
