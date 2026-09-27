/* FlowForge Responsive System - additive module. Does not replace the legacy designer. */
(function(w){'use strict';
  const bp={mobile:0,tablet:768,desktop:1200};
  const listeners=new Set(); let current='desktop';
  function detect(width){if(width<bp.tablet)return'mobile';if(width<bp.desktop)return'tablet';return'desktop'}
  function update(){const next=detect(w.innerWidth||1200);if(next===current)return;const prev=current;current=next;document.documentElement.dataset.ffBreakpoint=current;listeners.forEach(fn=>{try{fn(current,prev)}catch(e){}})}
  function observe(fn){if(typeof fn!=='function')return()=>{};listeners.add(fn);fn(current,null);return()=>listeners.delete(fn)}
  function variant(obj, fallback){return obj&&obj[current]!==undefined?obj[current]:fallback}
  function apply(el, cfg){if(!el||!cfg)return el;const v=variant(cfg,{});Object.keys(v||{}).forEach(k=>{if(k==='style'&&v.style)Object.assign(el.style,v.style);else if(k==='className')el.className=v.className;else if(k in el)try{el[k]=v[k]}catch(e){}else el.dataset[k]=v[k]});return el}
  w.FFResponsive={breakpoints:Object.freeze(bp),get current(){return current},detect,observe,variant,apply,setBreakpoints(next){Object.assign(bp,next||{});update()}};
  w.addEventListener('resize',update,{passive:true});
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',update,{once:true});else update();
})(window);
