# Refatoração da Arquitetura de Prompt e Resposta (RAG)

## Objetivo
Garantir 100% de confiabilidade no contrato entre Frontend e Backend (tags de resposta) e melhorar drasticamente a qualidade da formatação Markdown gerada pelo LLM usando as melhores práticas de mercado.

## O Problema Atual
Delegar a responsabilidade de estruturação de dados (envelopamento com `<ContentResponse>`) ao prompt do LLM é falho, pois os modelos de IA são probabilísticos e tendem a "esquecer" ou ignorar instruções quando o contexto da pergunta se torna complexo. Além disso, as instruções de formatação de sistema estão misturadas na pergunta do usuário (QA Template).

## Plano de Ação (Checklist de Implementação)

- [x] **1. Limpar o QA Template Atual**
  - Arquivo: `backend/rag/engine.py`
  - Remover a constante `_SYSTEM_PROMPT` e a interpolação que exige "ALWAYS USING MARKDOWN FORMATTING".
  - Retornar o `PromptTemplate` do LlamaIndex para seu estado base (apenas recebendo o contexto e repassando a query do usuário).

- [x] **2. Garantir o Contrato de Tags XML Hardcoded**
  - Arquivo: `backend/rag/engine.py`
  - Na função `query(question: str)`, logo após a chamada `response = engine.query(question)`, aplicar hardcode da tag ao invés de confiar no LLM.
  - Implementar retorno seguro: `return f"<ContentResponse>\n{str(response)}\n</ContentResponse>"`

- [x] **3. Implementar o Suporte a 'System Prompt' nos Clentes LLM**
  - Arquivo: `backend/llm/client.py`
  - Adicionar suporte formal à injeção de instruções de sistema (`role="system"`) nas classes `OpenAISDKLLM` e `AnthropicLLM`, alinhando a estrutura com as melhores arquiteturas (como ChatGPT e Claude).
  - Atualizar os métodos `.complete()` e `.stream_complete()` para processar esse prompt antes do prompt de usuário.

- [x] **4. Configurar o System Prompt Oficial**
  - Arquivo: `backend/rag/engine.py` (no método `_build_engine` ou similar).
  - Passar uma instrução de sistema clara e robusta na inicialização do LLM (ex: `system_prompt="Você é um assistente técnico que responde estritamente usando Markdown rico (cabeçalhos, listas, blocos de código)."`).
