// FlowForge WebStudio v0.8.1
['datagrid','chart','calendar','tabcontrol','drawer','bottomsheet','camera','qrcode','listview','treeview','statcard','rating','timeline','stepper','sidebar','toolbar','footer','fileupload','colorpicker','avatar'].forEach(kind=>{
 FlowForgeRegistry.register({kind,version:1,responsive:true,properties:window.FlowForgePropertySchemaFor?FlowForgePropertySchemaFor(kind):[]});
});

// TabControl: abas internas com painéis, teclado (setas/Home/End) e evento change.
FlowForgeRegistry.register({kind:'tabcontrol',version:2,responsive:true,event:'change',properties:window.FlowForgePropertySchemaFor?FlowForgePropertySchemaFor('tabcontrol'):[],defaults:{activeTab:0,tabs:[{label:'Geral',content:'Conteúdo da aba Geral.'},{label:'Detalhes',content:'Conteúdo da aba Detalhes.'},{label:'Histórico',content:'Conteúdo da aba Histórico.'}]}});

// Componentes Web reais: iframe, canvas, mapa e QR Code.
FlowForgeRegistry.register({kind:'iframe',version:2,responsive:true,properties:window.FlowForgePropertySchemaFor('iframe'),defaults:{src:'about:blank',lazy:true}});
FlowForgeRegistry.register({kind:'canvas',version:2,responsive:true,properties:window.FlowForgePropertySchemaFor('canvas'),defaults:{canvasWidth:300,canvasHeight:180,canvasBackground:'#ffffff'}});
FlowForgeRegistry.register({kind:'map',version:2,responsive:true,properties:window.FlowForgePropertySchemaFor('map'),defaults:{mapLat:0,mapLng:0,mapZoom:13}});
FlowForgeRegistry.register({kind:'qrcode',version:2,responsive:true,properties:window.FlowForgePropertySchemaFor('qrcode'),defaults:{qrcodeSize:160,textContent:'https://flowforge.local'}});
