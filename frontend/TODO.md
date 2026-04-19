# Frontend - TODO

## Testes Automatizados

- [ ] **Configurar o Ambiente de Testes para Svelte 5**
  - O ambiente de testes atual (`vitest` + `playwright`) está quebrando com a reatividade do Svelte 5 e com componentes que usam contexto (ex: `bits-ui`).
  - É necessário criar uma configuração de `vite.config.ts` ou `vitest.config.ts` que separe corretamente os testes de unidade (rodando em `jsdom` ou `node`) dos testes de componente (rodando em um navegador real via Playwright).
  - A configuração deve ser capaz de processar corretamente as dependências (`deps.inline`) e resolver os aliases (`$lib`).
  - O objetivo é fazer a suíte de testes completa (`npm test`) passar sem erros de ambiente.
