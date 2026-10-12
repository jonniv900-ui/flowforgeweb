# Ferramentas de teste e geração (Python)

Scripts opcionais para desenvolvedores do FlowForge WebStudio. O IDE em si continua 100% estático (HTML/JS); nada aqui é necessário para usá-lo.

## Requisitos

```bash
pip install playwright
playwright install chromium
```

Testado em Linux/macOS (Python 3.10+). Todos os scripts iniciam sozinhos um servidor local na raiz do projeto — não é preciso subir nada antes.

## Testes

| Script | O que faz |
|---|---|
| `python tools/run_all.py` | Roda tudo abaixo e mostra um resumo |
| `python tools/run_suites.py [nome...]` | Suítes HTML de `tests/` (idiomas, ícones, viewport, câmera, eventos…) |
| `python tools/export_examples.py` | Exporta todos os `examples/*.flowmobile` para `tools/_out/exemplos_html/` |
| `python tools/test_exemplos.py [Exemplo...]` | Cenários de uso de cada exemplo (cliques, digitação, persistência…) |
| `python tools/test_camera.py` | Exemplo Estúdio de Câmera com câmera simulada do Chromium e com permissão negada |
| `python tools/test_permissoes.py` | Garante que a câmera só é pedida quando o projeto tem componente Câmera |
| `python tools/test_depurador.py` | Depurador: console, erros, eventos, variáveis, rede, REPL, redimensionamento |

Os scripts retornam código de saída diferente de zero em caso de falha (úteis em CI). Capturas de tela e HTML gerados ficam em `tools/_out/`.

## Geração dos exemplos

`tools/gerar_exemplos/exemplo_NN.py` são os programas que geraram os arquivos de `examples/`. `lib.py` traz as funções auxiliares (`it`, `proj`, `save`). Para gerar de novo:

```bash
python tools/gerar_exemplos/exemplo_10.py   # grava examples/*.flowmobile
```

Observações: `exemplo_09.py` reutiliza funções de `exemplo_08.py`. Os arquivos em `examples/` já estão prontos; rodar os geradores só os sobrescreve.
