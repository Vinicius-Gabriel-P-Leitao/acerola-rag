# Melhoria na Precisão de Busca e Recuperação (RAG)

## Objetivo
Resolver as deficiências de contexto do assistente (como "Lost in the Middle" e recuperação de documentos semanticamente similares, mas não idênticos aos termos da busca, e.g., "Date" vs "Data Collection") melhorando a inteligência da etapa de *Retrieval*.

## O Problema Atual (Diagnóstico)
O sistema RAG está entregando material de baixa qualidade para a geração da resposta:
1.  **Recuperação Puramente Vetorial:** Falha na busca por palavras-chave exatas (Keyword Search), o que é crítico ao buscar por código (`z.date()`).
2.  **"Lost in the Middle":** A IA ignora pedaços vitais do contexto quando eles ficam no meio dos documentos retornados pelo *retriever*.

## Plano de Ação

- [ ] **1. Ajustar Chunking**
  - **Ação:** Revisar as constantes `chunk_size` e `chunk_overlap` (`backend/config.py`) em relação à densidade da documentação inserida (código vs. texto). Pedaços muito curtos perdem continuidade de código, pedaços muito longos causam "Lost in the Middle". (Avaliar *Semantic Chunking* como alternativa futura).

- [ ] **2. Implementar Busca Híbrida (Hybrid Search)**
  - **Ação:** Configurar o *retriever* no `backend/rag/engine.py` (ou na pipeline de indexação) para usar tanto BM25 (busca lexical/por palavra-chave) quanto embeddings (busca semântica), caso o LlamaIndex suporte nativamente com o Chroma, ou fundi-los com um `QueryFusionRetriever`.

- [ ] **3. Implementar Re-Ranking (LongContextReorder)**
  - **Ação:** Adicionar um pós-processador (Postprocessor) à *Query Engine* no `backend/rag/engine.py`. O `LongContextReorder` reorganiza os documentos recuperados colocando os mais relevantes no início e no final do contexto, contornando a "preguiça" natural dos LLMs (Lost in the Middle).

- [ ] **4. Redução/Ajuste de `similarity_top_k` e `response_mode`**
  - **Ação:** Testar a combinação de retornar mais documentos (e.g., `top_k=5`) mas aplicar o modo `refine` (`response_mode="refine"`) para forçar a IA a iterar sobre cada documento. Alternativamente, manter um `top_k` menor (e.g., `3`) e usar o modo `compact` padrão se o Re-Ranking for suficiente.

- [ ] **5. Testes de Casos Limites**
  - **Ação:** Após as modificações, usar perguntas difíceis ("Quero exemplos de Zod para Date" ou nomes de variáveis específicos que se confundem semanticamente com palavras normais).
