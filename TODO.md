# TODO

## Componentes

- [x] Criar `sh-tooltip` — wrapper do `tooltip.svelte` da bits-ui com API simplificada (`content`, `side`, `delay`)

## Chat

- [x] Verificar `accept` do file input e tipos validados antes do upload — todos os formatos (.pdf, .docx, .doc, .txt, .md) estão alinhados entre frontend e backend
- [x] Exibir painel de sources sempre que `sources.length > 0`, não só ao carregar histórico
- [x] Usar `sh-tooltip` no nome do arquivo truncado nas sources
- [x] Modal/drawer de source — exibir `chunk_text` completo com campo de busca por `source_file`

## Streaming / Backend

- [x] Frontend: `chatStore.send()` gera `conversationId` no cliente, sempre inclui no FormData
- [x] Frontend: após o stream, busca sources via `GET /history/{convId}` e popula o store
- [x] `chatStore`: sources populados ao fim do stream em conversas novas e continuadas

## Admin

- [x] Corrigir paginação na tela de documentos (controles prev/next com estado de página)

## UI / Layout

- [x] Melhorar estilo de tabelas no markdown (bordas, zebra striping, scroll horizontal)
- [x] Corrigir centralização dos ícones quando a sidebar está colapsada
