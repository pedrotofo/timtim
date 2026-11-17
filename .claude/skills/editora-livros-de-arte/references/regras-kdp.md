# Regras de publicação (KDP e EPUB)

Levantadas em 17/11/2026. O site da KDP (kdp.amazon.com) estava bloqueado na rede da sessão: os números abaixo vêm de buscas que citam as páginas de ajuda da KDP e de guias que conferem com elas. Antes de cada envio, confira no próprio site os itens marcados com ⚠.

## Kindle eBook (KDP)

| Item | Regra | Fonte |
|---|---|---|
| Formato do original | EPUB é o formato recomendado; layout refluível | KDP Help; guias de requisitos KDP |
| Tamanho do arquivo | até 650 MB | vários guias KDP |
| Custo de entrega | na opção de 70 %, cobrado por MB do arquivo **convertido** (o KPF, que pode pesar diferente do EPUB): US$ 0,15/MB na Amazon.com, R$ 0,30/MB na Amazon.com.br. A tela de preço da KDP mostra o valor real depois do envio | KDP Pricing (G200634500) |
| 70 % ou 35 % | royalty de 70 % = 70 % × (preço − impostos − entrega); 35 % não tem tarifa de entrega. Num livro de imagens, a de 70 % só compensa acima de **duas vezes a tarifa de entrega**. A faixa de preço que permite 70 % mudou em 07/07/2026 (nos EUA, US$ 2,99 a 12,99) ⚠ confira a faixa em reais no painel | KDP Pricing |
| Amostra grátis | os primeiros 10 % do conteúdo (front matter incluído) viram a amostra e o "Ler amostra" | KDP Help (G200644250) |
| KDP Select | 90 dias de exclusividade do **e-book**: enquanto durar, o EPUB não pode estar na Apple, Google, Kobo nem no seu site. Impresso fica livre | guias de KDP Select ⚠ termos atuais |
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
- **Apple Books: nenhuma imagem dentro do EPUB acima de 4 milhões de pixels**, e isso vale para a capa interna (1600 × 2560 = 4,1 milhões é recusada). Dentro do EPUB a capa vai a 1500 × 2400; a de 1600 × 2560 é enviada à parte. A capa da loja precisa de pelo menos 1400 px no lado menor.
- **Acessibilidade.** Desde 28/06/2025 a Lei Europeia de Acessibilidade vale para e-books vendidos na UE. O build declara no OPF os metadados `schema:accessMode`, `accessibilityFeature`, `accessibilityHazard` e `accessibilitySummary` (o que o livro tem), sem afirmar conformidade auditada. Um autor sozinho se enquadra como microempresa (menos de 10 pessoas e até 2 milhões de euros); declarar a isenção (`a11y:exemption` = `eaa-microenterprise`) é decisão do autor, e as lojas podem não aceitar.
- ISBN: o Kindle não exige; Apple, Google e Kobo aceitam sem. No Brasil o ISBN sai pela CBL e cada formato (impresso, EPUB) tem o seu.

## Fontes consultadas

- [KDP — Trim size](https://kdp.amazon.com/help?topicId=G201857950) e [Paperback Submission Guidelines](https://kdp.amazon.com/en_US/help/topic/G201857950)
- [KDP — eBook cover (G6GTK3T3NUHKLEFX)](https://kdp.amazon.com/en_US/help/topic/G6GTK3T3NUHKLEFX)
- [KDP margin table, DEV Community](https://dev.to/orenrot24/setting-kdp-paperback-margins-in-latex-the-gutter-table-a-working-preamble-and-a-check-that-1gkl)
- [Book Margins and Gutter, diybookformats](https://diybookformats.com/book-margins-and-gutter/)
- [Cambric — KDP Requirements](https://cambric.pub/guides/kdp-requirements/)
- [deckle.studio — Amazon KDP EPUB requirements](https://deckle.studio/wiki/workflow/export/epub/amazon-kdp-epub-requirements/)
- [KDP spine width calculator (inkfluenceai)](https://www.inkfluenceai.com/kdp-spine-width-calculator)
- [Lightning Source — ePUB File Creation Guidelines](https://help.lightningsource.com/hc/en-us/articles/5294175362061-ePUB-File-Creation-Guidelines)
- [KDP — eBook Royalties e custo de entrega (G200634500, pt-BR)](https://kdp.amazon.com/pt_BR/help/topic/G200634500)
- [KDP — amostra e Look Inside (G200644250)](https://kdp.amazon.com/help/topic/G200644250)
- [Apple Books — preparar o livro (limite de imagem)](https://itunespartner.apple.com/books/support/9-prepare-book)
- [W3C — EPUB Accessibility exemption property](https://www.w3.org/TR/epub-a11y-exemption)
- [ALLi — European Accessibility Act](https://selfpublishingadvice.org/european-accessibility-act/)
- [Scribecount — KDP Select, guia](https://scribecount.com/author-resource/publishing-a-book/kdp-select-the-complete-operational-guide)
