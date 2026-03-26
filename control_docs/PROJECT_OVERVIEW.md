# Project Overview: VibeCoding Chat Atendente

> Chat inteligente com IA que atende, qualifica leads e vende cursos de vibe coding 24/7.

## 1. Visao do Projeto

| Campo | Valor |
|---|---|
| **Nome provisorio** | VibeCoding Chat Atendente |
| **Tagline** | Atendente IA que responde duvidas, qualifica leads e vende seus cursos de vibe coding automaticamente |
| **Proposta de valor** | Atendimento instantaneo 24h, sem depender do fundador estar online. Qualifica potenciais alunos e direciona para o produto certo (comunidade, mentoria ou consultoria) |

## 2. Problema

### 2.1 Situacao Atual
O fundador atende todos os interessados manualmente via WhatsApp pessoal e Instagram DM. Cada pessoa que pergunta sobre os cursos precisa de resposta individual. As mesmas perguntas se repetem dezenas de vezes. Fora do horario comercial, ninguem responde e potenciais clientes esfriam.

### 2.2 Quem Sofre
- **O fundador:** sobrecarregado com atendimento repetitivo, nao consegue escalar
- **Os potenciais alunos:** esperam horas ou dias por uma resposta, muitos desistem

### 2.3 Impacto
- Perda de vendas: leads esfriam enquanto aguardam resposta
- Tempo do fundador consumido por atendimento repetitivo em vez de criar conteudo e cursos
- Mistura de vida pessoal e profissional no WhatsApp
- Impossivel atender fora do horario ou em volume alto

### 2.4 Evidencia
Experiencia propria do fundador que vive o problema diariamente. O volume de mensagens repetitivas no WhatsApp e Instagram confirma a demanda nao atendida.

## 3. Publico-Alvo

### 3.1 Persona Primaria

| Campo | Descricao |
|---|---|
| **Nome ficticio** | "Pedro, o empreendedor curioso" |
| **Perfil** | 25-45 anos, empreendedor ou profissional que quer criar produtos digitais usando IA, sem saber programar |
| **Dor principal** | Quer aprender a construir com IA (vibe coding) mas nao sabe por onde comecar nem qual produto e certo para ele |
| **Comportamento atual** | Pesquisa no Instagram/YouTube, manda DM perguntando preco e detalhes, compara com outros cursos |
| **O que a faria adotar** | Resposta imediata, clareza sobre qual produto serve para o nivel dele, prova social |

### 3.2 Persona Secundaria

| Campo | Descricao |
|---|---|
| **Nome ficticio** | "Ana, a executiva de alto ticket" |
| **Perfil** | 35-55 anos, empresaria ou C-level que quer implementar IA na empresa |
| **Relacao com a persona primaria** | Busca solucoes mais caras (mentoria/consultoria), precisa de atendimento consultivo e personalizado |

### 3.3 Tamanho do Mercado (estimativa)

| Metrica | Estimativa | Base |
|---|---|---|
| **TAM** | A DEFINIR | Mercado de cursos de programacao/IA no Brasil |
| **SAM** | A DEFINIR | Pessoas interessadas especificamente em vibe coding |
| **SOM** (meta 12 meses) | A DEFINIR | Base atual de seguidores + alcance organico |

## 4. Solucao Proposta

### 4.1 O Que o Produto Faz
Um chat na web onde visitantes conversam com um atendente IA que:
- Responde duvidas sobre os cursos e o metodo de vibe coding
- Entende o perfil e nivel do visitante
- Recomenda o produto mais adequado (comunidade R$3.000/ano, mentoria R$20.000, consultoria R$100.000)
- Coleta dados de contato para follow-up
- Funciona 24 horas, 7 dias por semana

### 4.2 Core Use Case
Visitante chega no site com duvida sobre vibe coding -> conversa com a IA -> recebe recomendacao personalizada do produto certo -> IA captura o contato -> fundador faz o fechamento de vendas de alto ticket.

### 4.3 Diferencial
- Atendimento instantaneo 24/7 (vs. esperar resposta no WhatsApp)
- IA treinada especificamente sobre os produtos e metodo do fundador
- Qualificacao automatica: direciona cada lead para o produto certo baseado no perfil
- Libera o tempo do fundador para criar conteudo e atender alunos

## 5. Jornada Principal do Usuario

| Passo | O que acontece |
|---|---|
| 1 | Visitante acessa o site e ve o widget de chat |
| 2 | Inicia conversa e faz perguntas sobre vibe coding ou os cursos |
| 3 | A IA responde, faz perguntas para entender o perfil e objetivo do visitante |
| 4 | A IA recomenda o produto mais adequado (comunidade, mentoria ou consultoria) |
| 5 | A IA coleta nome, email e/ou WhatsApp para o fundador fazer follow-up |

## 6. Metricas de Sucesso

| Metrica | Meta (6 meses) | Como Medir |
|---|---|---|
| Conversas iniciadas por mes | 500+ | Analytics do chat |
| Taxa de captura de contato | 30%+ | Leads capturados / conversas |
| Vendas influenciadas pelo chat | 10+ comunidade/mes | CRM / acompanhamento manual |
| Tempo medio de resposta | < 5 segundos | Logs do sistema |
| Satisfacao do visitante | Positiva em 80%+ | Feedback no final do chat |

## 7. Restricoes e Premissas

### 7.1 Orcamento
Lean / AI-assisted. Custo principal sera o consumo da API do Gemini (pay-per-use).

### 7.2 Equipe
Solo + IA. O fundador opera sozinho com assistencia de agentes de IA.

### 7.3 Prazo
MVP funcional o mais rapido possivel.

### 7.4 Regulatorio e Compliance
LGPD se aplica: o chat coleta dados pessoais (nome, email, WhatsApp). Necessario: termos de uso, politica de privacidade, consentimento explicito para coleta de dados. VERIFICAR necessidade de consultoria juridica antes do lancamento.

### 7.5 Privacidade de Dados
O produto coleta: nome, email, WhatsApp, historico de conversa. Dados devem ser armazenados com seguranca, acesso restrito, e com possibilidade de exclusao a pedido do usuario (direito LGPD).

### 7.6 Outras Restricoes
- Idioma: Portugues brasileiro
- A IA deve conhecer os produtos, precos e metodo do fundador
- A IA NAO deve inventar informacoes ou fazer promessas de resultado
- Integracao futura desejavel com WhatsApp e Instagram (pos-MVP)

## 8. Concorrencia e Alternativas

| Alternativa | O que faz | Ponto forte | Ponto fraco | Por que o seu e melhor |
|---|---|---|---|---|
| WhatsApp manual | Fundador responde cada mensagem | Pessoal, direto | Nao escala, sem horario, mistura pessoal | Automatico, 24/7, qualifica leads |
| Instagram DM | Mensagens pelo Instagram | Onde o publico esta | Lento, sem qualificacao, perde contexto | IA com memoria de conversa e qualificacao |
| Chatbots genericos (ManyChat, Tidio) | Fluxos pre-definidos | Facil de configurar | Rigido, nao entende contexto, respostas roboticas | IA conversacional que entende e adapta |
| Intercom / Zendesk | Atendimento completo | Robusto | Caro, complexo, nao especializado | Leve, barato, feito sob medida |

## 9. Perguntas Abertas

- [ ] Qual o perfil exato do aluno tipico? (idade, nivel tecnico) — usando estimativa por ora
- [ ] Volume atual de mensagens por dia/semana?
- [ ] O fundador ja tem site ou precisa criar um?
- [ ] Conteudo de treinamento da IA: tem FAQ, materiais, descricao detalhada dos produtos?
- [ ] LGPD: precisa de consultoria juridica para termos e politica de privacidade?
- [ ] Tamanho do mercado: validar estimativas com dados reais

## 10. Proximos Passos

1. Resolver as Perguntas Abertas criticas (perfil do aluno, conteudo de treinamento)
2. **Executar mvp-scope-cutter para definir o MVP**
3. Executar core-domain-mapper + founder-stack-selector (podem rodar em paralelo)
4. Executar repo-blueprint-bootstrapper para criar a estrutura do repositorio
5. Executar control-docs-bootstrapper para gerar os docs canonicos
6. Executar agent-handoff-packet para preparar o kickoff do agente

---

> **Nota:** Este documento e vivo. Atualize-o conforme novas informacoes surgirem. Ele mora em `control_docs/PROJECT_OVERVIEW.md` e e a fonte de verdade sobre a visao do projeto.
