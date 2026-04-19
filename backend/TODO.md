# Implementação de Tags de Resposta do LLM

## Objetivo
Garantir que a resposta gerada pelo LLM seja estritamente processada em formato Markdown pelo frontend, envelopando o conteúdo de resposta com tags XML específicas.

## O que deve ser feito no Backend
No script onde o prompt principal do sistema (`System Prompt`) é injetado no modelo ou no processamento final do RAG:

1. Instruir o LLM (via prompt) para **obrigatoriamente** retornar sua resposta final dentro das seguintes tags de envelope:
   - Tag de abertura: `<ContentResponse>`
   - Tag de fechamento: `</ContentResponse>`

**Exemplo de Prompt para o Modelo:**
> "Sua resposta deve ser estritamente formatada em Markdown, envelopada dentro das tags <ContentResponse> e </ContentResponse>. Não adicione textos, saudações ou explicações fora dessas tags."

## Implementação no Frontend
O Frontend já foi preparado para isso usando um *Contrato de Inteligência Artificial* (Constants).
* **Local das constants:** `frontend/src/lib/contracts/ai.contract.ts`
* **Parsing:** O componente `chat/+page.svelte` procura especificamente por essas tags na propriedade `m.content` e envia para o parser do `marked` apenas o que estiver *dentro* delas. Se a tag não existir, ele aplicará um fallback seguro renderizando todo o texto.
