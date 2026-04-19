# Refatoração da Arquitetura de Prompt e Resposta (RAG)

## Objetivo
Garantir 100% de confiabilidade no contrato entre Frontend e Backend (tags de resposta) e melhorar drasticamente a qualidade da formatação Markdown gerada pelo LLM.

## O problema atual
Delegar a responsabilidade de estruturação de dados (envelopamento com `<ContentResponse>`) ao prompt do LLM é falho, pois os modelos de IA são probabilísticos e tendem a "esquecer" ou ignorar instruções quando o contexto da pergunta se torna complexo. Além disso, as instruções de formatação de sistema estão misturadas na pergunta do usuário (QA Template).

## Plano de Ação (A ser implementado no Backend)

### 1. Garantir o Contrato de Tags XML via Backend
Em vez de pedir para o LLM adicionar as tags, o código Python vai garantir isso de forma "hardcoded".

- **Arquivo:** `backend/rag/engine.py`
- **Ação:** Interceptar a resposta do `engine.query(question)` no método `query()` e concatenar as tags `<ContentResponse>` e `</ContentResponse>` no texto, garantindo que elas cheguem ao roteador da API já prontas, ou então concatenar as tags diretamente lá no `routes.py`. Faremos isso de forma hardcoded e infalível, ou seja, de forma puramente algorítmica.

### 2. Refatorar o Prompt de Sistema Global (System Prompt)
Removeremos o peso de formatação XML do LLM e o focaremos exclusivamente em agir como um assistente técnico gerador de Markdown rico.

- **Arquivo:** `backend/llm/client.py` ou `backend/rag/engine.py`
- **Ação:** Implementar o parâmetro `system_prompt` diretamente nas configurações do LLM (`Settings.llm` ou na criação do cliente).
- **Conteúdo Sugerido do System Prompt:**
  > "Você é um assistente técnico focado em extrair informações de documentações. 
  > Sua função é responder a dúvida do usuário com base estritamente no contexto fornecido.
  > Você DEVE SEMPRE usar formatação Markdown rica. Use obrigatoriamente:
  > - Cabeçalhos (###) para estruturar sua resposta;
  > - Listas e bullet-points para enumerar passos ou características;
  > - Blocos de código (```linguagem) quando mencionar configurações, comandos ou código-fonte.
  > Não adicione textos informais como 'Aqui está a resposta', seja direto."

### 3. Limpar o QA Template
- **Arquivo:** `backend/rag/engine.py`
- **Ação:** Voltar o `qa_prompt` para seu estado limpo original (apenas contexto e pergunta), delegando a responsabilidade de "como responder" (Markdown) para o *System Prompt* descrito acima.
