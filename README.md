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

## QR Code

O QR Code pode ser atualizado por JavaScript:

```js
qrcode1.textContent = "https://exemplo.com";
```

Isso permite gerar códigos dinamicamente, inclusive para URLs de streams de rádio.

## Exportação

A exportação transforma a estrutura do projeto em uma aplicação web executável, considerando páginas, componentes, hierarquia, eventos, JavaScript e assets.

Assets armazenados no projeto podem ser incorporados ao resultado final.

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
