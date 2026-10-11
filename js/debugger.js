// FlowForge WebStudio — Debugger aprimorado
(function(){
 'use strict';
 const $=s=>document.querySelector(s);
 const LIMIT=1500;
 const state={logs:[],errors:[],events:[],network:[],paused:false,startedAt:null,projectName:'',lastHtml:''};
 const now=()=>new Date().toISOString();
 function esc(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
 function safe(v,seen=new WeakSet()){
  if(v===null||v===undefined)return String(v);
  if(typeof v==='string')return v;
  if(typeof v==='function')return `[Function ${v.name||'anonymous'}]`;
  if(v instanceof Error)return {name:v.name,message:v.message,stack:v.stack||''};
  if(typeof Element!=='undefined'&&v instanceof Element)return `<${v.tagName.toLowerCase()}${v.id?'#'+v.id:''}${v.classList?.length?'.'+[...v.classList].slice(0,3).join('.'):''}>`;
  if(typeof v==='object'){
   if(seen.has(v))return '[Circular]';seen.add(v);
   if(Array.isArray(v))return v.slice(0,100).map(x=>safe(x,seen));
   const out={};Object.keys(v).slice(0,80).forEach(k=>{try{out[k]=safe(v[k],seen)}catch(e){out[k]='[unavailable]'}});return out;
  }
  return String(v);
 }
 function printable(v){try{return typeof v==='string'?v:JSON.stringify(v)}catch(_){return String(v)}}
 function add(bucket,item){state[bucket].push(item);if(state[bucket].length>LIMIT)state[bucket].splice(0,state[bucket].length-LIMIT);render()}
 function row(kind,args,time=now(),meta=''){
  const details=args.map(printable).join(' ');
  return `<div class="dbgRow dbg-${esc(kind)}"><small>${esc(new Date(time).toLocaleTimeString())}</small><span class="dbgMessage">${esc(details)}${meta?`<details><summary>Detalhes</summary><pre>${esc(meta)}</pre></details>`:''}</span></div>`;
 }
 function matches(item){const q=($('#dbgSearch')?.value||'').trim().toLowerCase();return !q||JSON.stringify(item).toLowerCase().includes(q)}
 function render(){
  if(!$('#dbgConsole'))return;
  $('#dbgConsole').innerHTML=state.logs.filter(matches).map(x=>row(x.kind,x.args,x.time,x.stack||'')).join('')||'<em>Sem mensagens correspondentes.</em>';
  $('#dbgErrors').innerHTML=state.errors.filter(matches).map(x=>row('error',x.args,x.time,x.stack||'')).join('')||'<em>Sem erros correspondentes.</em>';
  $('#dbgEvents').innerHTML=state.events.filter(matches).map(x=>row('event',x.args,x.time)).join('')||'<em>Nenhum evento correspondente.</em>';
  $('#dbgNetwork').innerHTML=state.network.filter(matches).map(x=>row(x.ok?'info':'error',[`${x.method} ${x.url} → ${x.status}`,x.duration+' ms'],x.time,x.error||'')).join('')||'<em>Nenhuma requisição registrada.</em>';
  $('#dbgErrorCount').textContent=state.errors.length;
  $('#dbgState').textContent=state.paused?'Pausado':(state.startedAt?'Monitorando':'Parado');
  $('#dbgLogCount').textContent=state.logs.length;
  $('#dbgEventCount').textContent=state.events.length;
  $('#dbgNetworkCount').textContent=state.network.length;
 }
 function inspect(){
  const w=$('#preview')?.contentWindow;if(!w)return;
  try{
   const vars={};Object.keys(w).filter(k=>/^ff|contador|score|nome|ativo|total|valor|resultado/i.test(k)).slice(0,200).forEach(k=>{try{const v=w[k];if(['string','number','boolean'].includes(typeof v))vars[k]=v}catch(_){}});
   $('#dbgVars').innerHTML=Object.entries(vars).map(([k,v])=>`<div class="dbgKV"><b>${esc(k)}</b><span>${esc(v)}</span></div>`).join('')||'<em>Nenhuma variável global pública detectada. Use window.minhaVariavel para expor valores.</em>';
   const doc=w.document;
   const comps=[...doc.querySelectorAll('.ff-component')].map(el=>{const c=el.querySelector('[data-ff-control],input,button,textarea,select,img,video,audio,canvas')||el;const style=w.getComputedStyle(el);return {name:c.id||el.id||el.dataset.flowId||'(sem nome)',kind:el.className?.toString().match(/ff-kind-([\w-]+)/)?.[1]||el.tagName.toLowerCase(),value:('value'in c?c.value:(c.textContent||'').trim()).toString().slice(0,180),visible:style.display!=='none'&&style.visibility!=='hidden'&&el.getClientRects().length>0,enabled:!('disabled'in c)||!c.disabled}});
   $('#dbgComponents').innerHTML=comps.map(c=>`<div class="dbgKV"><b>${esc(c.name)} <small>${esc(c.kind)}</small></b><span>${esc(c.value)} ${c.visible?'':'· oculto'} ${c.enabled?'':'· desabilitado'}</span></div>`).join('')||'<em>O preview não contém componentes .ff-component.</em>';
   const pages=[...doc.querySelectorAll('[data-page-id],.ff-page')].map(p=>({id:p.dataset.pageId||p.id,visible:w.getComputedStyle(p).display!=='none'&&!p.hidden}));
   $('#dbgPageInfo').textContent=pages.length?pages.map(p=>`${p.id}${p.visible?' (ativa)':''}`).join(' · '):'Sem páginas detectadas';
  }catch(e){add('errors',{time:now(),args:['Falha ao inspecionar o preview',e.message],stack:e.stack||''})}
 }
 function bridgeScript(){
  // Executa antes do código gerado, capturando erros de inicialização e console do OnLoad.
  return `<script>(function(){if(window.__ffDebuggerInstalled)return;window.__ffDebuggerInstalled=true;var send=function(type,data){try{parent.postMessage(Object.assign({__ffdbg:1,type:type,time:new Date().toISOString()},data||{}),'*')}catch(_){}};var repr=function(v){try{if(v instanceof Error)return {name:v.name,message:v.message,stack:v.stack||''};if(v&&v.nodeType===1)return '<'+v.tagName.toLowerCase()+(v.id?'#'+v.id:'')+'>';if(typeof v==='object'&&v!==null){var seen=new WeakSet();return JSON.parse(JSON.stringify(v,function(k,x){if(x instanceof Error)return {name:x.name,message:x.message,stack:x.stack};if(typeof x==='object'&&x!==null){if(seen.has(x))return '[Circular]';seen.add(x)}return x}))}return String(v)}catch(_){return String(v)}};['log','info','warn','error','debug','table','assert'].forEach(function(k){var orig=console[k];if(typeof orig!=='function')return;console[k]=function(){var args=[].slice.call(arguments).map(repr);send('console',{kind:k,args:args,stack:(new Error()).stack});try{return orig.apply(console,arguments)}catch(_){}}});window.addEventListener('error',function(e){send('error',{args:[e.message||'Erro de recurso',e.filename||'',(e.lineno||0)+':'+(e.colno||0)],stack:e.error&&e.error.stack||''})},true);window.addEventListener('unhandledrejection',function(e){send('error',{args:['Promise rejeitada',repr(e.reason)],stack:e.reason&&e.reason.stack||''})});window.addEventListener('rejectionhandled',function(e){send('console',{kind:'info',args:['Promise rejeitada tratada posteriormente',repr(e.reason)]})});['click','input','change','submit','keydown'].forEach(function(type){document.addEventListener(type,function(e){var el=e.target;if(!el)return;if(type==='keydown'&&!['Enter','Escape',' '].includes(e.key))return;var root=el.closest&&el.closest('.ff-component'),comp=root||el,tag=(el.tagName||'element').toLowerCase(),id=comp.id||(comp.dataset&&(comp.dataset.flowId||comp.dataset.name))||comp.getAttribute&&comp.getAttribute('name')||'',label=comp.getAttribute&&(comp.getAttribute('aria-label')||comp.getAttribute('title'))||'',txt=(comp.innerText||comp.textContent||'').trim().replace(/\s+/g,' ').slice(0,48);if(!label)label=txt;if(!label)label=id||tag;var kind=tag==='button'?'Botão':(tag==='input'||tag==='textarea'||tag==='select'?'Campo':'Componente'),action=type==='click'?'pressionado':type==='input'?'recebeu entrada':type==='change'?'foi alterado':type==='submit'?'foi enviado':'recebeu tecla '+e.key;var message=kind+' “'+label+'” '+action+'; evento '+type+' disparado no componente '+(id||label);send('event',{args:[message,'Evento: '+type,'Componente: '+(id||label), 'Elemento: '+tag]})},true)});var origFetch=window.fetch;if(origFetch)window.fetch=function(){var args=arguments,url=String(args[0]&&args[0].url||args[0]),method=(args[1]&&args[1].method)||'GET',start=performance.now();return origFetch.apply(this,args).then(function(r){send('network',{method:method,url:url,status:r.status,ok:r.ok,duration:Math.round(performance.now()-start)});return r},function(err){send('network',{method:method,url:url,status:'NETWORK ERROR',ok:false,duration:Math.round(performance.now()-start),error:repr(err)});throw err})};var X=window.XMLHttpRequest;if(X&&!X.prototype.__ffWrapped){var open=X.prototype.open,sendX=X.prototype.send;X.prototype.open=function(m,u){this.__ffreq={method:m,url:String(u)};return open.apply(this,arguments)};X.prototype.send=function(){var x=this,start=performance.now();x.addEventListener('loadend',function(){send('network',{method:x.__ffreq&&x.__ffreq.method||'XHR',url:x.__ffreq&&x.__ffreq.url||'',status:x.status,ok:x.status>=200&&x.status<400,duration:Math.round(performance.now()-start)})},{once:true});return sendX.apply(this,arguments)};X.prototype.__ffWrapped=true}send('console',{kind:'info',args:['Debugger conectado antes da execução do app']})})();</script>`;
 }
 function instrument(html){const bridge=bridgeScript();if(/<head(?:\s[^>]*)?>/i.test(html))return html.replace(/<head(?:\s[^>]*)?>/i,m=>m+bridge);return bridge+html}
 function start(){
  if(typeof window.generated!=='function'){add('errors',{time:now(),args:['Não foi possível gerar o preview: window.generated não está disponível.']});return}
  try{
   state.startedAt=now();state.projectName=window.project?.name||'Projeto sem nome';
   const raw=window.generated();state.lastHtml=raw;
   const html=window.FlowForgeImageAssets?.resolveHtml?.(raw)??raw;
   const f=$('#preview');f.srcdoc=instrument(html);
   $('#debuggerPanel').hidden=false;render();
  }catch(e){add('errors',{time:now(),args:['Falha ao iniciar o preview depurado',e.message],stack:e.stack||''})}
 }
 function exportReport(){
  const report={tool:'FlowForge WebStudio Debugger',version:'1.1',createdAt:now(),project:state.projectName,startedAt:state.startedAt,counts:{logs:state.logs.length,errors:state.errors.length,events:state.events.length,network:state.network.length},logs:state.logs,errors:state.errors,events:state.events,network:state.network};
  const blob=new Blob([JSON.stringify(report,null,2)],{type:'application/json'}),a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='flowforge-debug-'+new Date().toISOString().replace(/[:.]/g,'-')+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);
 }
 addEventListener('message',e=>{
  const d=e.data;if(!d?.__ffdbg)return;
  if(state.paused&&d.type!=='error'&&!(d.type==='network'&&!d.ok))return;
  const time=d.time||now();
  if(d.type==='console')add('logs',{time,kind:d.kind||'log',args:d.args||[],stack:d.stack||''});
  else if(d.type==='error')add('errors',{time,args:d.args||['Erro desconhecido'],stack:d.stack||''});
  else if(d.type==='event')add('events',{time,args:d.args||[]});
  else if(d.type==='network')add('network',{time,method:d.method||'GET',url:d.url||'',status:d.status??'',ok:!!d.ok,duration:d.duration??0,error:d.error||''});
 });
 addEventListener('DOMContentLoaded',()=>{
  $('#debugBtn').onclick=start;
  $('#preview').addEventListener('load',()=>{if(!$('#debuggerPanel').hidden){inspect();render()}});
  $('#dbgClose').onclick=()=>$('#debuggerPanel').hidden=true;
  $('#dbgClear').onclick=()=>{state.logs=[];state.errors=[];state.events=[];state.network=[];render()};
  $('#dbgRefresh').onclick=inspect;$('#dbgPause').onclick=()=>{state.paused=true;render()};$('#dbgResume').onclick=()=>{state.paused=false;render()};
  $('#dbgExport').onclick=exportReport;$('#dbgSearch').addEventListener('input',render);
  document.querySelectorAll('[data-dbg-tab]').forEach(b=>b.onclick=()=>{document.querySelectorAll('[data-dbg-tab]').forEach(x=>x.classList.toggle('active',x===b));document.querySelectorAll('.dbgView').forEach(x=>x.hidden=true);const id=b.dataset.dbgTab;$('#dbg'+id[0].toUpperCase()+id.slice(1)).hidden=false;if(['vars','components'].includes(id))inspect()});
 });
 window.FlowForgeDebugger={state,inspect,render,start,exportReport};
})();
