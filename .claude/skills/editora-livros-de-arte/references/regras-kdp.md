# Regras de publicação (KDP e EPUB)

Levantadas em 17/11/2026. O site da KDP (kdp.amazon.com) estava bloqueado na rede da sessão: os números abaixo vêm de buscas que citam as páginas de ajuda da KDP e de guias que conferem com elas. Antes de cada envio, confira no próprio site os itens marcados com ⚠.

## Kindle eBook (KDP)

| Item | Regra | Fonte |
|---|---|---|
| Formato do original | EPUB é o formato recomendado; layout refluível | KDP Help; guias de requisitos KDP |
| Tamanho do arquivo | até 650 MB | vários guias KDP |
| Custo de entrega | na opção de 70 %, cobrado por MB do arquivo convertido (cerca de US$ 0,15/MB nos EUA) ⚠ tabela por país | KDP Pricing |
| Validação | EPUBCheck sem erros; conferir no Kindle Previewer | guias KDP; deckle.studio |
| Sumário | documento de navegação (EPUB 3 `nav` com `epub:type="toc"`) | guias KDP |
| Capa interna | imagem declarada no manifesto (`properties="cover-image"`) | guias KDP |
| Imagens internas | JPEG ou PNG; WebP não; float e posicionamento CSS pouco confiáveis no Kindle | guias KDP |

## Capa do e-book

| Item | Regra |
|---|---|
| Tamanho | ideal 1600 × 2560 px (largura × altura), proporção 1,6:1 |
| Mínimo | 625 × 1000 px ⚠ alguns guias dizem 1600 × 2560 como mínimo |
| Formato | JPEG ou TIFF, RGB (CMYK é recusado) |
| Peso | até 50 MB |
| Cuidados | não esticar imagem pequena; capa muito clara perde o contorno na loja |

## KDP Paperback (impresso)

| Item | Regra |
|---|---|
| Corte da série | 6 × 9 pol. (formato padrão KDP) |
| Sangria | página 0,125 pol. mais larga e 0,25 pol. mais alta: 6,125 × 9,25 pol. para 6 × 9 ⚠ |
| Margem interna (lombada) | 24 a 150 páginas: 0,375 pol.; 151 a 300: 0,5; 301 a 500: 0,625; 501 a 700: 0,75; 701 a 828: 0,875 |
| Margem externa, topo e base | mínimo 0,25 pol. sem sangria; 0,375 pol. com sangria |
| Páginas | mínimo 24; máximo 828 em preto e branco ⚠ papel colorido tem outros limites (o colorido padrão começa em 72 páginas) |
| Imagens | 300 ppi recomendados |
| Fontes | todas embutidas no PDF |
| Arquivo | PDF de páginas simples (não espelhadas), sem marcas de corte, sem a capa |
| Lombada | páginas × 0,002252 pol. (branco), × 0,0025 (creme), × 0,002347 (colorido premium) ⚠ colorido padrão |
| Capa inteira | largura = 0,125 + corte + lombada + corte + 0,125; altura = altura do corte + 0,25 |
| Texto na lombada | só com mais de 79 páginas, com folga de 0,0625 pol. de cada lado |
| Código de barras | a KDP aplica no canto inferior direito da contracapa: deixe a área livre |

## EPUB para as outras lojas (Apple Books, Google Play, Kobo)

- EPUB 3, EPUBCheck sem erros nem avisos.
- Metadados: título, autor, idioma (`pt-BR`), identificador único, `dcterms:modified`, descrição.
- `lang` em cada página (hifenização e leitura em voz alta).
- `alt` descritivo em toda imagem de conteúdo.
- Fontes embutidas só com licença que permita (EB Garamond e Archivo: SIL Open Font License, permitido).

## Fontes consultadas

- [KDP — Trim size](https://kdp.amazon.com/help?topicId=G201857950) e [Paperback Submission Guidelines](https://kdp.amazon.com/en_US/help/topic/G201857950)
- [KDP — eBook cover (G6GTK3T3NUHKLEFX)](https://kdp.amazon.com/en_US/help/topic/G6GTK3T3NUHKLEFX)
- [KDP margin table, DEV Community](https://dev.to/orenrot24/setting-kdp-paperback-margins-in-latex-the-gutter-table-a-working-preamble-and-a-check-that-1gkl)
- [Book Margins and Gutter, diybookformats](https://diybookformats.com/book-margins-and-gutter/)
- [Cambric — KDP Requirements](https://cambric.pub/guides/kdp-requirements/)
- [deckle.studio — Amazon KDP EPUB requirements](https://deckle.studio/wiki/workflow/export/epub/amazon-kdp-epub-requirements/)
- [KDP spine width calculator (inkfluenceai)](https://www.inkfluenceai.com/kdp-spine-width-calculator)
- [Lightning Source — ePUB File Creation Guidelines](https://help.lightningsource.com/hc/en-us/articles/5294175362061-ePUB-File-Creation-Guidelines)
