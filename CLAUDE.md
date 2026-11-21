# Tofo — instruções para o Claude

Responda sempre em **português**.

## Produção de vídeo com IA

Para qualquer vídeo, siga o fluxo em [`docs/workflow-video-ia.md`](docs/workflow-video-ia.md).

### Regras de ferramentas (obrigatórias)

- **Imagens = Nano Banana Pro no Google Flow.** É a ferramenta principal e **não gasta créditos**.
  Toda imagem (ficha de personagem, teste de estilo, primeiro/último quadro) sai de lá.
  **Nunca gaste crédito pago (OpenArt, Higgsfield, ArtList etc.) para gerar imagem** sem o usuário pedir.
- O MCP do Flow está **instalado no PC do usuário**:
  - Sessão rodando no PC (Claude Desktop ou `claude remote-control`): use o MCP do Flow direto.
  - Sessão na nuvem / celular: escreva os prompts; o usuário gera no Flow e salva numa pasta do
    **Google Drive**; leia as imagens pelo conector do Drive e revise.
- **Vídeo** (gasta crédito): Higgsfield, ArtList ou OpenArt, conforme o que estiver conectado.
  Sempre mostrar o custo e esperar aprovação antes de enviar.
- Pós-produção (cortes, cor, zoom, upscale, montagem): ffmpeg + Python.
