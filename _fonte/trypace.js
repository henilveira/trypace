/* Trypace: rolagem suave, entradas, vitrine, fileiras, sacola, escolha por mim e upgrade. */
(function(){
  var TP=window.TP||{p:[]};
  var $=function(s,c){return (c||document).querySelector(s)},$$=function(s,c){return Array.prototype.slice.call((c||document).querySelectorAll(s))};
  var porId={};TP.p.forEach(function(p){porId[p.id]=p});
  function brl(v){return 'R$ '+Math.round(v).toLocaleString('pt-BR')}
  var calmo=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var raf=window.requestAnimationFrame.bind(window);

  /* Rolagem suave no desktop (Lenis). No celular fica a rolagem nativa. */
  var lenis=null;
  if(!calmo&&window.Lenis){
    lenis=new Lenis({duration:1.15,easing:function(t){return Math.min(1,1.001-Math.pow(2,-10*t))},smoothWheel:true,wheelMultiplier:.95});
    (function loop(t){lenis.raf(t);raf(loop)})(0);
  }
  function rolarAte(alvo){
    if(lenis){lenis.scrollTo(alvo,{offset:-64,duration:1.4})}
    else{var y=(typeof alvo==='number')?alvo:alvo.getBoundingClientRect().top+window.scrollY-64;window.scrollTo({top:y,behavior:calmo?'auto':'smooth'})}
  }
  document.addEventListener('click',function(e){
    var a=e.target.closest('a[href^="#"]');if(!a)return;
    var id=a.getAttribute('href').slice(1);if(!id)return;
    var alvo=document.getElementById(id);if(!alvo)return;
    e.preventDefault();rolarAte(alvo);history.replaceState(null,'','#'+id);
    var nav=$('.nav');if(nav)nav.classList.remove('aberto');
  });

  /* Navegação: fundo mais firme depois de rolar, menu no celular */
  var nav=$('.nav');
  function navEstado(){if(nav)nav.classList.toggle('rolou',window.scrollY>8)}
  window.addEventListener('scroll',navEstado,{passive:true});navEstado();
  var menuBtn=$('.menu-btn');
  if(menuBtn)menuBtn.addEventListener('click',function(){var on=nav.classList.toggle('aberto');menuBtn.setAttribute('aria-expanded',on)});

  /* Entradas ao rolar */
  var alvos=$$('[data-rv]');
  if('IntersectionObserver' in window&&!calmo){
    var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('on');io.unobserve(e.target)}})},{rootMargin:'0px 0px -12% 0px',threshold:.08});
    alvos.forEach(function(el){io.observe(el)});
  }else{alvos.forEach(function(el){el.classList.add('on')})}

  /* Parallax leve nas fotos grandes */
  var pxs=$$('[data-px]');
  if(pxs.length&&!calmo){
    var visiveis=new Set();
    var iop=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting)visiveis.add(e.target);else visiveis.delete(e.target)})},{rootMargin:'120px 0px'});
    pxs.forEach(function(el){iop.observe(el)});
    var pedido=false;
    function px(){pedido=false;var vh=window.innerHeight;visiveis.forEach(function(el){var r=el.getBoundingClientRect();var p=(r.top+r.height/2-vh/2)/(vh+r.height);var img=el.querySelector('.px');if(img)img.style.setProperty('--py',(p*-90).toFixed(1)+'px')})}
    function pedir(){if(!pedido){pedido=true;raf(px)}}
    if(lenis)lenis.on('scroll',pedir);
    window.addEventListener('scroll',pedir,{passive:true});window.addEventListener('resize',pedir);pedir();
  }

  /* Vitrine: troca suave com barra de progresso */
  var vit=$('.vitrine');
  if(vit){
    var slides=$$('.slide',vit),segs=$$('.segmentos button',vit),atual=0,pausado=calmo,toque=null;
    function ir(i){
      i=(i+slides.length)%slides.length;
      slides.forEach(function(s,k){s.classList.toggle('ativo',k===i);s.setAttribute('aria-hidden',k===i?'false':'true');$$('a,button',s).forEach(function(b){b.tabIndex=k===i?0:-1})});
      segs.forEach(function(b,k){b.classList.toggle('feito',k<i);b.setAttribute('aria-current',k===i?'true':'false');var sp=b.firstElementChild;sp.style.animation='none';void sp.offsetWidth;sp.style.animation=''});
      atual=i;
    }
    segs.forEach(function(b,k){
      b.addEventListener('click',function(){ir(k)});
      b.firstElementChild.addEventListener('animationend',function(){if(k===atual&&!pausado)ir(atual+1)});
    });
    var pausa=$('.pausa',vit),icP=pausa.innerHTML,icPlay=pausa.dataset.play;
    function marcarPausa(){vit.classList.toggle('pausado',pausado);pausa.innerHTML=pausado?icPlay:icP;pausa.setAttribute('aria-label',pausado?'Continuar destaques':'Pausar destaques')}
    pausa.addEventListener('click',function(){pausado=!pausado;marcarPausa()});
    document.addEventListener('visibilitychange',function(){vit.classList.toggle('pausado',pausado||document.hidden)});
    vit.addEventListener('touchstart',function(e){toque=e.touches[0].clientX},{passive:true});
    vit.addEventListener('touchend',function(e){if(toque===null)return;var d=e.changedTouches[0].clientX-toque;toque=null;if(Math.abs(d)>50)ir(atual+(d<0?1:-1))});
    ir(0);marcarPausa();
  }

  /* Fileiras que rolam para o lado */
  $$('[data-rolagem]').forEach(function(r){
    var box=r.parentElement,ant=$('[data-voltar]',box),prox=$('[data-avancar]',box);
    if(!ant||!prox)return;
    function passo(){var c=r.firstElementChild;if(!c)return r.clientWidth*.8;var w=c.getBoundingClientRect().width+16;return w*Math.max(1,Math.floor((r.clientWidth-60)/w))}
    function estado(){ant.disabled=r.scrollLeft<4;prox.disabled=r.scrollLeft+r.clientWidth>=r.scrollWidth-4;ant.parentElement.classList.toggle('sem',r.scrollWidth<=r.clientWidth+4)}
    ant.addEventListener('click',function(){r.scrollBy({left:-passo(),behavior:calmo?'auto':'smooth'})});
    prox.addEventListener('click',function(){r.scrollBy({left:passo(),behavior:calmo?'auto':'smooth'})});
    r.addEventListener('scroll',function(){raf(estado)},{passive:true});
    window.addEventListener('resize',estado);estado();
  });

  /* Dúvidas abrindo com altura animada */
  $$('.faq details').forEach(function(d){
    var s=$('summary',d),c=$('.resp',d),anim=null;
    s.addEventListener('click',function(e){
      if(calmo||!c.animate)return;
      e.preventDefault();if(anim)anim.cancel();
      if(!d.open){d.open=true;var h=c.scrollHeight;anim=c.animate([{height:'0px',opacity:0},{height:h+'px',opacity:1}],{duration:600,easing:'cubic-bezier(.16,1,.3,1)'});anim.onfinish=function(){anim=null}}
      else{var h2=c.scrollHeight;anim=c.animate([{height:h2+'px',opacity:1},{height:'0px',opacity:0}],{duration:420,easing:'cubic-bezier(.65,0,.35,1)'});anim.onfinish=function(){d.open=false;anim=null}}
    });
  });

  /* Galeria da página do relógio */
  var gal=$('.galeria');
  if(gal){
    var imgs=$$('.principal img',gal),mins=$$('.miniaturas button',gal);
    mins.forEach(function(b,k){b.addEventListener('click',function(){imgs.forEach(function(im,j){im.classList.toggle('on',j===k)});mins.forEach(function(m,j){m.setAttribute('aria-current',j===k?'true':'false')})})});
  }

  /* Toast */
  var toast=$('#toast'),tt;
  function avisar(m,ms){toast.textContent=m;toast.classList.add('on');clearTimeout(tt);tt=setTimeout(function(){toast.classList.remove('on')},ms||3500)}

  /* Mensagem pronta para o direct */
  function abrirDirect(){var w=null;try{w=window.open(TP.ig,'_blank','noopener')}catch(e){}if(!w)location.href=TP.ig}
  function mandar(msg){
    if(navigator.clipboard&&navigator.clipboard.writeText){
      navigator.clipboard.writeText(msg).then(function(){avisar('Mensagem copiada. Cole no direct e envie.',6000);setTimeout(abrirDirect,700)},function(){avisar('Copie e envie no direct:\n'+msg,12000);setTimeout(abrirDirect,2500)});
    }else{avisar('Copie e envie no direct:\n'+msg,12000);setTimeout(abrirDirect,2500)}
  }
  document.addEventListener('click',function(e){var b=e.target.closest('[data-msg]');if(b){e.preventDefault();mandar(b.dataset.msg)}});

  /* Sacola */
  var sacola=[];
  try{sacola=JSON.parse(localStorage.getItem('trypace-sacola')||'[]').filter(function(id){return porId[id]})}catch(e){}
  function salvar(){try{localStorage.setItem('trypace-sacola',JSON.stringify(sacola))}catch(e){}}
  function fotoMini(p){return p.foto?'<img src="'+p.foto+'" alt="" width="72" height="72">':'<span class="mini"></span>'}
  var dlg=$('#sacola');
  function render(){
    var c=$('.contador');c.textContent=sacola.length;if(sacola.length)c.removeAttribute('data-zero');else c.setAttribute('data-zero','');
    $('#abrir-sacola').setAttribute('aria-label','Abrir sacola, '+sacola.length+(sacola.length===1?' item':' itens'));
    $('#itens').innerHTML=sacola.map(function(id,i){var p=porId[id];return '<li style="animation-delay:'+(i*70)+'ms">'+fotoMini(p)+'<div><b>'+p.nome+'</b><span>'+brl(p.preco)+'</span></div><button type="button" data-rem="'+i+'">Remover</button></li>'}).join('');
    $('#total').textContent=brl(sacola.reduce(function(s,id){return s+porId[id].preco},0));
    $('#vazio').hidden=sacola.length>0;$('#fechamento').hidden=sacola.length===0;$('#itens').hidden=sacola.length===0;
  }
  function pular(){var c=$('.contador');c.classList.remove('pulo');void c.offsetWidth;c.classList.add('pulo')}
  function adicionar(id){
    if(sacola.indexOf(id)>-1){avisar(porId[id].nome+' já está na sacola');return}
    sacola.push(id);salvar();render();pular();avisar(porId[id].nome+' foi para a sacola');
  }
  $('#itens').addEventListener('click',function(e){var b=e.target.closest('[data-rem]');if(!b)return;sacola.splice(+b.dataset.rem,1);salvar();render()});
  document.addEventListener('click',function(e){var a=e.target.closest('[data-add]');if(a){e.preventDefault();adicionar(a.dataset.add)}});
  function abrir(){render();if(dlg.showModal)dlg.showModal();else dlg.setAttribute('open','');document.body.classList.add('travado');if(lenis)lenis.stop()}
  function fechar(){if(dlg.close)dlg.close();else{dlg.removeAttribute('open');aoFechar()}}
  function aoFechar(){document.body.classList.remove('travado');if(lenis)lenis.start()}
  dlg.addEventListener('close',aoFechar);
  dlg.addEventListener('click',function(e){if(e.target===dlg||e.target.closest('[data-fechar]'))fechar()});
  $('#abrir-sacola').addEventListener('click',abrir);
  $$('[data-abrir-sacola]').forEach(function(b){b.addEventListener('click',abrir)});
  $('#fechamento').addEventListener('submit',function(e){
    e.preventDefault();if(!sacola.length)return;
    var nome=$('#f-nome').value.trim(),cidade=$('#f-cidade').value.trim();
    var l=['Faala, Trypace! Quero fechar este pedido do site:'];
    sacola.forEach(function(id){var p=porId[id];l.push('- '+p.nome+' ('+brl(p.preco)+')')});
    if(sacola.length>1)l.push('Total: '+brl(sacola.reduce(function(s,id){return s+porId[id].preco},0)));
    if(nome)l.push('Nome: '+nome);if(cidade)l.push('Cidade: '+cidade);
    l.push('Ainda tem disponível?');mandar(l.join('\n'));
  });
  render();

  /* Números que contam até o valor */
  function contar(el,para){
    var de=+(el.dataset.v||0);el.dataset.v=para;
    if(calmo||de===para){el.textContent=brl(para);return}
    var t0=performance.now(),dur=900;
    (function f(t){var k=Math.min(1,(t-t0)/dur);k=1-Math.pow(1-k,4);el.textContent=brl(de+(para-de)*k);if(k<1)raf(f)})(t0);
  }

  /* Escolha o Garmin por mim */
  var quiz=$('#quiz');
  if(quiz){
    var P=[
      {q:'Como está sua corrida hoje?',a:'Sem resposta errada. É pra gente entender seu momento.',o:[['inicio','Começando agora','Corro pouco ou quero começar'],['evolucao','Corro com frequência','5 a 10 km algumas vezes por semana'],['performance','Treino pra prova','Meia, maratona, planilha'],['triathlon','Triathlon ou ultra','Nado, pedal ou provas longas']]},
      {q:'O que mais importa no relógio?',a:'Escolha o que pesa mais pra você.',o:[['preco','Preço','O essencial bem feito'],['tela','Tela bonita','AMOLED, fácil de ler'],['bateria','Bateria','Carregar o mínimo possível'],['dados','Dados de treino','Prontidão, carga e recuperação']]},
      {q:'Quer ouvir música pelo relógio?',a:'Música offline no pulso, sem levar o celular.',o:[['sim','Sim','Quero treinar sem o celular'],['nao','Não preciso','Uso o celular ou não ouço']]},
      {q:'Quanto quer investir?',a:'Preços de seminovo revisado.',o:[[1000,'Até R$ 1.000','Forerunner 55 e 245'],[1600,'Até R$ 1.600','Forerunner 165, 255 e mais'],[2200,'Até R$ 2.200','Forerunner 265, 945 e mais'],[99999,'Quero o melhor','Forerunner 955 e 965']]}
    ];
    var passo=0,resp=[],palco=$('.palco-q',quiz),barra=$('.barra i',quiz),num=$('[data-num]',quiz),voltar=$('.voltar',quiz),res=$('.resultado',quiz),perg=$('.perguntas',quiz);
    function trocar(fn){if(calmo){fn();return}palco.classList.add('sai');setTimeout(function(){fn();palco.classList.remove('sai');palco.classList.add('entra');void palco.offsetWidth;palco.classList.remove('entra')},380)}
    function desenhar(){
      var fim=passo>=P.length;
      perg.hidden=fim;res.hidden=!fim;voltar.hidden=passo===0||fim;
      barra.style.width=fim?'100%':((passo+1)*25)+'%';
      num.textContent=fim?'Pronto':'Pergunta '+(passo+1)+' de '+P.length;
      if(!fim){
        var q=P[passo];$('.pergunta-q',perg).textContent=q.q;$('.ajuda-q',perg).textContent=q.a;
        $('.respostas',perg).innerHTML=q.o.map(function(o){return '<button class="resposta" type="button" data-v="'+o[0]+'"><b>'+o[1]+'</b><span>'+o[2]+'</span></button>'}).join('');
      }else{resultado()}
      if(window.scrollY>200)rolarAte(0);
    }
    function nota(p){
      var perfil=resp[0],foco=resp[1],musica=resp[2],teto=+resp[3],s=0;
      if(p.perfil.indexOf(perfil)>-1)s+=3;
      if(foco==='preco')s+=2-p.preco/800;
      if(foco==='tela'&&p.amoled)s+=2.5;
      if(foco==='bateria')s+=p.gpsH/14;
      if(foco==='dados')s+=p.nivel*.9;
      if(musica==='sim')s+=p.musica?1.5:-2;
      if(musica==='nao'&&p.musica)s-=.3;
      if(p.preco>teto)s-=10;
      return s;
    }
    function resultado(){
      var lista=TP.p.slice().sort(function(a,b){return nota(b)-nota(a)});
      var r=lista[0],alt=lista.slice(1,3);
      $('[data-r-nome]',res).textContent=r.nome;
      $('[data-r-porque]',res).textContent=r.porque;
      $('[data-r-motivos]',res).innerHTML=r.motivos.map(function(m){return '<li>'+m+'</li>'}).join('');
      $('[data-r-preco]',res).textContent=brl(r.preco);
      $('[data-r-foto]',res).innerHTML=r.fotoG?'<img src="'+r.fotoG+'" alt="'+r.marca+' '+r.nome+'" width="600" height="600">':TP.desenho;
      $('[data-r-ver]',res).href=r.url;
      $('[data-r-add]',res).dataset.add=r.id;
      $('[data-r-alt]',res).innerHTML=alt.map(function(a){return '<a href="'+a.url+'">'+a.nome+'<span>'+brl(a.preco)+'</span></a>'}).join('');
      var rot={inicio:'começando agora',evolucao:'corro com frequência',performance:'treino pra prova',triathlon:'triathlon ou ultra'};
      $('[data-r-direct]',res).dataset.msg='Faala, Trypace! Fiz o "Escolha por mim" no site ('+rot[resp[0]]+', '+(resp[2]==='sim'?'quero música':'sem música')+') e deu o '+r.nome+'. Ainda tem disponível?';
    }
    quiz.addEventListener('click',function(e){
      var b=e.target.closest('.resposta');
      if(b){var v=b.dataset.v;trocar(function(){resp[passo]=v;passo++;desenhar()});return}
      if(e.target.closest('.voltar')){trocar(function(){passo=Math.max(0,passo-1);desenhar()});return}
      if(e.target.closest('[data-refazer]')){trocar(function(){passo=0;resp=[];desenhar()})}
    });
    var pre=new URLSearchParams(location.search).get('perfil');
    if(pre&&P[0].o.some(function(o){return o[0]===pre})){resp[0]=pre;passo=1}
    desenhar();
  }

  /* Upgrade de Garmin */
  var sim=$('#simulador');
  if(sim){
    var TROCA=TP.troca||{},ESTADO={otimo:1,bom:.85,marcas:.65};
    var esc={atual:'fr245',estado:'bom',destino:new URLSearchParams(location.search).get('para')||'fr265'};
    if(!porId[esc.destino])esc.destino='fr265';
    function nomeAtual(){var b=$('[data-atual="'+esc.atual+'"]',sim);return b?b.textContent:''}
    function nomeEstado(){var b=$('[data-estado="'+esc.estado+'"]',sim);return b?b.textContent.toLowerCase():''}
    function atualizar(){
      $$('[data-atual]',sim).forEach(function(b){b.setAttribute('aria-pressed',b.dataset.atual===esc.atual)});
      $$('[data-estado]',sim).forEach(function(b){b.setAttribute('aria-pressed',b.dataset.estado===esc.estado)});
      $$('[data-destino]',sim).forEach(function(b){b.setAttribute('aria-pressed',b.dataset.destino===esc.destino)});
      var d=porId[esc.destino],base=TROCA[esc.atual];
      contar($('[data-novo]',sim),d.preco);
      $('[data-seu]',sim).textContent='Seu '+nomeAtual();
      var cred=$('[data-cred]',sim),dif=$('[data-dif]',sim),rot=$('[data-dif-rot]',sim);
      if(base){var v=Math.round(base*ESTADO[esc.estado]/10)*10;cred.textContent='− '+brl(v);rot.textContent='Você paga a diferença';contar(dif,Math.max(0,d.preco-v))}
      else{cred.textContent='Avaliado no direct';rot.textContent='Você paga a diferença';dif.textContent='Sob consulta';dif.dataset.v=0}
      $('[data-pedir]',sim).dataset.msg='Faala, Trypace! Quero fazer upgrade: tenho um '+nomeAtual()+' ('+nomeEstado()+' estado) e quero o '+d.nome+' ('+brl(d.preco)+'). Quanto fica a diferença?';
    }
    sim.addEventListener('click',function(e){
      var b=e.target.closest('[data-atual],[data-estado],[data-destino]');if(!b)return;
      if(b.dataset.atual)esc.atual=b.dataset.atual;if(b.dataset.estado)esc.estado=b.dataset.estado;if(b.dataset.destino)esc.destino=b.dataset.destino;
      atualizar();
    });
    atualizar();
  }

  /* Comparador: até 3 relógios, radar, barras e ficha */
  var cmp=$('#comparador');
  if(cmp){
    var CORES=['#B8FF00','#FFFFFF','#8E8E93'];
    var NIVEL=['Básico','Intermediário','Avançado','Completo'];
    function cl(v){return Math.max(1,Math.min(10,v))}
    function extras(p){return [p.musica,p.mapas,p.pay,p.tri].filter(Boolean).length}
    var ASP=[
      {k:'batDia',t:'Bateria no dia a dia',n:function(p){return cl(p.batDias/24*10)},v:function(p){return p.bat}},
      {k:'batGps',t:'Bateria com GPS',n:function(p){return cl(p.gpsH/42*10)},v:function(p){return p.gpsH+' h'}},
      {k:'gps',t:'Precisão do GPS',n:function(p){return p.multibanda?10:6},v:function(p){return p.multibanda?'Multibanda':'Simples'}},
      {k:'tela',t:'Tela',n:function(p){return p.amoled?10:6},v:function(p){return p.tela}},
      {k:'dados',t:'Dados de treino',n:function(p){return [3,5.5,8,10][p.nivel]},v:function(p){return NIVEL[p.nivel]}},
      {k:'extras',t:'Recursos extras',n:function(p){return cl(extras(p)/4*10)},v:function(p){return extras(p)+' de 4'}},
      {k:'leve',t:'Leveza',n:function(p){return cl((58-p.pesoG)/(58-36)*10)},v:function(p){return p.peso}}
    ];
    var sels=$$('[data-sel]',cmp),q=new URLSearchParams(location.search);
    ['a','b','c'].forEach(function(k,i){var v=q.get(k);if(v!==null&&(v===''||porId[v])&&sels[i]&&!(v===''&&i<2))sels[i].value=v});
    sels.forEach(function(s,i){
      var antes=sels.slice(0,i).map(function(x){return x.value});
      if(s.value&&antes.indexOf(s.value)>-1){
        if(i===2){s.value=''}else{var livre=TP.p.filter(function(p){return antes.indexOf(p.id)<0&&p.id!==s.value})[0];s.value=livre?livre.id:''}
      }
    });
    function escolhidos(){return sels.map(function(s,i){return {i:i,p:porId[s.value]}}).filter(function(x){return x.p})}
    function cardSlot(i,p){
      var el=$('[data-card="'+i+'"]',cmp);
      var html=p?('<div class="palco">'+(p.fotoG?'<img src="'+p.fotoG+'" alt="'+p.marca+' '+p.nome+'" width="600" height="450" loading="lazy">':TP.desenho)+'</div>'+
        '<div class="corpo"><h2>'+p.nome+'</h2><p class="resumo">'+p.resumo+'</p><div class="pe"><b>'+brl(p.preco)+'</b><span style="display:flex;gap:8px"><a class="btn btn-claro btn-p" href="'+p.url+'">Ver</a><button class="btn btn-lima btn-p" type="button" data-add="'+p.id+'">Comprar</button></span></div></div>')
        :'<div class="slot-vazio">Escolha um terceiro relógio acima pra comparar.</div>';
      var id=p?p.id:'-';
      if(el.dataset.id===id)return;
      var primeira=!el.dataset.id;el.dataset.id=id;
      if(calmo||primeira){el.innerHTML=html;return}
      el.classList.add('troca');setTimeout(function(){el.innerHTML=html;el.classList.remove('troca')},260);
    }
    /* Radar */
    var svg=$('[data-radar]'),CX=230,CY=220,R=150,N=ASP.length,formas={};
    function pt(i,v){var a=-Math.PI/2+i*2*Math.PI/N;return [(CX+Math.cos(a)*R*v/10).toFixed(1),(CY+Math.sin(a)*R*v/10).toFixed(1)]}
    (function base(){
      var s='';
      [2.5,5,7.5,10].forEach(function(v){s+='<polygon points="'+ASP.map(function(a,i){return pt(i,v).join(',')}).join(' ')+'" fill="none" stroke="#3A3A3C" stroke-width="1"/>'});
      ASP.forEach(function(a,i){var e=pt(i,10),l=pt(i,11.4);s+='<line x1="'+CX+'" y1="'+CY+'" x2="'+e[0]+'" y2="'+e[1]+'" stroke="#3A3A3C" stroke-width="1"/>';
        var anc=Math.abs(l[0]-CX)<8?'middle':(l[0]>CX?'start':'end');s+='<text x="'+l[0]+'" y="'+(+l[1]+4)+'" text-anchor="'+anc+'" fill="#A1A1A6" font-size="12" font-weight="600" font-family="Montserrat,sans-serif">'+a.t+'</text>'});
      [0,1,2].forEach(function(k){s+='<polygon data-forma="'+k+'" points="'+ASP.map(function(a,i){return pt(i,0).join(',')}).join(' ')+'" fill="'+CORES[k]+'" fill-opacity="'+(k===1?.08:.14)+'" stroke="'+CORES[k]+'" stroke-width="2.2" stroke-linejoin="round"'+(k===2?' stroke-dasharray="7 5"':'')+' opacity="0"/>'});
      svg.innerHTML=s;
      [0,1,2].forEach(function(k){formas[k]={el:svg.querySelector('[data-forma="'+k+'"]'),v:ASP.map(function(){return 0}),id:0}});
    })();
    function animarForma(k,alvo,visivel){
      var f=formas[k],de=f.v.slice(),t0=performance.now(),dur=calmo?0:1100,meu=++f.id;
      f.el.style.transition='opacity .5s';f.el.setAttribute('opacity',visivel?1:0);
      (function passo(t){if(meu!==f.id)return;var x=dur?Math.min(1,(t-t0)/dur):1;x=1-Math.pow(1-x,4);f.v=de.map(function(d,i){return d+(alvo[i]-d)*x});
        f.el.setAttribute('points',f.v.map(function(v,i){return pt(i,v).join(',')}).join(' '));if(x<1)raf(passo)})(t0);
    }
    var visto=false,grafSec=$('#graficos');
    function desenhar(){
      var es=escolhidos();
      sels.forEach(function(s,i){cardSlot(i,porId[s.value])});
      $('[data-legenda]').innerHTML=es.map(function(x){return '<span><i class="'+(x.i===2?'tracejado':'')+'" style="background:'+CORES[x.i]+'"></i>'+x.p.nome+'</span>'}).join('');
      var bx=$('[data-barras]');
      if(!bx.children.length)bx.innerHTML=ASP.map(function(a){return '<div class="aspecto" data-asp="'+a.k+'"><h3>'+a.t+'</h3><div class="linhas-b">'+[0,1,2].map(function(k){return '<div class="barra-l" data-l="'+k+'"><div class="trilha-b"><i style="background:'+CORES[k]+(k===2?';background-image:repeating-linear-gradient(90deg,#8E8E93 0 10px,#6E6E73 10px 14px)':'')+'"></i></div><span class="v"></span></div>'}).join('')+'</div></div>'}).join('');
      ASP.forEach(function(a){
        var box=$('[data-asp="'+a.k+'"]',bx),notas=es.map(function(x){return a.n(x.p)}),max=Math.max.apply(null,notas),unico=notas.filter(function(v){return v===max}).length<es.length;
        [0,1,2].forEach(function(k){
          var l=$('[data-l="'+k+'"]',box),x=es.filter(function(e){return e.i===k})[0];
          l.hidden=!x;if(!x)return;
          var n=a.n(x.p);l.classList.toggle('best',es.length>1&&unico&&n===max);
          $('.v',l).textContent=a.v(x.p);l.title=x.p.nome+': '+a.v(x.p);
          $('i',l).style.width=(visto?n*10:0)+'%';
        });
      });
      if(visto)[0,1,2].forEach(function(k){var x=es.filter(function(e){return e.i===k})[0];animarForma(k,x?ASP.map(function(a){return a.n(x.p)}):formas[k].v,!!x)});
      var LIN=[
        ['Preço',function(p){return brl(p.preco)},function(p){return -p.preco}],
        ['Tela',function(p){return p.tela},function(p){return p.amoled?1:0}],
        ['Bateria no modo relógio',function(p){return p.bat},function(p){return p.batDias}],
        ['Bateria com GPS',function(p){return p.gpsH+' h'},function(p){return p.gpsH}],
        ['GPS',function(p){return p.multibanda?'Multibanda':'Simples'},function(p){return p.multibanda?1:0}],
        ['Métrica de recuperação',function(p){return p.rec},null],
        ['Dados de treino',function(p){return NIVEL[p.nivel]},function(p){return p.nivel}],
        ['Música offline',function(p){return p.musica?'Sim':'Não'},function(p){return p.musica?1:0}],
        ['Mapas',function(p){return p.mapas?'Sim':'Não'},function(p){return p.mapas?1:0}],
        ['Multiesporte',function(p){return p.tri?'Sim':'Não'},function(p){return p.tri?1:0}],
        ['Pagamento por aproximação',function(p){return p.pay?'Sim':'Não'},function(p){return p.pay?1:0}],
        ['Peso',function(p){return p.peso},function(p){return -p.pesoG}],
        ['Resistência à água',function(){return '5 ATM'},null]
      ];
      var h='<thead><tr><th scope="col"><span class="sr">Item</span></th>'+es.map(function(x){return '<th scope="col"><span class="cab-cor"><span class="cor c'+x.i+'" style="width:12px;height:12px;border-radius:3px;display:inline-block"></span>'+x.p.nome+'</span></th>'}).join('')+'</tr></thead><tbody>';
      LIN.forEach(function(r){
        var vs=r[2]?es.map(function(x){return r[2](x.p)}):[],mx=vs.length?Math.max.apply(null,vs):null,unico=vs.filter(function(v){return v===mx}).length<es.length;
        h+='<tr><th scope="row">'+r[0]+'</th>'+es.map(function(x,j){return '<td'+(r[2]&&es.length>1&&unico&&vs[j]===mx?' class="best"':'')+'>'+r[1](x.p)+'</td>'}).join('')+'</tr>';
      });
      $('[data-tabela]').innerHTML=h+'</tbody>';
      var u=new URLSearchParams();['a','b','c'].forEach(function(k,i){u.set(k,sels[i].value)});history.replaceState(null,'','?'+u.toString());
    }
    sels.forEach(function(s){s.addEventListener('change',function(){
      if(s.value&&sels.filter(function(x){return x.value===s.value}).length>1)avisar('Esse relógio já está na comparação');
      desenhar()})});
    desenhar();
    if('IntersectionObserver' in window&&!calmo){
      var iog=new IntersectionObserver(function(es){if(es[0].isIntersecting){visto=true;iog.disconnect();desenhar()}},{threshold:.15});iog.observe(grafSec);
    }else{visto=true;desenhar()}
  }

  var ano=$('#ano');if(ano)ano.textContent=new Date().getFullYear();
})();
