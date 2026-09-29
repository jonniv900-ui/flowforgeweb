/* FlowForge Designer Viewport - restores real Mobile/Tablet/Desktop preview switching. */
(function(w,d){'use strict';
  const PRESETS={
    mobile:{width:390,height:844},
    tablet:{width:768,height:1024},
    desktop:{width:1440,height:900}
  };
  const byWidth={390:'mobile',768:'tablet',1200:'desktop',1440:'desktop'};
  const $=id=>d.getElementById(id);

  function presetName(width){return byWidth[Number(width)]||
    (Number(width)<768?'mobile':Number(width)<1200?'tablet':'desktop');}

  function apply(width,height,name){
    const stage=$('stage');
    if(!stage)return;
    width=Number(width)||390;
    const preset=PRESETS[name||presetName(width)];
    height=Number(height)||preset?.height||900;
    stage.style.width=Math.min(Math.max(width,280),1440)+'px';
    stage.style.minHeight=height+'px';
    stage.style.height=height+'px';
    stage.dataset.viewport=name||presetName(width);
    stage.classList.remove('ff-viewport-mobile','ff-viewport-tablet','ff-viewport-desktop');
    stage.classList.add('ff-viewport-'+(name||presetName(width)));
    const vp=$('viewport');
    if(vp){
      const value=String(width===1440?1200:width);
      const option=[...vp.options].find(o=>o.value===value);
      if(option)vp.value=value;
    }
    const dp=$('devicePreset');
    /* In "Designer" mode (empty value) keep the selector as is; the stage follows the Viewport select. */
    if(dp&&dp.value!=='')dp.value=(name||presetName(width))==='desktop'?'1440':String(width);
  }

  function applyPreset(key){
    const p=PRESETS[key];
    if(!p)return;
    apply(p.width,p.height,key);
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
          const width=Number($('viewport')?.value)||390;
          const key=presetName(width);
          apply(width,PRESETS[key]?.height||900,key);
          return;
        }
        const key=value==='390'?'mobile':value==='768'?'tablet':'desktop';
        applyPreset(key);
      });
    }
    if(vp&&!vp.dataset.ffViewportBound){
      vp.dataset.ffViewportBound='1';
      vp.addEventListener('change',function(){
        const width=Number(this.value)||390;
        const key=presetName(width);
        const p=PRESETS[key];
        apply(width,p?.height||900,key);
      });
    }
    applyCurrent();
  }

  function applyCurrent(){
    const stage=$('stage');
    if(!stage)return;
    const dp=$('devicePreset');
    const value=dp?.value;
    if(value==='390')return applyPreset('mobile');
    if(value==='768')return applyPreset('tablet');
    if(value==='1440')return applyPreset('desktop');
    const vp=$('viewport');
    if(vp?.value){
      const width=Number(vp.value);
      const key=presetName(width);
      apply(width,PRESETS[key]?.height||900,key);
    }
  }

  w.FFDesignerViewport={presets:PRESETS,apply,applyPreset,bind,applyCurrent};
  if(d.readyState==='loading')d.addEventListener('DOMContentLoaded',bind,{once:true});
  else bind();
})(window,document);
