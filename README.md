# FlowForge WebStudio Beta

**FlowForge WebStudio** é um ambiente visual para criação de aplicações web, sites e landing pages usando componentes, páginas, eventos, JavaScript, dados e recursos locais.

> **Status:** Beta  
> **Formato de projeto:** `.flowmobile`  
> **Execução:** navegador / HTML5 + JavaScript

## Índice

- [Visão geral](#visão-geral)
- [Tipos de projeto](#tipos-de-projeto)
- [Componentes](#componentes)
- [Páginas e navegação](#páginas-e-navegação)
- [Eventos e JavaScript](#eventos-e-javascript)
- [OnLoad e OnShow](#onload-e-onshow)
- [ListBox e ComboBox](#listbox-e-combobox)
- [Áudio e vídeo](#áudio-e-vídeo)
- [Imagens e Assets](#imagens-e-assets)
- [HTTP](#http)
- [Database](#database)
- [Frameworks CSS](#frameworks-css)
- [Layout e responsividade](#layout-e-responsividade)
- [QR Code](#qr-code)
- [Exportação](#exportação)
- [Formato `.flowmobile`](#formato-flowmobile)
- [Arquitetura](#arquitetura)
- [Boas práticas](#boas-práticas)
- [Limitações](#limitações)

## Visão geral

O FlowForge WebStudio combina um designer visual com programação JavaScript. O usuário pode criar páginas, adicionar componentes, configurar propriedades, definir eventos, testar a aplicação e exportar o resultado para a Web.

A ideia central é:

```text
Designer visual + Componentes + Eventos + JavaScript + Dados + Assets
```

Projetos são armazenados no formato `.flowmobile`.

## Tipos de projeto

### App

Para aplicações web interativas com múltiplas telas, navegação, componentes, eventos, lógica JavaScript e layout responsivo.

### Site

Para sites institucionais e portais, com recursos como Header, Navbar, seções, cards e Footer.

### Landing Page

Para páginas de apresentação, produtos e serviços, com estruturas como Header, Hero, CTA, benefícios, cards e Footer.

## Componentes

O WebStudio possui componentes de interface, entrada, navegação, dados e visualização.

Exemplos:

- Button, Label, Link
- IconButton, GradientButton, FAB
- Image, Video, Audio, IFrame, Canvas
- Input, TextArea, CheckBox, Radio, Switch
- ComboBox, ListBox, ColorPicker, FileUpload
- Navbar, BottomNav, Tabs, TabControl, Drawer, Sidebar, Toolbar
- Pagination, PageNav
- List, ListView, MobileList, Table, DataGrid, TreeView
- Chart, Calendar, Rating, Timeline, Stepper, Accordion
- Modal, Toast, Tooltip, Carousel, QRCode
- Battery, Thermometer, LED, Sparkline
- ValueCard, StatusCard, StatCard, GlassPanel

### Toolbox traduzida

Os nomes das ferramentas e dos grupos da Toolbox seguem o idioma escolhido no seletor de idioma (pt-BR, English e Español). Por exemplo, `TextBox` aparece como **Caixa de texto** em português e **Cuadro de texto** em espanhol. Em inglês, os nomes técnicos de sempre são mantidos.

- Só o texto da Toolbox é traduzido. Nomes de componentes (`input1`, `button1`), o tipo (`input`), os eventos e o código gerado não mudam.
- A busca encontra pelo nome traduzido, pelo nome técnico original (`textbox`) e pelo nome do grupo, ignorando acentos.
- As traduções ficam em `js/ui-i18n-tools.js`, indexadas pelo tipo da ferramenta. Ao criar uma ferramenta nova no `TOOL_GROUPS`, adicione o nome em pt-BR e es nesse arquivo. O teste `/tests/toolbox_i18n_test.html` avisa se faltar alguma.

## Páginas e navegação

Um projeto pode possuir várias páginas, cada uma com seus componentes e configurações.

Exemplo:

```text
Home
Radios
Sobre
Contato
```

A navegação pode ser feita por componentes ou JavaScript:

```js
ffNavigate("Radios");
```

A navegação interna também utiliza hash/URL para permitir roteamento entre páginas.

### Header, navegação e footer automáticos

Projetos criados pelo assistente (e Site/Landing sem layout definido) recebem header, navegação e footer automáticos em todas as páginas. Esses blocos são marcados como `siteChrome` e acompanham as páginas e o framework CSS.

- Se a página já tem um **header ou footer próprio** e o projeto não tem layout do assistente (`siteLayout`), ela é tratada como de layout próprio e **não recebe chrome automático**. Chrome automático já gravado nesse tipo de projeto é removido ao abrir.
- Um header, footer ou navegação **inserido manualmente** impede que o automático do mesmo tipo seja recriado. Se o automático já existe e você acrescenta um manual, os dois permanecem (escolha explícita).
- Teste: `/tests/site_chrome_test.html`.

### Eventos `load` e `error` no HTML gerado

Os eventos de componentes viram atributos inline (`onclick="button1_click(event)"`). `load` e `error` podem disparar enquanto a página ainda está sendo lida (por exemplo um iframe `about:blank`), antes de o script com os handlers existir. Por isso eles são gerados protegidos: `onload="typeof iframe1_load==='function'&&iframe1_load(event)"`. Os demais eventos não mudam. Teste: `/tests/generated_events_test.html`.

## Eventos e JavaScript

Componentes possuem eventos que podem executar JavaScript.

Exemplos:

```js
label1.textContent = "Olá, FlowForge!";
```

```js
button1.visible = false;
```

```js
button1.enabled = false;
```

O editor de código permite trabalhar diretamente com a lógica dos eventos.

## OnLoad e OnShow

As páginas possuem eventos de ciclo de vida.

### OnLoad

Executado no carregamento inicial da página:

```js
async function Home_onload(event) {
    label1.textContent = "Aplicação carregada";
}
```

### OnShow

Executado quando a página é exibida:

```js
async function Home_onshow(event) {
    label1.textContent = "Página exibida";
}
```

Na primeira página, o fluxo é `OnLoad` seguido de `OnShow`. Nas navegações posteriores, `OnShow` acompanha a exibição da página.

Os eventos de página aparecem na área de Actions e seguem o mesmo conceito de edição dos eventos de componentes.

## ListBox e ComboBox

O `ListBox` trabalha com itens contendo texto e valor:

```js
radiosList.items = [
    { text: "Groove Salad", value: "groovesalad" },
    { text: "Drone Zone", value: "dronezone" }
];
```

Item selecionado:

```js
const item = radiosList.selectedItem;

if (item) {
    label1.textContent = item.text;
}
```

O item possui:

```text
text
value
index
```

Manipulação:

```js
radiosList.addItem("Nova rádio", "radio1");
radiosList.removeItem("radio1");
radiosList.clearItems();
```

## Áudio e vídeo

O FlowForge utiliza elementos HTML reais para áudio e vídeo.

Exemplo de rádio:

```js
audio1.src = "https://exemplo.com/stream";
audio1.load();
await audio1.play();
```

Pausa:

```js
audio1.pause();
```

Volume:

```js
audio1.volume = 0.5;
```

Áudio e vídeo suportam propriedades como `src`, `controls`, `autoplay`, `loop`, `muted`, `volume`, `poster` e `visible`, além de eventos de mídia.

## Imagens e Assets

Imagens locais podem ser armazenadas nos Assets do projeto.

A arquitetura utiliza referências de asset para evitar duplicação desnecessária de Base64 nos componentes:

```text
Imagem local
    ↓
Asset do projeto
    ↓
asset://id
    ↓
Preview
    ↓
Exportação
    ↓
Base64 no HTML final
```

Isso permite manter os projetos autocontidos.

## HTTP

O FlowForge possui serviços HTTP para consumo de APIs:

```js
await http.get(url);
await http.post(url, data);
await http.put(url, data);
await http.patch(url, data);
await http.delete(url);
await http.request(options);
```

O uso de APIs externas continua sujeito às regras do navegador, especialmente CORS.

## Database

O serviço `Database` utiliza armazenamento local baseado em IndexedDB.

Exemplos:

```js
await db.createTable("users");
```

```js
await db.insert("users", {
    name: "FlowForge"
});
```

```js
const users = await db.select("users");
```

Também estão disponíveis operações como:

```js
db.get()
db.update()
db.delete()
db.clear()
db.count()
db.dropTable()
```

O banco é local ao navegador e não é automaticamente um banco de servidor.

## Frameworks CSS

O WebStudio possui suporte visual para:

- Bootstrap 5.3
- Bulma
- Pico CSS
- Tailwind CSS
- Materialize CSS
- Foundation
- UIkit
- Semantic UI

O framework pode ser utilizado para visualização e estilo da aplicação, mantendo a estrutura de componentes do FlowForge.

### Interface traduzida

Além da Toolbox, todo o restante da interface do editor segue o idioma escolhido (pt-BR, English e Español): painel de propriedades e de ações, painel do projeto, gavetas (Árvore, Páginas, Assets), blocos, depurador, assistente de novo projeto, editor WYSIWYG, diálogos de salvar e exportar, dicas (tooltips) e mensagens de aviso.

- O nome do tipo do componente também é traduzido onde aparece: na Árvore (`Caixa de texto: input1`), nos seletores de alvo das ações e no título `Propriedades: Caixa de texto`.
- **Conteúdo do usuário nunca é traduzido**: nomes de componentes e de páginas, textos digitados nos campos, o conteúdo do editor WYSIWYG, o palco, o preview e o código gerado. Só textos que coincidem exatamente com uma entrada do dicionário são trocados, nunca trechos de frases.
- O dicionário fica em `js/ui-i18n-dom.js`. Cada entrada tem as três versões, no formato `['português', 'english', 'español']`. Um `{0}` marca uma parte dinâmica (por exemplo `'definir {0}'`), e a opção `scope` limita a entrada a um trecho da tela. O texto reconhecido pode estar em qualquer um dos três idiomas, então voltar ao português restaura tudo.
- Rótulos desenhados por CSS no palco (`duplo clique → ação`, `HIDDEN`, `DISABLED`) usam variáveis CSS atualizadas a cada troca de idioma.
- Ao criar um texto novo na interface, adicione a entrada no dicionário. O teste `/tests/ui_i18n_test.html` percorre os 110 componentes, os painéis e os diálogos nos três idiomas e avisa se algum texto conhecido aparecer no idioma errado.

## Layout e responsividade

O modo App possui recursos para interfaces responsivas e diferentes tamanhos de viewport.

O docking pode utilizar:

```text
none
top
bottom
left
right
fill
```

Exemplo conceitual:

```text
Header  -> top
Sidebar -> left
Content -> fill
Footer  -> bottom
```

Sempre teste o projeto em desktop, tablet e celular.

### Viewport do Designer

O tamanho do palco pode ser escolhido de três formas:

- **Viewport** (propriedades do projeto): Mobile 390, Tablet 768 ou Desktop 1200.
- **Largura × Altura** (propriedades do projeto): valores livres, de 280 a 1440 de largura e de 200 a 4000 de altura. O Viewport passa a mostrar *Outro*.
- **Seletor de dispositivo** (barra de ferramentas): *Livre* segue o Viewport / Largura × Altura; *Mobile*, *Tablet* e *Desktop* aplicam largura e altura de um dispositivo.

A escolha é salva no projeto (`project.viewport`, no arquivo `.flowmobile`) e restaurada ao reabrir. Projetos antigos, sem esse campo, usam 390 (App) ou 1200 (Site e Landing Page). Desfazer e refazer não alteram o viewport.

O módulo `js/ff-designer-viewport.js` (`FFDesignerViewport`) é o único responsável por esse tamanho. Os breakpoints do `FFResponsive` (mobile, tablet e desktop) são medidos sobre o palco, e não sobre a janela do navegador.

Para rodar o teste de regressão, inicie um servidor local na raiz do projeto (`python -m http.server`) e abra `/tests/viewport_test.html`.


## QR Code

O QR Code pode ser atualizado por JavaScript:

```js
qrcode1.textContent = "https://exemplo.com";
```

Isso permite gerar códigos dinamicamente, inclusive para URLs de streams de rádio.

## Exportação

A exportação transforma a estrutura do projeto em uma aplicação web executável, considerando páginas, componentes, hierarquia, eventos, JavaScript e assets.

Assets armazenados no projeto podem ser incorporados ao resultado final.

### Ícone e favicon

Tanto **Salvar** quanto **Exportar HTML** permitem definir o ícone do app (Apple Touch Icon) e o favicon. Os dois sempre ficam incorporados em **Base64**, dentro do `.flowmobile` e do `index.html` exportado, sem arquivos externos.

- **Escolher** abre um arquivo (PNG, JPEG, WEBP, GIF, SVG ou ICO). **Usar Asset** aproveita uma imagem dos Assets do projeto, que também é convertida em Base64. **Remover** limpa o campo.
- Imagens maiores que o necessário são reduzidas e gravadas como PNG: o ícone fica com no máximo 192 px e o favicon com no máximo 64 px, mantendo a proporção. Imagens pequenas são mantidas como estão. SVG e ICO são incorporados sem alteração (até 512 KB). O limite do arquivo escolhido é 5 MB.
- Cada campo mostra uma prévia, o formato, o tamanho e as dimensões. Um aviso aparece quando a imagem não é quadrada.
- No HTML exportado, o `<head>` recebe `<link rel="icon">`, `<link rel="apple-touch-icon">` e `<link rel="icon" sizes="192x192">`, com o `type` correto.
- Projetos antigos que usam um caminho (por exemplo `assets/icon-192.png`) ou um token `asset://` continuam funcionando. Escolha a imagem novamente para convertê-la em Base64.

Para rodar os testes de regressão, inicie um servidor local na raiz do projeto (`python -m http.server`) e abra `/tests/project_icons_test.html`, `/tests/viewport_test.html` ou `/tests/preview_assets_test.html`.


## Formato `.flowmobile`

Um projeto possui estrutura JSON. Entre as informações principais estão:

```text
version
name
projectVersion
icon
favicon
themeColor
type
framework
titlebar
pages
assets
```

As páginas armazenam seus componentes em `pages[].items`.

Componentes normalmente possuem propriedades como:

```text
id
kind
name
text
x
y
width
height
bg
color
visible
enabled
events
```

Componentes específicos podem possuir propriedades adicionais.

## Arquitetura

O FlowForge utiliza uma arquitetura modular. Funcionalidades específicas são mantidas em módulos separados sempre que possível, incluindo recursos relacionados a:

- responsividade;
- layout;
- estilos;
- componentes;
- data binding;
- debug;
- templates;
- enhancements;
- eventos de página;
- imagens/assets;
- HTTP;
- Database.

A separação reduz alterações desnecessárias no executor principal e facilita a evolução do WebStudio.

## Boas práticas

### Organize por páginas

Separe funcionalidades em páginas como:

```text
Home
Login
Dashboard
Configurações
Sobre
```

### Use nomes claros

Prefira:

```text
buttonLogin
labelStatus
radioList
audioPlayer
```

### Use Assets para recursos grandes

Evite repetir grandes strings Base64 diretamente em vários componentes.

### Use `await` em operações assíncronas

```js
const data = await http.get(url);
```

### Teste a responsividade

Verifique diferentes larguras e orientações antes da publicação.

## Limitações

O FlowForge WebStudio está em fase Beta.

Alguns recursos dependem do navegador, incluindo:

- reprodução automática de áudio/vídeo;
- CORS;
- APIs externas;
- armazenamento local;
- permissões do navegador.

A reprodução automática de mídia pode ser bloqueada até que o usuário interaja com a página.

Streams externos podem mudar ou ficar indisponíveis independentemente do FlowForge.

O banco local é específico do ambiente do navegador.

## Fluxo de criação

```text
Criar projeto
      ↓
Escolher App / Site / Landing Page
      ↓
Criar páginas
      ↓
Adicionar componentes
      ↓
Configurar propriedades
      ↓
Criar eventos
      ↓
Programar em JavaScript
      ↓
Executar e testar
      ↓
Exportar
```

## Princípios do projeto

1. **Visual primeiro** — a interface deve poder ser construída visualmente.
2. **Código quando necessário** — JavaScript amplia o comportamento da aplicação.
3. **Projetos autocontidos** — recursos locais devem permanecer no `.flowmobile` sempre que possível.
4. **Modularidade** — novas funcionalidades devem preferencialmente utilizar módulos independentes.
5. **Compatibilidade** — alterações no núcleo devem ser evitadas quando uma funcionalidade puder ser adicionada sem modificar o executor existente.
6. **Funcionalidade real** — componentes devem produzir comportamento funcional, e não apenas representação visual.

## Identidade

**Produto:** FlowForge WebStudio Beta  
**Projeto:** FlowForge WebStudio  
**Formato:** `.flowmobile`

> **Crie visualmente. Programe quando precisar. Exporte para a Web.**

## Licença

A licença do FlowForge  é a GPL 3.0.

## Site/Landing chrome automático
Ao selecionar **Site** ou **Landing Page**, o WebStudio cria automaticamente em cada página:
1. Header
2. Barra de navegação com botões para todas as páginas
3. Área de conteúdo
4. Footer abaixo do conteúdo

Ao selecionar **App HTML5**, esses componentes estruturais de navegação são removidos da estrutura automática; o App mantém apenas a Titlebar como estrutura global. Button e Link continuam disponíveis para navegação via `ffNavigate()`.


## Revisão dos exemplos

- Corrigidos: Adivinhe_o_Numero (campo não era limpo ao iniciar), Pong_IA (índice da raquete da CPU), Jogo_da_Memoria (seletor pegava outros componentes), Calculadora_Interativa (itens do combo), Dashboard_Sistema (histórico do sparkline) e cards usados como texto (sem o valor padrão "1.284").
- Gerador: cards atualizam o texto do rótulo, botões respeitam cores personalizadas, `switch` é um input real (funciona no modo escuro) e `sparkline` lê `data-values`.

### Exemplos novos

- **Lista_de_Tarefas**: criação de elementos pela página, filtro, contador e persistência em `localStorage`; carrega tudo no evento `OnLoad` da página.
- **Conversor_de_Unidades**: comprimento, massa, volume e temperatura; os combos De/Para são recriados ao trocar a categoria.
- **Quiz_de_Conhecimentos**: perguntas embaralhadas, ProgressBar, feedback de acerto/erro e recorde salvo.
- **Calculadoras_Multipagina**: IMC, gorjeta com divisão e juros compostos, com navegação por `ffNavigate`.
- **Pomodoro**: temporizador com pausa, reinício, três modos e contagem de sessões.
- **Jogo_da_Forca**: teclado A–Z, dicas por categoria e fim de jogo.

- **Editor_de_Texto**: Novo/Abrir/Salvar (.txt), localizar e substituir, ABC/abc/Aa, contagem de linhas/palavras/caracteres, tamanho da fonte, modo escuro e rascunho automático.

- **Editor_de_Texto_Blocos**: editor feito só com programação por blocos (definir propriedade, juntar texto, somar variável, repetir, se/senão, ir para página); sem código digitado.
Correção no gerador: o código do `OnLoad`/`OnShow` da página que contivesse `$&`, `$'` ou `` $` `` era corrompido na exportação (uso de `String.replace` com texto). Agora a inserção usa função. Teste: `/tests/generated_events_test.html`.

Observação: em projetos tipo app a TitleBar ocupa os primeiros 52 px da página, então os exemplos novos começam em y ≥ 56 e usam largura máxima de 390 px.

## Correção do componente Câmera

Por que a câmera "não funcionava" mesmo com o app publicado:

- Nada iniciava a câmera: o componente só abria o fluxo quando o código chamava `start`. Agora há um botão **Ativar câmera** no próprio componente (oculte com a propriedade *Ocultar botão Ativar câmera*) e a propriedade **autoplay** inicia a câmera automaticamente.
- Os erros eram silenciosos. Agora aparecem mensagens claras (permissão negada, sem câmera, câmera em uso, HTTPS ausente) e o evento `cameraerror` traz `error` e `message`.
- Se `facingMode` (frontal/traseira) for recusado, há fallback para qualquer câmera disponível.
- A câmera exige **HTTPS** (ou `localhost`). Em `http://` de um servidor, o navegador bloqueia `getUserMedia`.
- Se o app for embutido em um `iframe` de outra origem, use `allow="camera; microphone"`. O preview do IDE já faz isso.
- Se o servidor enviar o cabeçalho `Permissions-Policy: camera=()`, a câmera é bloqueada; use `camera=(self)`.

Testes: `tests/camera_test.html` (18 verificações).

Correções adicionais na câmera:

- Os eventos `camerastart`, `camerastop` e `cameraerror` agora executam as ações definidas pelo usuário (antes o atributo `oncamera…` era gerado, mas o navegador não o executava).
- `camerastop` só dispara quando havia uma câmera ligada; reiniciar a câmera (por exemplo, trocar frontal/traseira) não dispara `camerastop`.
- O bloco "iniciar câmera" não gera mais erro não tratado quando o acesso é negado; a mensagem aparece pelo evento `cameraerror`.
- Novo exemplo: `examples/Estudio_de_Camera.flowmobile` (ligar, desligar, trocar câmera, tirar foto, baixar, listar câmeras).

Depurador e exemplo da câmera:

- O painel do Depurador deixou de cobrir a parte de baixo do Preview/Design: agora ocupa uma linha própria abaixo da área de trabalho, e a barra de rolagem do projeto fica totalmente visível e utilizável com o Debug aberto.
- No exemplo `Estudio_de_Camera`, os botões Tirar foto e Trocar ficam sempre visíveis (antes só apareciam depois de a câmera ligar); o indicador "● AO VIVO" mostra/oculta pelos eventos `camerastart`/`camerastop`.

Permissões do Preview/Debug:

- O iframe do Preview e do Debug só recebe permissão de câmera (e microfone, se o componente usar áudio) quando o projeto possui um componente Câmera; permissão de localização só com componente Geolocalização. Sem esses componentes, nada é delegado nem solicitado.
- O navegador só pede acesso à câmera quando existe um componente Câmera no projeto e a câmera é iniciada (autoplay, botão Ativar câmera ou ação). Adicionar o componente no Design não pede permissão.

## Depurador melhorado

- **Captura desde o início:** o código de captura é injetado no começo do app em execução, então mensagens e erros do carregamento (onload etc.) também aparecem. Antes só eram registrados depois do carregamento.
- **Console:** hora real de cada mensagem (antes mostrava a hora da renderização), filtro por nível (Todos/Informações/Avisos/Erros), filtro de texto, botão **Copiar** e linha para **executar expressões JavaScript no app** (setas ↑↓ percorrem o histórico).
- **Erros:** mostram a origem quando vêm de um evento (ex.: `btnBad · click ↗`; clique para selecionar o componente no Design), detalhes da pilha, falhas de carregamento de recursos e Promises rejeitadas. A aba fica em vermelho com o contador.
- **Eventos:** click, dblclick, input (com o valor), change, submit e camerastart/camerastop/cameraerror; clique no nome do componente para destacá-lo no app.
- **Variáveis:** lista todas as variáveis globais criadas pelo projeto (não só nomes pré-definidos), atualiza sozinha e permite **editar o valor** (Enter).
- **Componentes:** nome, tipo, valor e visibilidade; clique para destacar no app ou selecionar no Design.
- **Rede (nova):** registra `fetch` e `XMLHttpRequest` com método, URL, status e tempo.
- **Painel:** redimensionável arrastando a borda superior; traduzido em português, inglês e espanhol.

## Novos exemplos e ferramentas Python

- Exemplos novos em `examples/`: **Cronometro_Voltas** (Iniciar/Pausar/Volta/Zerar, melhor e pior volta), **Controle_de_Gastos** (lançamentos por categoria, total e percentuais, salvos no navegador), **Foto_de_Perfil** (câmera + recorte quadrado + cartão em outra página, salvo no navegador) e **Laboratorio_do_Depurador** (botões que geram logs, avisos, erros, requisições e variáveis para explorar o Depurador).
- Pasta `tools/` (opcional, só para desenvolvimento): testes automatizados em Python/Playwright e os geradores dos exemplos. Veja `tools/README.md`. Rodar tudo: `python tools/run_all.py`.

## Exemplo Chess_Landing_Page funcional

- O tabuleiro demonstrativo virou um **jogo de xadrez completo**: regras oficiais (roque, en passant, promoção com escolha da peça, xeque, xeque-mate, afogamento, material insuficiente, regra dos 50 lances e repetição tripla), destaque do último lance e das casas possíveis, notação algébrica em português (R, D, T, B, C), peças capturadas, desfazer, girar o tabuleiro e salvamento automático da partida no navegador.
- Modos: contra o computador (fácil ou médio) ou dois jogadores.
- O motor foi validado por *perft* em 5 posições de referência (inicial, Kiwipete, posições 3, 4 e 5); os cenários estão em `tools/test_exemplos.py`. O código do jogo fica em `tools/gerar_exemplos/xadrez.js` e é gerado por `exemplo_11.py`.
- O conteúdo da landing page agora começa abaixo do cabeçalho/menu (antes o hero ficava por cima do cabeçalho).

Xadrez: modo Computador x Computador e relógio analógico:

- **Computador x Computador:** duas máquinas jogam sozinhas, com ritmo lento/normal/rápido, botão **Pausar/Continuar**, placar acumulado (brancas/empates/pretas) e opção de **nova partida automática** para um torneio contínuo. Há limite de 150 jogadas (empate).
- **Relógio de xadrez analógico:** um mostrador para cada lado, com ponteiros de hora e minuto, ponteiro de segundos, bandeirinha que sobe no último minuto e cai quando o tempo acaba. Tempos: 1, 3+2, 5, 5+3, 10, 15+10 e 30 minutos, ou *Sem limite (cronômetro)*, em que os ponteiros contam o tempo gasto. O lado da vez fica com o aro verde; clique em um relógio para pausar/continuar. O relógio começa a correr após o primeiro lance, aplica o incremento a cada lance, e Desfazer devolve o tempo anterior. Tempo esgotado = derrota (ou empate se o adversário não tem material para dar mate).
- Correção: a notação dos lances do computador mostrava desambiguação desnecessária (`Cb1c3`, `Ta1a8#`); agora aparece `Cc3`, `Ta8#`.
- O exemplo passou a ter cabeçalho e rodapé próprios (o rodapé automático ficava por cima do relógio).

Xadrez 3D com WebGL (`Xadrez_3D.flowmobile`):

- Mesmo jogo, motor, relógios analógicos e modo Computador x Computador do exemplo de xadrez, mas com **tabuleiro e peças em 3D desenhados com WebGL puro** (sem Three.js, sem imagens). O renderizador é `tools/gerar_exemplos/xadrez3d.js` e se encaixa no motor `xadrez.js` trocando `ffChess.draw` e `ffChess.click`.
- Peças torneadas (peão, torre, bispo, dama, rei) e cavalo extrudado; iluminação com brilho, sombras suaves, tabuleiro texturizado com coordenadas, destaque do último lance, da peça selecionada, dos destinos e do rei em xeque.
- Câmera orbital: **arraste** para girar, **roda do mouse** para o zoom; o botão Girar vira o tabuleiro suavemente para o lado das pretas. Clique nas peças ou casas (seleção por raio, correta em qualquer ângulo).
- Os lances são animados: a peça sobe e atravessa o tabuleiro, as capturas afundam, e o roque move rei e torre.
- Sem WebGL no navegador, o exemplo volta sozinho ao desenho 2D. Gere de novo com `python tools/gerar_exemplos/exemplo_11.py && python tools/gerar_exemplos/exemplo_12.py`.

## Empacotar para Android (APK)

O FlowForge roda só no navegador e não consegue compilar um APK sozinho (isso exige o Android SDK). Por isso o botão **APK**, na barra superior, gera no próprio navegador um pacote `.zip` pronto para virar APK, em três formatos:

- **Capacitor + build na nuvem:** projeto Capacitor com o app em `www/`, ícones, permissões, versão e orientação já configurados (`scripts/prepare-android.js`) e um workflow do GitHub Actions (`.github/workflows/build-apk.yml`) que compila o APK de teste sozinho. Inclui assinatura opcional (APK e AAB de release) por *secrets*. Também compila localmente com `npm install && npm run android:apk` (Node 22+, JDK 21 e Android SDK).
- **PWA + PWABuilder:** `index.html` com manifest, `sw.js` (funciona offline) e ícones (192, 512, *maskable* e Apple). Publique em HTTPS e gere o APK/AAB em pwabuilder.com.
- **Projeto Android Studio:** projeto nativo (Java) com um `WebView` que serve o app em `https://appassets.androidplatform.net`, para câmera, microfone e localização funcionarem como no navegador. Trata permissões em tempo de execução, envio de arquivos, botão voltar, links externos e tela cheia. Também traz o workflow do GitHub Actions.

Opções do diálogo: nome do app, ID do pacote (validado), versão e código da versão, orientação, tela cheia. As **permissões** são deduzidas dos componentes do projeto (câmera → `CAMERA`, e `RECORD_AUDIO` se a câmera captura áudio; localização → `ACCESS_FINE_LOCATION`/`ACCESS_COARSE_LOCATION`). O **ícone** vem do ícone do projeto (ou é gerado a partir do nome) e é convertido para todas as densidades, inclusive o ícone adaptativo. As opções ficam salvas no projeto (`project.android`). Cada pacote traz um `LEIA-ME.md` com o passo a passo.

Arquivos: `js/ff-android-export.js` (diálogo, ícones e gerador de `.zip` sem bibliotecas), `js/ff-android-templates.js` (modelos de texto, **gerado**) e os modelos editáveis em `tools/android_templates/`; depois de editar um modelo rode `python tools/gerar_android_templates.py`. Teste: `python tools/test_android.py`.

Importante: o FlowForge entrega o projeto, e o build do APK acontece no GitHub, no PWABuilder ou no Android Studio. A estrutura foi validada (XML, JSON, YAML, PNG, sintaxe do Java, `npx cap add android` + `prepare-android.js` + `cap sync`), mas a compilação final com o Android SDK não pôde ser executada no ambiente de desenvolvimento.
