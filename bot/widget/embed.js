/* ΒΛΑΞ — ο ξεναγός. Παράγεται από widget/index.html (bot/build_embed.py). Μην το επεξεργάζεσαι με το χέρι. */
(function () {
  if (window.__vlaxGuideLoaded) return;
  window.__vlaxGuideLoaded = true;

  var FONTS = ["https://fonts.googleapis.com/css2?family=Anton&family=Commissioner:wght@400;700;800&family=GFS+Didot&family=Literata:ital,opsz,wght@0,7..72,400;1,7..72,400&display=swap"];
  FONTS.forEach(function (href) {
    if (document.querySelector('link[href="' + href + '"]')) return;
    var l = document.createElement('link'); l.rel = 'stylesheet'; l.href = href; document.head.appendChild(l);
  });

  var style = document.createElement('style');
  style.textContent = "\n  :root{\n    --mavro:#0a0605; --kokkino:#f3101e; --xryso:#d9a92f; --xryso-glitter:#f2c94c;\n    --charti:#f4ecdd; --gri:#615d5c; --mov:#8e3fa8;\n    --flyer:\"Commissioner\",system-ui,sans-serif; --book:\"GFS Didot\",Georgia,serif; --display:\"Anton\",Impact,sans-serif;\n  }\n  *{box-sizing:border-box}\n  body{margin:0;background:var(--mavro);color:var(--charti);font-family:var(--flyer);min-height:100vh}\n  .demo{max-width:820px;margin:0 auto;padding:56px 20px}\n  .demo h1{font-family:var(--display);font-size:clamp(3rem,12vw,6rem);letter-spacing:.02em;margin:0;color:var(--charti)}\n  .demo p{font-family:var(--book);font-size:1.05rem;color:#cdc3b2;max-width:38rem}\n  .demo .red{color:var(--kokkino)}\n\n  #vx-launcher{position:fixed;right:22px;bottom:22px;width:74px;height:74px;border-radius:50%;border:2px solid var(--xryso);cursor:pointer;\n    background:#1a1210 center/cover no-repeat;box-shadow:0 10px 30px rgba(0,0,0,.55);transition:transform .15s}\n  #vx-launcher:hover{transform:scale(1.06);border-color:var(--xryso-glitter)}\n  #vx-launcher .tag{position:absolute;left:50%;transform:translateX(-50%);bottom:-9px;background:var(--kokkino);color:#fff;\n    font-size:10px;font-weight:800;letter-spacing:.08em;padding:2px 7px;border-radius:2px;white-space:nowrap}\n\n  #vx{position:fixed;right:22px;bottom:110px;width:min(420px,calc(100vw - 28px));height:min(660px,calc(100vh - 140px));\n    background:#120c0a;border:1px solid #34281f;border-radius:4px;box-shadow:0 18px 50px rgba(0,0,0,.6);display:none;flex-direction:column;overflow:hidden}\n  #vx.open{display:flex}\n  .vx-head{display:flex;align-items:center;gap:10px;padding:10px 12px;border-bottom:1px solid #34281f;background:linear-gradient(180deg,#1a1210,#120c0a)}\n  .vx-av{width:52px;height:52px;border-radius:50%;flex:none;position:relative;overflow:hidden;background:#241a16;border:1px solid var(--xryso)}\n  .vx-av img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:0;transition:opacity .2s}\n  .vx-av img.show{opacity:1}\n  .vx-av.think{animation:pulse 1.2s ease-in-out infinite}\n  @keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.05)}}\n  .vx-who b{display:block;font-family:var(--display);font-size:16px;letter-spacing:.04em;color:var(--charti)}\n  .vx-who span{font-family:var(--book);font-size:12px;color:var(--xryso)}\n  .vx-actions{margin-left:auto;display:flex;gap:6px;align-items:center}\n  .vx-mini{width:30px;height:30px;border-radius:50%;border:1px solid #3d2f24;background:#241a16 center/cover no-repeat;cursor:pointer;opacity:.55;padding:0}\n  .vx-mini.on{opacity:1;border-color:var(--kokkino)}\n  .vx-x{border:0;background:transparent;color:var(--gri);font-size:20px;cursor:pointer;line-height:1}\n\n  .vx-body{flex:1;overflow-y:auto;padding:14px;display:flex;flex-direction:column;gap:12px}\n  .msg{max-width:88%;font-size:14.5px;line-height:1.45;white-space:pre-wrap}\n  .msg.bot{align-self:flex-start;background:#1c1411;border-left:2px solid var(--kokkino);padding:10px 12px}\n  .msg.user{align-self:flex-end;background:var(--charti);color:#17110d;padding:9px 12px;border-radius:2px}\n  .fn{align-self:flex-start;max-width:88%;font-family:var(--book);font-size:12.5px;line-height:1.5;color:#b3a795;padding-left:14px;position:relative}\n  .fn:before{content:attr(data-n);position:absolute;left:0;top:0;color:var(--kokkino);font-family:var(--flyer);font-size:11px;font-weight:800}\n  .typing{display:inline-flex;gap:5px}.typing i{width:5px;height:5px;background:var(--xryso);border-radius:50%;animation:bl 1.1s infinite}\n  .typing i:nth-child(2){animation-delay:.18s}.typing i:nth-child(3){animation-delay:.36s}\n  @keyframes bl{0%,80%,100%{opacity:.25}40%{opacity:1}}\n\n  .cards{display:flex;flex-direction:column;gap:8px;align-self:stretch}\n  .card{display:flex;gap:10px;text-decoration:none;color:inherit;background:#1a1210;border:1px solid #34281f;padding:8px;transition:border-color .15s}\n  .card:hover{border-color:var(--xryso)}\n  .card .im{width:58px;height:78px;flex:none;background:#241a16 center/cover no-repeat}\n  .card .meta{min-width:0}\n  .card time{display:block;font-family:var(--book);font-size:11.5px;color:var(--xryso)}\n  .card h4{margin:2px 0 3px;font-size:13.5px;font-weight:700;line-height:1.25}\n  .card .v{font-size:11.5px;color:#a2978a}\n  .card .badge{display:inline-block;background:var(--kokkino);color:#fff;font-size:10px;font-weight:800;padding:1px 5px;margin-right:5px}\n  .card .canc{color:var(--kokkino);font-size:11px;font-weight:700}\n  .pagelink{align-self:flex-start;font-family:var(--display);font-size:13px;letter-spacing:.06em;color:var(--mavro);background:var(--xryso);padding:7px 12px;text-decoration:none}\n  .pagelink:hover{background:var(--xryso-glitter)}\n  .chips{display:flex;flex-wrap:wrap;gap:6px;align-self:flex-start}\n  .chip{background:transparent;border:1px solid #4a3a2c;color:var(--charti);font-family:var(--flyer);font-size:12.5px;padding:6px 10px;cursor:pointer}\n  .chip:hover{border-color:var(--xryso);color:var(--xryso-glitter)}\n  .handoff{align-self:flex-start;font-family:var(--book);font-size:12.5px;color:#cdc3b2;border:1px dashed var(--kokkino);padding:8px 10px}\n  .handoff a{color:var(--xryso)}\n\n  .picker{align-self:stretch;display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:4px}\n  .pick{background:#1a1210;border:1px solid #34281f;padding:10px 6px;cursor:pointer;text-align:center;color:var(--charti)}\n  .pick:hover{border-color:var(--xryso)}\n  .pick .pim{width:64px;height:64px;margin:0 auto 6px;border-radius:50%;background:#241a16 center/cover no-repeat;border:1px solid #4a3a2c}\n  .pick b{display:block;font-family:var(--display);font-size:13px;letter-spacing:.03em}\n  .pick span{font-family:var(--book);font-size:11px;color:var(--xryso)}\n\n  .vx-foot{display:flex;gap:8px;padding:10px;border-top:1px solid #34281f;background:#1a1210}\n  .vx-foot input{flex:1;background:#0e0a08;border:1px solid #3d2f24;color:var(--charti);padding:10px;font-family:var(--flyer);font-size:14px;outline:none}\n  .vx-foot input:focus{border-color:var(--xryso)}\n  .vx-foot button{border:0;background:var(--kokkino);color:#fff;padding:0 14px;font-weight:800;cursor:pointer}\n  .vx-foot button:disabled{opacity:.45;cursor:default}\n  .vx-lang{border:0;background:transparent;color:var(--gri);font-size:11px;cursor:pointer}\n";
  document.head.appendChild(style);

  var host = document.createElement('div');
  host.id = 'vlax-guide-root';
  host.innerHTML = "<button id=\"vx-launcher\" aria-label=\"\u03a1\u03ce\u03c4\u03b1 \u03c4\u03bf\u03bd \u03be\u03b5\u03bd\u03b1\u03b3\u03cc\"><span class=\"tag\">\u03a1\u03a9\u03a4\u0391</span></button><section id=\"vx\" aria-label=\"\u039e\u03b5\u03bd\u03b1\u03b3\u03cc\u03c2\">\n  <div class=\"vx-head\">\n    <div class=\"vx-av\" id=\"vx-av\">\n      <img data-state=\"idle\" alt=\"\"><img data-state=\"thinking\" alt=\"\"><img data-state=\"talking\" alt=\"\"><img data-state=\"wave\" alt=\"\"><img data-state=\"sorry\" alt=\"\">\n    </div>\n    <div class=\"vx-who\"><b id=\"vx-name\">\u039e\u0395\u039d\u0391\u0393\u039f\u03a3</b><span id=\"vx-tag\">\u03b4\u03b9\u03ac\u03bb\u03b5\u03be\u03b5 \u03c0\u03bf\u03b9\u03bf\u03bd \u03b8\u03b5\u03c2</span></div>\n    <div class=\"vx-actions\" id=\"vx-minis\"></div>\n    <button class=\"vx-lang\" id=\"vx-lang\">EN</button>\n    <button class=\"vx-x\" id=\"vx-close\" aria-label=\"\u039a\u03bb\u03b5\u03af\u03c3\u03b9\u03bc\u03bf\">\u00d7</button>\n  </div>\n  <div class=\"vx-body\" id=\"vx-body\"></div>\n  <form class=\"vx-foot\" id=\"vx-form\">\n    <input id=\"vx-input\" autocomplete=\"off\" placeholder=\"\u03a1\u03ce\u03c4\u03b1 \u03ba\u03ac\u03c4\u03b9\u2026\">\n    <button id=\"vx-send\" type=\"submit\">\u27a4</button>\n  </form>\n</section>";
  document.body.appendChild(host);

  (function () {
  const API=(window.VLAX_API||''), AV=(window.VLAX_AVATARS||'/avatar');
  const $=s=>document.querySelector(s);
  const panel=$('#vx'), launcher=$('#vx-launcher'), body=$('#vx-body'), input=$('#vx-input'), send=$('#vx-send'), avEl=$('#vx-av');
  let lang=(navigator.language||'').startsWith('el')?'el':'en', personas=[], persona=localStorage.getItem('vlax_persona')||null, busy=false, opened=false, fnCount=0;
  let sid=localStorage.getItem('vlax_sid')||(Math.random().toString(36).slice(2)+Date.now().toString(36));
  localStorage.setItem('vlax_sid',sid);

  const T={el:{pick:'Διάλεξε ξεναγό',think:'…',see:'Δες τη σελίδα →',canc:'ΜΑΤΑΙΩΘΗΚΕ',hand:'Για αυτό θέλει άνθρωπο:',gaps:'Κενά',book:'Κρατήσεις',err:'Κάτι έσπασε. Ξαναρώτα.'},
           en:{pick:'Choose a guide',think:'…',see:'Open the page →',canc:'CANCELLED',hand:'This one needs a human:',gaps:'Gaps',book:'Bookings',err:'Something broke. Ask again.'}};
  const ph={el:'Ρώτα κάτι…',en:'Ask something…'};

  const SIL=id=>'data:image/svg+xml;utf8,'+encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128"><rect width="128" height="128" fill="#241a16"/><text x="64" y="82" font-size="52" font-family="serif" font-weight="bold" fill="#d9a92f" text-anchor="middle">${id[0].toUpperCase()}</text></svg>`);
  const avatarURL=(id,state)=>`${AV}/${id}_${state}_128.png`;

  const imgs={}; avEl.querySelectorAll('img').forEach(im=>imgs[im.dataset.state]=im);
  function loadAvatar(id){
    Object.entries(imgs).forEach(([st,im])=>{ im.dataset.f=''; im.onerror=()=>{ if(im.dataset.f==='2')return; if(st!=='idle'&&im.dataset.f!=='1'){im.dataset.f='1';im.src=avatarURL(id,'idle');} else {im.dataset.f='2';im.src=SIL(id);} }; im.src=avatarURL(id,st); });
    launcher.style.backgroundImage=`url(${avatarURL(id,'idle')}), url("${SIL(id)}")`;
  }
  let tmr=null;
  function setState(s){ Object.values(imgs).forEach(i=>i.classList.remove('show')); (imgs[s]||imgs.idle).classList.add('show');
    avEl.classList.toggle('think',s==='thinking'); clearTimeout(tmr);
    if(['talking','wave','sorry'].includes(s)) tmr=setTimeout(()=>setState('idle'), s==='talking'?2600:1800); }

  const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const add=el=>{ body.appendChild(el); body.scrollTop=body.scrollHeight; return el; };
  const bubble=(t,w)=>{const d=document.createElement('div');d.className='msg '+w;d.innerHTML=esc(t);return add(d);};
  function footnote(t){ if(!t)return; fnCount++; const d=document.createElement('div'); d.className='fn'; d.dataset.n='['+fnCount+']'; d.textContent=t; add(d); }
  function typing(){const d=document.createElement('div');d.className='msg bot';d.innerHTML='<span class="typing"><i></i><i></i><i></i></span>';return add(d);}
  function chips(list){ if(!list||!list.length)return; const w=document.createElement('div'); w.className='chips';
    list.forEach(q=>{const b=document.createElement('button');b.className='chip';b.textContent=q;b.onclick=()=>{w.remove();ask(q);};w.appendChild(b);}); add(w); }
  function cards(evs,l){ if(!evs||!evs.length)return; const g=document.createElement('div'); g.className='cards';
    evs.forEach(e=>{const a=document.createElement('a');a.className='card';a.href=e.url;a.target='_blank';a.rel='noopener';
      a.innerHTML=`<div class="im" style="background-image:url('${e.image||''}')"></div><div class="meta">
        <time>${esc(e.date||'')}</time><h4>${e.badge?`<span class="badge">${esc(e.badge)}</span>`:''}${esc(e.title)}</h4>
        <div class="v">${esc(e.venue||'')}</div>${e.cancelled?`<div class="canc">${T[l].canc}</div>`:''}</div>`;
      g.appendChild(a);}); add(g); }
  function pagelink(p,l){ if(!p)return; const a=document.createElement('a'); a.className='pagelink'; a.href=p.url; a.target='_blank'; a.rel='noopener';
    a.textContent=(p.title||'')+' '+T[l].see.slice(-1); a.title=T[l].see; add(a); }
  function handoff(c,l){ const d=document.createElement('div'); d.className='handoff';
    d.innerHTML=`${T[l].hand} <a href="${c.booking_url}" target="_blank" rel="noopener">${T[l].book}</a> · <a href="${c.gaps_url}" target="_blank" rel="noopener">${T[l].gaps}</a>`; add(d); }

  function showPicker(){
    const d=document.createElement('div'); d.className='msg bot'; d.textContent=T[lang].pick; add(d);
    const g=document.createElement('div'); g.className='picker';
    personas.forEach(p=>{const b=document.createElement('button');b.className='pick';
      b.innerHTML=`<div class="pim" style="background-image:url('${avatarURL(p.id,'idle')}'),url('${SIL(p.id)}')"></div><b>${esc(lang==='el'?p.name:p.name_en)}</b><span>${esc(lang==='el'?p.tagline:p.tagline_en)}</span>`;
      b.onclick=()=>{ g.remove(); d.remove(); choose(p.id,true); }; g.appendChild(b);}); add(g);
  }
  function minis(){ const w=$('#vx-minis'); w.innerHTML='';
    personas.forEach(p=>{const b=document.createElement('button');b.className='vx-mini'+(p.id===persona?' on':'');
      b.style.backgroundImage=`url(${avatarURL(p.id,'idle')}), url("${SIL(p.id)}")`; b.title=lang==='el'?`${p.name} — ${p.tagline}`:`${p.name_en} — ${p.tagline_en}`;
      b.onclick=()=>{ if(p.id!==persona) choose(p.id,true); }; w.appendChild(b);}); }
  function choose(id,greet){
    persona=id; localStorage.setItem('vlax_persona',id);
    const p=personas.find(x=>x.id===id)||{};
    $('#vx-name').textContent=(lang==='el'?p.name:p.name_en)||'ΞΕΝΑΓΟΣ';
    $('#vx-tag').textContent=(lang==='el'?p.tagline:p.tagline_en)||'';
    loadAvatar(id); minis(); setState('wave');
    if(greet){ bubble(lang==='el'?p.hello_el:p.hello_en,'bot'); chips(lang==='el'?p.chips_el:p.chips_en); }
  }

  async function ask(text){
    if(busy||!text.trim())return; if(!persona){showPicker();return;}
    busy=true;send.disabled=true; bubble(text,'user'); input.value='';
    setState('thinking'); const t=typing();
    const slow=setTimeout(()=>{ if(t.isConnected) t.title=lang==='el'?'ξυπνάει ο ξεναγός…':'waking the guide…'; },4000);
    try{
      const r=await fetch(API+'/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({session_id:sid,message:text,persona})});
      const d=await r.json(); clearTimeout(slow); t.remove();
      const l=(d.language==='el'||d.language==='en')?d.language:lang; if(l!==lang){lang=l;applyLang();}
      setState(d.handoff?'sorry':'talking');
      bubble(d.reply,'bot'); footnote(d.footnote); cards(d.events,l); pagelink(d.page,l);
      if(d.handoff) handoff(d.contact||{},l); chips(d.quick_replies);
    }catch(e){ clearTimeout(slow); t.remove(); setState('sorry'); bubble(T[lang].err,'bot'); }
    busy=false;send.disabled=false;input.focus();
  }
  function applyLang(){ $('#vx-lang').textContent=lang==='el'?'EN':'ΕΛ'; input.placeholder=ph[lang];
    const p=personas.find(x=>x.id===persona); if(p){$('#vx-name').textContent=lang==='el'?p.name:p.name_en;$('#vx-tag').textContent=lang==='el'?p.tagline:p.tagline_en;} minis(); }

  fetch(API+'/personas').then(r=>r.json()).then(d=>{ personas=d.personas||[];
    if(persona&&!personas.some(p=>p.id===persona)) persona=null;
    loadAvatar(persona||d.default||'kouts'); minis(); applyLang();
  }).catch(()=>{});

  // Το free tier κοιμίζει το service μετά από 15' ησυχίας και θέλει ~1' να ξυπνήσει.
  // Το ξυπνάμε μόλις ανοίξει το παράθυρο — όσο ο επισκέπτης διαβάζει και πληκτρολογεί.
  let woken=false;
  function wake(){ if(woken)return; woken=true; fetch(API+'/health').catch(()=>{}); }
  launcher.addEventListener('pointerenter',wake,{once:true});

  launcher.onclick=()=>{ wake(); panel.classList.toggle('open');
    if(!opened){ opened=true; applyLang(); if(persona){ const p=personas.find(x=>x.id===persona); choose(persona,true);} else showPicker(); }
    input.focus(); };
  $('#vx-close').onclick=()=>panel.classList.remove('open');
  $('#vx-lang').onclick=()=>{ lang=lang==='el'?'en':'el'; applyLang(); };
  $('#vx-form').onsubmit=e=>{ e.preventDefault(); ask(input.value); };
})();
})();
