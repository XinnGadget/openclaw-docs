---
x-i18n:
    generated_at: "2026-04-11T15:15:56Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2a8884fc2c304bf96d4675f0c1d1ff781d6dc1ae8c49d92ce08040c9c7709035
    source_path: reference/rich-output-protocol.md
    workflow: 15
---

# Protocolo de Saída Rica

A saída do assistente pode incluir um pequeno conjunto de diretivas de entrega/renderização:

- `MEDIA:` para entrega de anexos
- `[[audio_as_voice]]` para dicas de apresentação em áudio
- `[[reply_to_current]]` / `[[reply_to:<id>]]` para metadados de resposta
- `[embed ...]` para renderização rica na Interface de Controle

Essas diretivas são separadas. `MEDIA:` e as tags de resposta/voz continuam sendo metadados de entrega; `[embed ...]` é o caminho de renderização rica apenas para a web.

## `[embed ...]`

`[embed ...]` é a única sintaxe de renderização rica voltada a agentes para a Interface de Controle.

Exemplo autocontido:

```text
[embed ref="cv_123" title="Status" /]
```

Regras:

- `[view ...]` não é mais válido para novas saídas.
- Os shortcodes de embed são renderizados apenas na superfície de mensagens do assistente.
- Apenas embeds com URL são renderizados. Use `ref="..."` ou `url="..."`.
- Shortcodes de embed em HTML inline no formato de bloco não são renderizados.
- A interface web remove o shortcode do texto visível e renderiza o embed inline.
- `MEDIA:` não é um alias de embed e não deve ser usado para renderização rica de embeds.

## Forma de Renderização Armazenada

O bloco de conteúdo do assistente normalizado/armazenado é um item `canvas` estruturado:

```json
{
  "type": "canvas",
  "preview": {
    "kind": "canvas",
    "surface": "assistant_message",
    "render": "url",
    "viewId": "cv_123",
    "url": "/__openclaw__/canvas/documents/cv_123/index.html",
    "title": "Status",
    "preferredHeight": 320
  }
}
```

Blocos ricos armazenados/renderizados usam diretamente esta forma `canvas`. `present_view` não é reconhecido.
