/* FlowForge Designer Viewport
 * Single owner of the designer stage size (Mobile / Tablet / Desktop).
 * - Every UI control (Viewport select, device preset, "Recursos" panel) goes through apply().
 * - The chosen layout is stored in project.viewport, so it is saved in the .flowmobile file
 *   and restored whenever the project is rendered, opened, or created.
 */
(function(w,d){'use strict';
  const PRESETS={
    mobile:{width:390,height:844},
    tablet:{width:768,height:1024},
    desktop:{width:1440,height:900}
  };
  const MIN=280,MAX=1440;
  const $=id=>d.getElementById(id);
  const proj=()=>typeof project!=='undefined'?project:null;

  function presetName(width){
    width=Number(width);
    return width<768?'mobile':width<1200?'tablet':'desktop';
  }
  function defaults(type){return {width:type==='app'?390:1200,device:''};}
  function valid(v){
    const n=Number(v&&v.width);
    return Number.isFinite(n)&&n>=MIN&&n<=MAX;
  }
  /* Layout stored in the project (or the default for its type). */
  function current(){
    const p=proj();
    if(p&&valid(p.viewport))return {width:Number(p.viewport.width),device:String(p.viewport.device??'')};
    return defaults(p&&p.type);
  }
  const hasOption=(sel,value)=>!!sel&&[...sel.options].some(o=>o.value===value);

  function apply(width,height,name,opts){
    const stage=$('stage');
    if(!stage)return;
    width=Math.min(Math.max(Number(width)||390,MIN),MAX);
    const key=name||presetName(width);
    height=Number(height)||PRESETS[key]?.height||900;
    stage.style.width=width+'px';
    stage.style.minHeight=height+'px';
    stage.style.height=height+'px';
    stage.dataset.viewport=key;
    stage.classList.remove('ff-viewport-mobile','ff-viewport-tablet','ff-viewport-desktop');
    stage.classList.add('ff-viewport-'+key);
    const vp=$('viewport');
    if(vp){
      const value=String(width===1440?1200:width);
      if(hasOption(vp,value))vp.value=value;
    }
    const dp=$('devicePreset');
    /* Empty value = "Designer" (free mode): keep it, the stage follows the Viewport select. */
    if(dp&&dp.value!=='')dp.value=key==='desktop'?'1440':String(width);
    if(!(opts&&opts.persist===false)){
      const p=proj();
      if(p)p.viewport={width,device:dp?dp.value:''};
    }
    w.FFResponsive?.update?.();
  }

  function applyPreset(key){
    const p=PRESETS[key];
    if(!p)return;
    apply(p.width,p.height,key);
  }

  /* Re-apply the layout stored in the current project (called by render()). */
  function restore(){
    const s=current();
    const dp=$('devicePreset');
    if(dp&&hasOption(dp,s.device))dp.value=s.device;
    apply(s.width);
  }

  /* New project or project type change: go back to the default layout for that type. */
  function reset(type){
    const p=proj();
    if(p)p.viewport=defaults(type||p.type);
    restore();
  }

  function bind(){
    const dp=$('devicePreset');
    const vp=$('viewport');
    if(dp&&!dp.dataset.ffViewportBound){
      dp.dataset.ffViewportBound='1';
      dp.addEventListener('change',function(){
        const value=this.value;
        if(!value){
          /* Designer mode: follow the layout selected in the Viewport select. */
          apply(Number(vp?.value)||390);
          return;
        }
        applyPreset(value==='390'?'mobile':value==='768'?'tablet':'desktop');
      });
    }
    if(vp&&!vp.dataset.ffViewportBound){
      vp.dataset.ffViewportBound='1';
      vp.addEventListener('change',function(){apply(Number(this.value)||390);});
    }
    restore();
  }

  w.FFDesignerViewport={presets:PRESETS,apply,applyPreset,bind,restore,reset,current,applyCurrent:restore};
  if(d.readyState==='loading')d.addEventListener('DOMContentLoaded',bind,{once:true});
  else bind();
})(window,document);
