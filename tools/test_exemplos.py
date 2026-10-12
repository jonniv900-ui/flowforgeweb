import sys,re,os
import common
EXOUT=os.environ.get('EXOUT',common.OUT+'/exemplos_html')
from playwright.sync_api import sync_playwright
ONLY=set(sys.argv[1:]); RES={}; ERRS_SEEN=[]
EXPECT={'Laboratorio_do_Depurador':'funcaoQueNaoExiste'}  # erro proposital do exemplo
FAST="""(()=>{const si=window.setInterval;window.setInterval=(f,ms,...a)=>si(f,Math.min(ms,4),...a);})()"""
def run(name,fn,fast=False,camera=False):
    if ONLY and name not in ONLY: return
    checks=[]
    def t(label,ok,detail=''): checks.append((label,bool(ok),str(detail)[:160]))
    with sync_playwright() as p:
        b=p.chromium.launch(args=['--use-fake-device-for-media-stream','--use-fake-ui-for-media-stream'] if camera else []); ctx=b.new_context(viewport={'width':1100,'height':900},permissions=['camera'] if camera else []); pg=ctx.new_page()
        global ERRS_SEEN
        errs=[]; dialogs=[]; ERRS_SEEN=errs
        pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.on('dialog',lambda d:(dialogs.append(d.message),d.accept()))
        pg.route('**/*',lambda r: r.continue_() if r.request.url.startswith(('file://','data:','about:','blob:')) else r.abort())
        if fast: pg.add_init_script(FAST)
        pg.goto(f'file://{EXOUT}/{name}.html'); pg.wait_for_timeout(500)
        pg.evaluate("window.__cards=[...document.querySelectorAll('.ff-real-card')].map(c=>(c.closest('[id]')||{}).id).filter(Boolean)")
        try: fn(pg,t,dialogs)
        except Exception as e: t('EXCEÇÃO no cenário',False,f'{type(e).__name__}: {str(e)[:120]}')
        errs=[e for e in errs if not (EXPECT.get(name) and EXPECT[name] in e)]
        t('sem erros de JavaScript durante o uso',not errs,'; '.join(sorted(set(errs)))[:150])
        b.close()
    RES[name]=checks
tx=lambda pg,i:pg.evaluate(f"(()=>{{const e=document.getElementById('{i}');if(!e)return '';if((window.__cards||[]).includes('{i}')){{const s=e.querySelector('small');return s?s.textContent.trim():'«estrutura do cartão perdida»'}}return e.textContent.trim()}})()")
def wait_txt(pg,i,pred,ms=4000):
    for _ in range(ms//50):
        v=tx(pg,i)
        if pred(v): return v
        pg.wait_for_timeout(50)
    return tx(pg,i)

def adivinhe(pg,t,d):
    pg.fill('#guessInput','50'); pg.click('#guessGo'); pg.wait_for_timeout(100)
    t('palpite digitado SEM clicar em "Novo jogo" é avaliado (não perdido)',re.search(r'maior|menor|Acertou',tx(pg,'guessStatus')),tx(pg,'guessStatus'))
    pg.click('#guessNew'); pg.evaluate("window.ffSecret=42")
    pg.fill('#guessInput','10'); pg.click('#guessGo'); t('palpite baixo → "É maior"','maior' in tx(pg,'guessStatus'),tx(pg,'guessStatus'))
    pg.fill('#guessInput','90'); pg.click('#guessGo'); t('palpite alto → "É menor"','menor' in tx(pg,'guessStatus'),tx(pg,'guessStatus'))
    pg.fill('#guessInput','abc'); pg.click('#guessGo'); t('texto inválido é rejeitado','entre 1 e 100' in tx(pg,'guessStatus'),tx(pg,'guessStatus'))
    pg.fill('#guessInput','42'); pg.click('#guessGo'); s=tx(pg,'guessStatus'); t('acerto mostra tentativas','Acertou' in s,s)
    t('concordância ("1 tentativa" no singular)',not re.search(r'em 1 tentativas',s),s)
run('Adivinhe_o_Numero',adivinhe)

def breakout(pg,t,d):
    pg.click('#breakStart'); pg.wait_for_timeout(300)
    b=tx(pg,'breakBoard'); t('tabuleiro desenhado (bola, tijolos e raquete)','●' in b and '■' in b and '═' in b,b[:40])
    s0=b; pg.wait_for_timeout(600); t('a bola se move',tx(pg,'breakBoard')!=s0 or 'Fim' in tx(pg,'breakStatus'))
    pg.wait_for_function("/Fim|venceu/.test(document.getElementById('breakStatus').textContent)",timeout=20000)
    t('o jogo termina com mensagem',re.search(r'Fim|venceu',tx(pg,'breakStatus')),tx(pg,'breakStatus'))
    pg.click('#breakStart'); t('reiniciar funciona',tx(pg,'breakStatus').startswith('Pontos'),tx(pg,'breakStatus'))
run('Breakout',breakout,fast=True)

def snake(pg,t,d):
    pg.click('#snakeStart'); pg.wait_for_timeout(60)
    h0=pg.evaluate("window.ffSnake.body[0].join(',')"); pg.wait_for_timeout(120)
    t('a cobra anda para a direita',pg.evaluate("window.ffSnake.body[0][0]")>int(h0.split(',')[0]) or 'Fim' in tx(pg,'snakeStatus'),h0)
    pg.click('#snakeStart'); pg.evaluate("clearInterval(window.ffSnakeTimer)")
    pg.evaluate("document.getElementById('snakeStart').click()")
    pg.wait_for_function("/Fim/.test(document.getElementById('snakeStatus').textContent)",timeout=8000)
    s=tx(pg,'snakeStatus'); t('bate na parede e mostra "Fim de jogo"','Fim de jogo' in s,s)
    t('comeu a comida padrão em [10,5] (pontos ≥ 1)',re.search(r'(\d+) pontos',s) and int(re.search(r'(\d+) pontos',s).group(1))>=1,s)
    pg.click('#snakeStart'); pg.evaluate("clearInterval(window.ffSnakeTimer)")
    pg.click('#snakeLeft'); t('Esquerda é ignorada quando já está indo para a direita (sem inverter)',pg.evaluate("window.ffSnake.dir.join(',')")=='1,0',pg.evaluate("window.ffSnake.dir.join(',')"))
    pg.click('#snakeUp'); t('Cima registra direção',pg.evaluate("window.ffSnake.dir.join(',')")=='0,-1')
    pg.click('#snakeDown'); t('Baixo é ignorado quando indo para cima',pg.evaluate("window.ffSnake.dir.join(',')")=='0,-1')
run('Snake',snake,fast=True)

def pong(pg,t,d):
    pg.click('#pongStart'); pg.wait_for_timeout(250)
    b=tx(pg,'pongBoard'); t('quadra desenhada com bola e as duas raquetes','●' in b and b.count('█')>=5,b[:30])
    pg.wait_for_timeout(4000)
    t('depois de ~1000 jogadas a quadra continua desenhada (sem travar)','●' in tx(pg,'pongBoard') or 'Fim' in tx(pg,'pongStatus'),tx(pg,'pongStatus'))
    for _ in range(6): pg.click('#pongUp')
    pg.wait_for_function("/Fim/.test(document.getElementById('pongStatus').textContent)",timeout=20000)
    t('afastando a raquete o jogo termina com "Fim — N rebatidas"',re.search(r'Fim — \d+ rebatidas',tx(pg,'pongStatus')),tx(pg,'pongStatus'))
    pg.click('#pongStart'); t('reiniciar funciona',tx(pg,'pongStatus').startswith('Rebatidas'),tx(pg,'pongStatus'))
    pg.click('#pongDown'); t('raquete do jogador responde aos botões',pg.evaluate("window.ffPong.p")>=1)
run('Pong_IA',pong,fast=True)

def genius(pg,t,d):
    pg.click('#simonStart'); v=wait_txt(pg,'simonStatus',lambda s:s=='Sua vez',4000); t('mostra a sequência e libera "Sua vez"',v=='Sua vez',v)
    for lvl in (1,2,3):
        seq=pg.evaluate("window.ffSimon.seq")
        for n in seq: pg.click(f'#s{n}'); pg.wait_for_timeout(30)
        v=tx(pg,'simonStatus'); t(f'nível {lvl}: sequência correta → "Certo!"',v=='Certo!',v)
        v=wait_txt(pg,'simonStatus',lambda s:s=='Sua vez',6000); t(f'nível {lvl+1}: nova rodada começa e libera "Sua vez"',v=='Sua vez',v)
        t(f'sequência cresce para {lvl+1}',pg.evaluate("window.ffSimon.seq.length")==lvl+1)
    seq=pg.evaluate("window.ffSimon.seq"); wrong=(seq[0]+1)%4; pg.click(f'#s{wrong}'); v=tx(pg,'simonStatus'); t('clique errado → "Errou!"',v.startswith('Errou'),v)
    pg.click('#simonStart'); v=wait_txt(pg,'simonStatus',lambda s:s=='Sua vez',4000); t('reiniciar volta ao nível 1',v=='Sua vez' and pg.evaluate("window.ffSimon.seq.length")==1,v)
    cols=pg.evaluate("[0,1,2,3].map(i=>{const e=document.getElementById('s'+i);const b=e.tagName==='BUTTON'?e:e.querySelector('button');return getComputedStyle(b).backgroundColor})")
    t('os 4 botões (o <button> que o usuário vê) têm cores diferentes',len(set(cols))==4,cols)
    t('as cores são as do exemplo (vermelho, verde, azul, amarelo), não o cinza padrão',all(c not in ('rgb(239, 239, 239)','rgba(0, 0, 0, 0)','rgb(255, 255, 255)') for c in cols),cols)
run('Genius_Simon',genius)

def memoria(pg,t,d):
    pg.click('#memNew'); pg.wait_for_timeout(100)
    t('título continua "Jogo da Memória"',tx(pg,'memTitle')=='Jogo da Memória',tx(pg,'memTitle'))
    t('botão "Novo jogo" continua com seu texto',tx(pg,'memNew')=='Novo jogo',tx(pg,'memNew'))
    vals=pg.evaluate("[...Array(8).keys()].map(i=>document.getElementById('m'+i).dataset.v)")
    from collections import Counter
    c=Counter(vals); t('8 cartas = 4 frutas, cada uma exatamente 2 vezes',len(c)==4 and all(v==2 for v in c.values()),vals)
    bidx=next(i for i in range(1,8) if vals[i]!=vals[0])
    pg.click('#m0'); pg.click(f'#m{bidx}')
    pg.wait_for_timeout(900); t('após 650 ms as cartas erradas voltam a "?"',tx(pg,'m0')=='?' and tx(pg,f'm{bidx}')=='?',(tx(pg,'m0'),tx(pg,f'm{bidx}')))
    done=set()
    for i in range(8):
        if i in done: continue
        j=next(k for k in range(i+1,8) if vals[k]==vals[i] and k not in done)
        pg.click(f'#m{i}'); pg.click(f'#m{j}'); done|={i,j}; pg.wait_for_timeout(40)
    v=tx(pg,'memStatus'); t('encontrar os 4 pares → "Você venceu!"',v=='Você venceu!',v)
run('Jogo_da_Memoria',memoria)

def velha(pg,t,d):
    pg.click('#c0'); pg.wait_for_timeout(150)
    cells=pg.evaluate("[...Array(9).keys()].map(i=>document.getElementById('c'+i).textContent.trim())")
    t('jogada do usuário (X) e resposta da IA (O)',cells[0]=='X' and cells.count('O')==1,cells)
    r=pg.evaluate("""async()=>{const out={win:0,loss:0,draw:0,stuck:0};
      for(let g=0;g<40;g++){document.getElementById('novoJogo').click();await new Promise(r=>setTimeout(r,5));
        for(let k=0;k<9;k++){const st=document.getElementById('status').textContent;if(/venceu|Empate/.test(st))break;
          const free=[...Array(9).keys()].filter(i=>!document.getElementById('c'+i).textContent.trim());if(!free.length)break;
          document.getElementById('c'+free[Math.floor(Math.random()*free.length)]).click();await new Promise(r=>setTimeout(r,3))}
        const s=document.getElementById('status').textContent;
        if(/Você venceu/.test(s))out.win++;else if(/IA venceu/.test(s))out.loss++;else if(/Empate/.test(s))out.draw++;else out.stuck++}
      return out}""")
    t('IA (minimax) nunca perde em 40 partidas aleatórias',r['win']==0,r)
    t('todas as partidas terminam em vitória da IA ou empate (nenhuma trava)',r['stuck']==0,r)
    pg.click('#novoJogo'); t('"Novo jogo" limpa o tabuleiro e o status',tx(pg,'status').startswith('Sua vez') and all(not tx(pg,f'c{i}') for i in range(9)),tx(pg,'status'))
run('Jogo_da_Velha_IA',velha)

def ppt(pg,t,d):
    ok=True; seen=set()
    for _ in range(30):
        for btn,p in (('rpsPedra','Pedra'),('rpsPapel','Papel'),('rpsTesoura','Tesoura')):
            pg.click('#'+btn); s=tx(pg,'rpsStatus'); m=re.match(r'Você: (\w+) \| IA: (\w+) — (.+)',s)
            if not m: ok=False; continue
            u,c,r=m.groups(); seen.add(r)
            win={('Pedra','Tesoura'),('Papel','Pedra'),('Tesoura','Papel')}
            exp='Empate' if u==c else ('Você venceu!' if (u,c) in win else 'IA venceu!')
            if r!=exp or u!=p: ok=False
    t('90 jogadas: resultado sempre coerente com as regras',ok)
    t('aparecem vitória, derrota e empate',len(seen)==3,seen)
run('Pedra_Papel_Tesoura_IA',ppt)

def reflexo(pg,t,d):
    pg.click('#reactBtn'); t('clicar antes de começar → "Queimou!"','Queimou' in tx(pg,'reactStatus'),tx(pg,'reactStatus'))
    pg.click('#reactStart'); t('começar → "Espere..."',tx(pg,'reactBtn')=='Espere...',tx(pg,'reactBtn'))
    pg.click('#reactBtn'); t('clicar cedo → "Queimou!"','Queimou' in tx(pg,'reactStatus'),tx(pg,'reactStatus'))
    pg.click('#reactStart'); v=wait_txt(pg,'reactBtn',lambda s:s=='CLIQUE!',5000); t('após 0,9–3,1 s o botão vira "CLIQUE!"',v=='CLIQUE!',v)
    pg.wait_for_timeout(120); pg.click('#reactBtn'); s=tx(pg,'reactStatus'); m=re.match(r'Seu tempo: (\d+) ms',s); t('mostra o tempo de reação',bool(m) and 80<=int(m.group(1))<=2500,s)
run('Teste_de_Reflexo',reflexo)

def calc(pg,t,d):
    opts=pg.evaluate("[...document.getElementById('op1').options].map(o=>o.value)")
    t('o seletor oferece Somar, Subtrair, Multiplicar e Dividir',opts==['Somar','Subtrair','Multiplicar','Dividir'],opts)
    def c(a,b,op):
        pg.fill('#num1',str(a)); pg.fill('#num2',str(b))
        pg.evaluate(f"(()=>{{const s=document.getElementById('op1');const o=[...s.options].find(x=>x.value==='{op}');if(o)s.value='{op}'}})()")
        pg.click('#calc1'); return tx(pg,'result1')
    for a,b,op,exp in [(6,3,'Somar','9'),(6,3,'Subtrair','3'),(6,3,'Multiplicar','18'),(6,3,'Dividir','2'),(6,0,'Dividir','Erro')]:
        r=c(a,b,op); t(f'{a} {op} {b} = {exp}',r=='Resultado: '+exp,r)
run('Calculadora_Interativa',calc)

def cadastro(pg,t,d):
    pg.click('#salvar1'); t('vazio → "Preencha nome e e-mail"',tx(pg,'status1')=='Preencha nome e e-mail',tx(pg,'status1'))
    pg.fill('#nome1','Ana'); pg.fill('#email1','ana@ex.com'); pg.click('#salvar1'); t('sem aceitar os termos → "Aceite os termos"',tx(pg,'status1')=='Aceite os termos',tx(pg,'status1'))
    pg.click('#termos1'); t('checkbox marca ao clicar',pg.evaluate("document.getElementById('termos1').checked"))
    pg.click('#salvar1'); t('completo → "Cadastro concluído: Ana"',tx(pg,'status1')=='Cadastro concluído: Ana',tx(pg,'status1'))
run('Cadastro_Usuario',cadastro)

def painel(pg,t,d):
    el=pg.evaluate("(()=>{const e=document.getElementById('dark1');return e?e.tagName+(e.type?':'+e.type:''):null})()"); t('a chave "Modo escuro" existe',el,el)
    bg0=pg.evaluate("getComputedStyle(document.body).backgroundColor")
    pg.click('label:has(#dark1), #dark1',force=True)
    pg.wait_for_timeout(150); bg1=pg.evaluate("getComputedStyle(document.body).backgroundColor")
    t('clicar na chave liga o modo escuro (fundo escuro e chave marcada)',bg1=='rgb(17, 24, 39)' and pg.evaluate("document.getElementById('dark1').checked"),(bg0,bg1))
    pg.click('label:has(#dark1), #dark1',force=True)
    pg.wait_for_timeout(150); t('clicar de novo desliga e volta ao fundo claro',pg.evaluate("getComputedStyle(document.body).backgroundColor")=='rgb(255, 255, 255)' and not pg.evaluate("document.getElementById('dark1').checked"),pg.evaluate("getComputedStyle(document.body).backgroundColor"))
    pg.evaluate("(()=>{const r=document.getElementById('volume1');r.value=80;r.dispatchEvent(new Event('input',{bubbles:true}))})()"); t('volume 80 → "Volume: 80%"',tx(pg,'volumeCard')=='Volume: 80%',tx(pg,'volumeCard'))
    pg.click('#notify1'); t('notificações ligadas',tx(pg,'status1')=='Notificações ativadas',tx(pg,'status1'))
    pg.click('#notify1'); t('notificações desligadas',tx(pg,'status1')=='Notificações desativadas',tx(pg,'status1'))
run('Painel_Configuracoes',painel)

def fileup(pg,t,d):
    pg.set_input_files('#fileUpload1',f'{common.TOOLS}/test_photo.png'); pg.wait_for_timeout(500)
    r=pg.evaluate("(()=>{const i=document.getElementById('picturebox1');return {tag:i&&i.tagName,src:(i&&i.getAttribute('src')||'').slice(0,5),w:i&&i.naturalWidth,alt:i&&i.alt}})()")
    t('a imagem escolhida aparece no PictureBox',r['src']=='blob:' and r['w']==120,r); t('o alt recebe o nome do arquivo',r['alt']=='test_photo.png',r)
    d.clear(); pg.set_input_files('#fileUpload1',f'{common.TOOLS}/test_file.txt'); pg.wait_for_timeout(300); t('arquivo que não é imagem mostra aviso',any('imagem' in x for x in d),d)
run('FileUpload_PictureBox',fileup)

def visual(pg,t,d):
    pg.set_input_files('#file1',f'{common.TOOLS}/test_photo.png'); pg.wait_for_timeout(500)
    t('imagem carregada e status atualizado','test_photo.png' in tx(pg,'status1') and pg.evaluate("document.getElementById('picturebox1').naturalWidth")==120,tx(pg,'status1'))
    pg.click('#picturebox1'); t('clicar na imagem mostra o nome',tx(pg,'status1')=='test_photo.png',tx(pg,'status1'))
    pg.click('#clear1'); t('"Limpar imagem" remove e restaura o status',tx(pg,'status1')=='Nenhuma imagem carregada' and not pg.evaluate("document.getElementById('picturebox1').getAttribute('src')"),tx(pg,'status1'))
run('Visualizador_de_Fotos',visual)

def dash(pg,t,d):
    pg.evaluate("(()=>{const r=document.getElementById('range1');r.value=73;r.dispatchEvent(new Event('input',{bubbles:true}))})()"); t('barra de CPU → "CPU: 73%"',tx(pg,'cpuCard')=='CPU: 73%',tx(pg,'cpuCard'))
    h0=pg.evaluate("document.querySelector('#sparkline1 canvas, canvas#sparkline1').toDataURL()")
    for v in (10,60,30,90,45):
        pg.evaluate(f"(()=>{{const r=document.getElementById('range1');r.value={v};r.dispatchEvent(new Event('input',{{bubbles:true}}))}})()"); pg.wait_for_timeout(30)
    h1=pg.evaluate("document.querySelector('#sparkline1 canvas, canvas#sparkline1').toDataURL()")
    t('o gráfico (sparkline) "Histórico CPU" é redesenhado a cada leitura',h1!=h0,len(h0))
    pg.click('#button1'); t('"Simular atualização" altera CPU e RAM',tx(pg,'cpuCard').startswith('CPU:') and tx(pg,'ramCard')!='RAM: 0%',(tx(pg,'cpuCard'),tx(pg,'ramCard')))
run('Dashboard_Sistema',dash)

def chess(pg,t,d):
    pg.click('#chessStart'); pg.wait_for_timeout(700)
    r=pg.evaluate("""(()=>{const c=document.getElementById('chessBoard');const ctx=c.getContext('2d');const d=ctx.getImageData(0,0,c.width,c.height).data;const cnt={};
      for(let i=0;i<d.length;i+=4*7){const k=d[i]+','+d[i+1]+','+d[i+2];cnt[k]=(cnt[k]||0)+1}
      const light=cnt['240,217,181']||0,dark=cnt['181,136,99']||0;const total=Object.values(cnt).reduce((a,b)=>a+b,0);
      return {w:c.width,h:c.height,light,dark,otherShare:Math.round(100*(total-light-dark)/total)}})()""")
    t('o canvas tem o tamanho do tabuleiro (≥ 400 px)',r['w']>=400,r)
    t('casas claras e escuras desenhadas',r['light']>50 and r['dark']>50,r)
    t('as 32 peças aparecem (pixels que não são casas)',r['otherShare']>=3,r)
run('Chess_Landing_Page',chess)

def pages_vis(pg): return pg.evaluate("[...document.querySelectorAll('.ff-page')].map(p=>!p.hidden&&!p.classList.contains('hidden'))")
def nav(pg,t,d,pages):
    v=pages_vis(pg); t('abre na primeira página',v[0] and sum(v)==1,v)
    for slug in pages[1:]+[pages[0]]:
        ok=pg.evaluate(f"ffNavigate('{slug}')"); pg.wait_for_timeout(60); v=pages_vis(pg)
        t(f'ffNavigate("{slug}") mostra só a página certa',ok and sum(v)==1 and v[pages.index(slug)],v)
def multi(pg,t,d):
    nav(pg,t,d,['home','produtos','contato'])
    pg.evaluate("ffNavigate('home')"); pg.click('#irProdutos'); pg.wait_for_timeout(100); v=pages_vis(pg); t('botão "Produtos" leva à página Produtos',v==[False,True,False],v)
    pg.click('#irContato'); pg.wait_for_timeout(100); v=pages_vis(pg); t('botão "Contato" leva à página Contato',v==[False,False,True],v)
    pg.click('#voltarHome'); pg.wait_for_timeout(100); v=pages_vis(pg); t('botão "Voltar" volta à Home',v==[True,False,False],v)
run('Site_Multipagina',multi)
def corp(pg,t,d):
    nav(pg,t,d,['home','sobre','servicos','contato'])
    pg.evaluate("ffNavigate('home')"); pg.click('#homeCta'); pg.wait_for_timeout(100); v=pages_vis(pg); t('"Conheça os serviços" → página Serviços',v==[False,False,True,False],v)
    pg.click('#servicosCta'); pg.wait_for_timeout(100); v=pages_vis(pg); t('"Fale conosco" → página Contato',v==[False,False,False,True],v)
    d.clear(); pg.click('#enviarContato'); t('"Enviar mensagem" mostra o aviso',any('enviada' in x for x in d),d)
run('Site_Corporativo_Exemplo',corp)
def saas(pg,t,d):
    y0=pg.evaluate("scrollY"); pg.click('#landingCta'); pg.wait_for_timeout(900)
    t('"Começar agora" rola até a seção de recursos',pg.evaluate("scrollY")>y0+100,pg.evaluate("scrollY"))
    d.clear(); pg.click('#finalCta'); t('"Quero experimentar" mostra o agradecimento',any('Obrigado' in x for x in d),d)
run('Landing_Page_SaaS_Exemplo',saas)
slugs=lambda pg:[s for s in pg.evaluate("window.__FLOWFORGE_PAGES__.map(p=>p.slug)")]
for n in ['FlowForge_Site_Header_Nav_Footer_Exemplo','FlowForge_Landing_Header_Nav_Footer_Exemplo','Landing_Page_Layout_Exemplo','Site_Landing_Pages_Layout_Exemplo']:
    run(n,lambda pg,t,d:nav(pg,t,d,slugs(pg)))

def todo(pg,t,d):
    cnt=lambda:tx(pg,'todoCount')
    t('começa vazio com mensagem',cnt()=='0 tarefas pendentes' and 'Nenhuma tarefa' in pg.inner_text('#todoList'),pg.inner_text('#todoList'))
    pg.click('#todoAdd'); t('adicionar vazio pede texto',cnt()=='Digite uma tarefa',cnt())
    pg.fill('#todoInput','Comprar pão'); pg.click('#todoAdd'); pg.fill('#todoInput','Estudar'); pg.press('#todoInput','Enter'); pg.fill('#todoInput','Correr'); pg.press('#todoInput','Enter')
    t('3 tarefas via botão e Enter',pg.locator('#todoList .todo-row').count()==3 and cnt()=='3 tarefas pendentes',cnt())
    t('campo é limpo após adicionar',pg.input_value('#todoInput')=='')
    pg.locator('#todoList .todo-row input').nth(0).check(); t('concluir reduz o contador',cnt()=='2 tarefas pendentes',cnt())
    pg.select_option('#todoFilter','Pendentes'); t('filtro Pendentes mostra 2',pg.locator('#todoList .todo-row').count()==2)
    pg.select_option('#todoFilter','Concluídas'); t('filtro Concluídas mostra 1',pg.locator('#todoList .todo-row').count()==1)
    pg.select_option('#todoFilter','Todas'); pg.click('#todoClear'); t('limpar concluídas remove 1',pg.locator('#todoList .todo-row').count()==2)
    pg.locator('#todoList .todo-del').first.click(); t('✕ remove a tarefa',pg.locator('#todoList .todo-row').count()==1 and cnt()=='1 tarefa pendente',cnt())
    pg.reload(); pg.wait_for_timeout(300); t('tarefas persistem após recarregar',pg.locator('#todoList .todo-row').count()==1 and 'Correr' in pg.inner_text('#todoList'),pg.inner_text('#todoList'))
run('Lista_de_Tarefas',todo)

def conv(pg,t,d):
    def go(cat,v,a,b):
        pg.select_option('#convCat',cat); pg.fill('#convValue',str(v)); pg.select_option('#convFrom',a); pg.select_option('#convTo',b); return tx(pg,'convResult')
    for args,exp in [(('Comprimento',1,'Quilômetro','Metro'),'1 Quilômetro = 1.000 Metro'),(('Comprimento',1,'Milha','Metro'),'1 Milha = 1.609,344 Metro'),(('Massa',2,'Quilograma','Libra'),'2 Quilograma = 4,409245 Libra'),(('Volume',1500,'Mililitro','Litro'),'1500 Mililitro = 1,5 Litro'),(('Temperatura',100,'Celsius','Fahrenheit'),'100 Celsius = 212 Fahrenheit'),(('Temperatura',32,'Fahrenheit','Kelvin'),'32 Fahrenheit = 273,15 Kelvin')]:
        r=go(*args); t(f'{args[1]} {args[2]} → {args[3]}',r==exp,r)
    pg.click('#convSwap'); t('Inverter troca De/Para e recalcula',pg.input_value('#convFrom')=='Kelvin' and 'Kelvin = ' in tx(pg,'convResult') and 'Fahrenheit' in tx(pg,'convResult').split('=')[1],tx(pg,'convResult'))
    pg.select_option('#convCat','Massa'); opts=pg.evaluate("[...document.getElementById('convFrom').options].map(o=>o.value)"); t('trocar categoria troca as unidades',opts[0]=='Quilograma' and 'Metro' not in opts,opts)
    pg.fill('#convValue','abc'); t('texto inválido → aviso',tx(pg,'convResult')=='Digite um número',tx(pg,'convResult'))
run('Conversor_de_Unidades',conv)

def quiz(pg,t,d):
    pg.wait_for_timeout(100)
    def correct(): return pg.evaluate("(()=>{const G=window.ffQuiz;return G.Q[G.order[G.i]].a})()")
    q0=tx(pg,'quizQuestion'); t('mostra a primeira pergunta',q0.startswith('1/8'),q0)
    t('botão Próxima e Jogar de novo ocultos no início',pg.evaluate("getComputedStyle(document.getElementById('quizNext').closest('.ff-component')).display")=='none' and pg.evaluate("getComputedStyle(document.getElementById('quizRestart').closest('.ff-component')).display")=='none')
    c=correct(); wrong=(c+1)%4; pg.click(f'#quizOpt{wrong}'); col=pg.evaluate(f"[document.getElementById('quizOpt{c}').style.background,document.getElementById('quizOpt{wrong}').style.background]")
    t('errar pinta certa de verde e errada de vermelho',col==['rgb(22, 163, 74)','rgb(220, 38, 38)'],col)
    t('após responder, as opções travam',pg.evaluate("document.getElementById('quizOpt0').disabled"))
    pg.click('#quizNext'); t('Próxima avança',tx(pg,'quizQuestion').startswith('2/8'),tx(pg,'quizQuestion'))
    for i in range(7):
        pg.click(f'#quizOpt{correct()}')
        if i<6: pg.click('#quizNext')
    e=tx(pg,'quizQuestion'); t('final mostra 7 de 8',('acertou 7 de 8' in e),e)
    t('Jogar de novo aparece e reinicia',pg.evaluate("getComputedStyle(document.getElementById('quizRestart').closest('.ff-component')).display")!='none')
    pg.click('#quizRestart'); t('reinicia na pergunta 1 com 0 acertos',tx(pg,'quizQuestion').startswith('1/8') and tx(pg,'quizScore')=='Acertos: 0',tx(pg,'quizScore'))
    pg.reload(); pg.wait_for_timeout(200)
    for i in range(8):
        pg.click(f'#quizOpt{correct()}')
        if i<7: pg.click('#quizNext')
    e=tx(pg,'quizQuestion'); t('perfeito mostra recorde 8',('Perfeito' in e and 'Recorde: 8' in e),e)
    w=pg.evaluate("document.querySelector('#quizBar i, #quizBar .ff-progress i').style.width"); t('barra de progresso chega a 100%',w=='100%',w)
run('Quiz_de_Conhecimentos',quiz)

def calcs(pg,t,d):
    nav(pg,t,d,['IMC','Gorjeta','Juros'])
    pg.evaluate("ffNavigate('imc')"); pg.fill('#imcPeso','70'); pg.fill('#imcAltura','1,75'); pg.click('#imcCalc')
    t('IMC 70kg/1,75m = 22,9 normal',tx(pg,'imcResult')=='IMC: 22,9' and tx(pg,'imcClass')=='Peso normal',(tx(pg,'imcResult'),tx(pg,'imcClass')))
    pg.fill('#imcPeso','100'); pg.fill('#imcAltura','175'); pg.click('#imcCalc'); t('altura em cm é aceita (100/175 = 32,7 obesidade I)',tx(pg,'imcResult')=='IMC: 32,7' and tx(pg,'imcClass')=='Obesidade grau I',(tx(pg,'imcResult'),tx(pg,'imcClass')))
    pg.fill('#imcPeso',''); pg.click('#imcCalc'); t('IMC vazio pede dados','Informe' in tx(pg,'imcResult'),tx(pg,'imcResult'))
    pg.click('#imcNavtip'); pg.wait_for_timeout(100); t('botão Gorjeta navega',pages_vis(pg)==[False,True,False],pages_vis(pg))
    pg.fill('#tipConta','200'); pg.select_option('#tipPct','10'); pg.fill('#tipPessoas','4'); pg.click('#tipCalc')
    t('gorjeta 10% de 200 = R$ 220,00 / 55,00 por pessoa',tx(pg,'tipResult')=='Total: R$ 220,00 (gorjeta R$ 20,00)' and tx(pg,'tipPerson')=='Por pessoa (4): R$ 55,00',(tx(pg,'tipResult'),tx(pg,'tipPerson')))
    pg.click('#tipNavinv'); pg.wait_for_timeout(100); t('botão Juros navega',pages_vis(pg)==[False,False,True],pages_vis(pg))
    pg.fill('#invCap','1000'); pg.fill('#invMes','0'); pg.fill('#invTaxa','1'); pg.fill('#invMeses','12'); pg.click('#invCalc')
    t('1000 a 1% por 12 meses = R$ 1126,83',tx(pg,'invResult')=='Montante: R$ 1126,83',tx(pg,'invResult'))
    pg.fill('#invMes','100'); pg.click('#invCalc'); t('com aporte 100/mês = R$ 2389,00 (juros R$ 189,00 sobre 2200)', 'Investido R$ 2200,00' in tx(pg,'invGain'),(tx(pg,'invResult'),tx(pg,'invGain')))
    pg.click('#invNavimc'); pg.wait_for_timeout(100); t('botão IMC volta',pages_vis(pg)==[True,False,False],pages_vis(pg))
run('Calculadoras_Multipagina',calcs)

def pomo(pg,t,d):
    T=lambda:tx(pg,'pomoTime')
    t('começa em 25:00',T()=='25:00',T())
    pg.click('#pomoShort'); t('Pausa 5 → 05:00',T()=='05:00',T())
    pg.click('#pomoFocus'); pg.click('#pomoStart'); t('Iniciar vira Pausar',tx(pg,'pomoStart')=='Pausar',tx(pg,'pomoStart'))
    pg.wait_for_timeout(500); v=T(); t('contagem regressiva anda (<25:00)',v!='25:00',v)
    pg.click('#pomoStart'); a=T(); pg.wait_for_timeout(150); t('pausar para o relógio',T()==a and tx(pg,'pomoStart')=='Continuar',(a,T()))
    pg.click('#pomoReset'); t('reiniciar volta a 25:00',T()=='25:00',T())
    pg.evaluate("(()=>{const M=window.ffPomo;M.stop();M.left=3;M.draw()})()"); pg.click('#pomoStart'); pg.wait_for_timeout(400)
    t('ao zerar conta sessão e avisa',T()=='00:00' and 'concluído' in tx(pg,'pomoMode') and 'concluídas: 1' in tx(pg,'pomoSessions'),(T(),tx(pg,'pomoMode'),tx(pg,'pomoSessions')))
    w=pg.evaluate("document.querySelector('#pomoBar i').style.width"); t('barra em 100% ao concluir',w=='100%',w)
run('Pomodoro',pomo,fast=True)

def forca(pg,t,d):
    pg.click('#forcaNew'); w=pg.evaluate("window.ffForca.word"); t('Novo jogo sorteia uma palavra',len(w)>=6 and '_' in tx(pg,'forcaWord'),tx(pg,'forcaWord'))
    notin=[l for l in 'ZXKQWY' if l not in w][:2]
    pg.click(f'#forca{notin[0]}'); t('letra errada conta erro',pg.evaluate("window.ffForca.miss")==1 and 'Erros: 1/6' in tx(pg,'forcaInfo'),tx(pg,'forcaInfo'))
    t('letra usada fica desabilitada',pg.evaluate(f"document.getElementById('forca{notin[0]}').disabled"))
    for l in dict.fromkeys(w): pg.click(f'#forca{l}')
    t('acertar todas → venceu','venceu' in tx(pg,'forcaStatus') and '_' not in tx(pg,'forcaWord'),(tx(pg,'forcaStatus'),tx(pg,'forcaWord')))
    t('após vencer as letras travam',pg.evaluate("document.getElementById('forcaA').disabled"))
    pg.click('#forcaNew'); w=pg.evaluate("window.ffForca.word"); errs=[l for l in 'QWXZKYJHUVBCDFGPMN' if l not in w][:6]
    for l in errs: pg.click(f'#forca{l}')
    t('6 erros → fim de jogo revela a palavra',('Fim de jogo' in tx(pg,'forcaStatus') and w in tx(pg,'forcaStatus') and w in tx(pg,'forcaWord').replace(' ','')),(tx(pg,'forcaStatus'),tx(pg,'forcaWord')))
    t('rosto final 💀',tx(pg,'forcaFace')=='💀',tx(pg,'forcaFace'))
run('Jogo_da_Forca',forca)

def editor(pg,t,d):
    st=lambda:tx(pg,'edStatus'); stats=lambda:tx(pg,'edStats')
    t('começa pronto e vazio',st()=='Pronto' and stats()=='Linhas 0 · Palavras 0 · Caracteres 0',(st(),stats()))
    pg.fill('#edText','Olá mundo\nsegunda linha com mundo'); t('estatísticas: 2 linhas, 6 palavras',stats().startswith('Linhas 2 · Palavras 6'),stats()); t('aviso de alterações não salvas','não salvas' in st(),st())
    pg.fill('#edFind','MUNDO'); pg.click('#edNext'); sel=pg.evaluate("(()=>{const t=document.getElementById('edText');return t.value.slice(t.selectionStart,t.selectionEnd)})()"); t('localizar ignora maiúsculas e seleciona',sel=='mundo',sel)
    pg.click('#edNext'); p2=pg.evaluate("document.getElementById('edText').selectionStart"); t('próximo vai à segunda ocorrência',p2>10,p2)
    pg.click('#edNext'); t('terceiro clique volta ao início',pg.evaluate("document.getElementById('edText').selectionStart")==4 and 'início' in st(),st())
    pg.fill('#edFind','xyz'); pg.click('#edNext'); t('não encontrado avisa','Não encontrado' in st(),st())
    pg.fill('#edFind','mundo'); pg.fill('#edRepl','Brasil'); pg.click('#edReplAll'); v=pg.input_value('#edText'); t('substituir tudo (2)',v=='Olá Brasil\nsegunda linha com Brasil' and '2 substituição' in st(),(v,st()))
    pg.fill('#edFind','.*'); pg.fill('#edRepl','!'); pg.click('#edReplAll'); t('caracteres especiais de regex tratados como texto','0 substituição' in st(),st())
    pg.fill('#edText','um dois três'); pg.click('#edUp'); t('ABC maiúsculas',pg.input_value('#edText')=='UM DOIS TRÊS',pg.input_value('#edText'))
    pg.click('#edLow'); t('abc minúsculas',pg.input_value('#edText')=='um dois três')
    pg.click('#edCap'); t('Aa capitaliza frases',pg.input_value('#edText')=='Um dois três',pg.input_value('#edText'))
    pg.evaluate("(()=>{const x=document.getElementById('edText');x.focus();x.setSelectionRange(3,7)})()"); pg.click('#edUp'); t('maiúsculas só na seleção',pg.input_value('#edText')=='Um DOIS três',pg.input_value('#edText'))
    pg.select_option('#edSize','Grande'); fs=pg.evaluate("getComputedStyle(document.getElementById('edText')).fontSize"); t('fonte Grande = 20px',fs=='20px',fs)
    pg.click('label:has(#edDark), #edDark',force=True); bg=pg.evaluate("getComputedStyle(document.getElementById('edText')).backgroundColor"); t('modo escuro escurece o editor',bg=='rgb(17, 24, 39)',bg)
    pg.fill('#edName','nota'); 
    with pg.expect_download() as dl: pg.click('#edSave')
    dw=dl.value; path=dw.path(); t('Salvar baixa nota.txt com o conteúdo',dw.suggested_filename=='nota.txt' and open(path,encoding='utf-8').read()=='Um DOIS três',(dw.suggested_filename,))
    t('após salvar mostra "Salvo como"','Salvo como nota.txt'==st(),st())
    pg.reload(); pg.wait_for_timeout(300); t('rascunho é restaurado ao recarregar',pg.input_value('#edText')=='Um DOIS três' and pg.input_value('#edName')=='nota.txt' and 'restaurado' in st(),(pg.input_value('#edText'),st()))
    t('tema escuro e fonte restaurados',pg.evaluate("getComputedStyle(document.getElementById('edText')).backgroundColor")=='rgb(17, 24, 39)' and pg.evaluate("getComputedStyle(document.getElementById('edText')).fontSize")=='20px')
    open(f'{common.TOOLS}/open_test.txt','w',encoding='utf-8').write('linha A\nlinha B\nlinha C'); d.clear()
    pg.set_input_files('#edOpen',f'{common.TOOLS}/open_test.txt'); pg.wait_for_timeout(300)
    t('Abrir carrega o arquivo (com confirmação por haver rascunho)',pg.input_value('#edText')=='linha A\nlinha B\nlinha C' and pg.input_value('#edName')=='open_test.txt' and stats().startswith('Linhas 3 · Palavras 6'),(pg.input_value('#edText'),stats()))
    d.clear(); pg.fill('#edText','x'); pg.click('#edNew'); t('Novo com alterações pergunta e limpa',any('Descartar' in x for x in d) and pg.input_value('#edText')=='',d)
run('Editor_de_Texto',editor)

def editorblocos(pg,t,d):
    v=lambda:pg.input_value('#texto')
    pg.fill('#texto','Olá'); pg.click('#btnItem'); t('• Item acrescenta ao texto',v()=='Olá\n• ',repr(v()))
    t('Desfazer guarda cópia antes da alteração',pg.input_value('#rascunho')=='Olá')
    pg.click('#btnTarefa'); pg.click('#btnTitulo'); pg.click('#btnPar'); pg.click('#btnLinha'); pg.click('#btnAssina')
    t('tarefa, título, parágrafo, nova linha e assinatura',v().endswith('☐ \n# \n\n\n\n\n— Escrito com FlowForge'),repr(v()))
    pg.click('#btnSep'); t('Separador repete ─ 20 vezes',v().endswith('─'*20) and not v().endswith('─'*21),v()[-25:])
    t('contador de ações via variável',tx(pg,'acoesLabel')=='Ações no texto: 7',tx(pg,'acoesLabel'))
    t('status da última ação',tx(pg,'status')=='Separador inserido',tx(pg,'status'))
    pg.click('#btnDesfazer'); t('Desfazer remove o separador',not v().endswith('─') and v().endswith('Escrito com FlowForge'),v()[-30:])
    t('status do desfazer',tx(pg,'status')=='Última alteração desfeita')
    for _ in range(3): pg.click('#btnItem')
    t('se/senão: acima de 9 ações muda a mensagem','Muitas alterações' in tx(pg,'status'),tx(pg,'status'))
    pg.click('#btnLimpar'); t('Limpar zera o texto',v()=='' and 'Desfazer restaura' in tx(pg,'status'))
    pg.click('#btnDesfazer'); t('Desfazer restaura o texto limpo',len(v())>40,len(v()))
    pg.click('#btnTrava'); t('Travar desabilita a caixa',pg.evaluate("document.getElementById('texto').disabled") is True and 'travado' in tx(pg,'status'),tx(pg,'status'))
    pg.click('#btnTrava'); t('clicar de novo libera',pg.evaluate("document.getElementById('texto').disabled") is False and 'liberada' in tx(pg,'status'),tx(pg,'status'))
    pg.click('#btnSobre'); pg.wait_for_timeout(100); t('Sobre navega para a página 2',pages_vis(pg)==[False,True],pages_vis(pg))
    pg.click('#btnVoltar'); pg.wait_for_timeout(100); t('Voltar retorna ao editor',pages_vis(pg)==[True,False],pages_vis(pg))
run('Editor_de_Texto_Blocos',editorblocos)


def cronometro(pg,t,d):
    g=lambda i:tx(pg,i)
    t('começa zerado','00:00.00' in g('swTime') and 'Iniciar' in g('swStart'),g('swTime'))
    t('Volta e Zerar começam desabilitados',pg.evaluate("document.getElementById('swLap').disabled&&document.getElementById('swReset').disabled"))
    pg.click('#swStart'); pg.wait_for_timeout(700)
    ms=lambda s:int(s[:2])*60000+int(s[3:5])*1000+int(s[6:8])*10
    v1=ms(g('swTime')); t('avança com o tempo (≈0,7 s)',400<=v1<=1500,g('swTime'))
    t('botão vira Pausar',g('swStart')=='Pausar')
    pg.click('#swLap'); pg.wait_for_timeout(300); pg.click('#swLap'); pg.wait_for_timeout(300); pg.click('#swLap'); pg.wait_for_timeout(100)
    laps=pg.input_value('#swLaps'); t('3 voltas registradas, a mais recente primeiro','Volta 3' in laps.split('\n')[0] and laps.count('Volta')==3,laps)
    t('marca melhor e pior volta com 3+ voltas','melhor' in laps and 'pior' in laps,laps)
    t('resumo mostra contagem, melhor e média','Voltas: 3' in g('swInfo') and 'média' in g('swInfo'),g('swInfo'))
    pg.click('#swStart'); a=g('swTime'); pg.wait_for_timeout(400); t('Pausar congela o tempo',g('swTime')==a and 'Continuar' in g('swStart'),(a,g('swTime')))
    pg.click('#swStart'); pg.wait_for_timeout(300); t('Continuar retoma de onde parou',ms(g('swTime'))>ms(a))
    pg.click('#swStart'); pg.click('#swReset'); t('Zerar limpa tempo e voltas','00:00.00' in g('swTime') and pg.input_value('#swLaps')=='' and 'Iniciar' in g('swStart'))
run('Cronometro_Voltas',cronometro)

def gastos(pg,t,d):
    g=lambda i:tx(pg,i)
    add=lambda desc,val,cat=None:(pg.fill('#gDesc',desc),pg.fill('#gValor',val),cat and pg.select_option('#gCat',cat),pg.click('#gAdd'))
    pg.click('#gAdd'); t('sem descrição é rejeitado','Descreva' in g('gMsg'),g('gMsg'))
    pg.fill('#gDesc','Almoço'); pg.click('#gAdd'); t('sem valor é rejeitado','valor' in g('gMsg'),g('gMsg'))
    pg.fill('#gValor','-5'); pg.click('#gAdd'); t('valor negativo é rejeitado','maior que zero' in g('gMsg'),g('gMsg'))
    add('Almoço','35,50','Alimentação'); add('Ônibus','4,80','Transporte'); add('Cinema','1200','Lazer')
    t('total com vírgula decimal e milhar','Total: R$ 1.240,30' in g('gTotal'),g('gTotal'))
    t('contagem no singular/plural','3 lançamentos' in g('gCount'),g('gCount'))
    t('lista com o mais novo primeiro','Cinema' in pg.input_value('#gList').split('\n')[0],pg.input_value('#gList'))
    t('percentual por categoria (Lazer 97%)','Lazer 97%' in g('gCats'),g('gCats'))
    pg.fill('#gDesc','Café'); pg.fill('#gValor','3'); pg.press('#gValor','Enter'); t('Enter no valor adiciona',g('gCount').startswith('4'),g('gCount'))
    pg.click('#gUndo'); t('Desfazer remove o último',g('gCount').startswith('3') and 'Removido: Café' in g('gMsg'),g('gMsg'))
    pg.reload(); pg.wait_for_timeout(400); t('dados persistem após recarregar (localStorage)',g('gCount').startswith('3') and 'R$ 1.240,30' in g('gTotal'),g('gTotal'))
    pg.click('#gClear'); pg.wait_for_timeout(200); t('Limpar tudo (confirmado) zera',g('gCount').startswith('0') and 'R$ 0,00' in g('gTotal'),g('gTotal'))
run('Controle_de_Gastos',gastos)

def perfil(pg,t,d):
    g=lambda i:tx(pg,i)
    vis=lambda i:pg.evaluate(f"(()=>{{const e=document.getElementById('{i}');return !!e&&getComputedStyle(e.closest('.ff-component')||e).display!=='none'&&e.offsetParent!==null}})()")
    t('sem botão interno da câmera',pg.evaluate("!document.querySelector('.ff-cam-ui')"))
    pg.click('#pfShot'); t('foto sem câmera avisa','Ligue a câmera' in g('pfMsg'),g('pfMsg'))
    pg.click('#pfOn'); pg.wait_for_timeout(1500); t('Ligar abre a câmera (evento camerastart no app)','Câmera ligada' in g('pfMsg') and pg.evaluate("document.getElementById('pfCam').videoWidth")>0,g('pfMsg'))
    pg.click('#pfShot'); pg.wait_for_timeout(700); t('foto quadrada recortada aparece na prévia',pg.evaluate("document.getElementById('pfPreview').src.startsWith('data:image/jpeg')"),g('pfMsg'))
    pg.click('#pfSave'); t('salvar sem nome é rejeitado','nome' in g('pfMsg'),g('pfMsg'))
    pg.fill('#pfNome','Ana Souza'); pg.click('#pfSave'); pg.wait_for_timeout(400)
    t('Salvar leva ao Cartão e para a câmera',vis('cardNome') and not vis('pfCam') and pg.evaluate("!document.getElementById('pfCam').srcObject"))
    t('cartão mostra nome e foto','Ana Souza' in g('cardNome') and pg.evaluate("document.getElementById('cardFoto').src.startsWith('data:image/jpeg')"))
    pg.reload(); pg.wait_for_timeout(500)
    pg.evaluate("window.ffPerfil&&1"); pg.click('#pfNome') if vis('pfNome') else None
    t('perfil persiste após recarregar',pg.evaluate("JSON.parse(localStorage.getItem('ffPerfilV1')||'{}').nome")=='Ana Souza')
    t('campo nome é preenchido na volta',pg.input_value('#pfNome')=='Ana Souza',pg.input_value('#pfNome'))
run('Foto_de_Perfil',perfil,camera=True)

def depurador(pg,t,d):
    g=lambda i:tx(pg,i)
    pg.click('#dbLog'); t('console.log atualiza a variável e a mensagem','ffDemo.n = 1' in g('dbOut'),g('dbOut'))
    pg.click('#dbVar'); pg.click('#dbVar'); t('Criar variáveis soma pontos','pontos = 20' in g('dbOut'),g('dbOut'))
    t('variável global usuario criada',pg.evaluate("window.usuario&&window.usuario.nome")=='Ana')
    pg.fill('#dbInput','abc'); t('input grava a última digitação',pg.evaluate("window.ultimoTexto")=='abc')
    pg.click('#dbNet'); pg.wait_for_timeout(400); t('fetch inexistente é tratado (sem quebrar)','Falhou' in g('dbOut') or 'Status' in g('dbOut'),g('dbOut'))
    pg.click('#dbWarn'); t('aviso enviado','Aviso' in g('dbOut'))
    pg.click('#dbErr'); pg.wait_for_timeout(200); t('"Gerar erro" lança ReferenceError (capturado em window.onerror)',any('funcaoQueNaoExiste' in e for e in ERRS_SEEN),ERRS_SEEN[:1])
run('Laboratorio_do_Depurador',depurador)

bad=0; tot=0
for name,checks in RES.items():
    fails=[c for c in checks if not c[1]]; tot+=len(checks); bad+=len(fails)
    print(f"{'✗' if fails else '✓'} {name:46s} {len(checks)-len(fails)}/{len(checks)}")
    for l,ok,dt in fails: print(f"      FALHA: {l}  → {dt}")
print(f"\nTOTAL: {tot-bad}/{tot} verificações OK | exemplos com falha: {sum(1 for c in RES.values() if any(not x[1] for x in c))}/{len(RES)}")
sys.exit(1 if bad else 0)
