# Implementation Plan: PotatoGene — MVP educacional

**Branch**: `001-potatogene-mvp` (identificador retornado pelo setup; nenhuma branch Git criada) | **Date**: 2026-10-13 | **Spec**: [spec.md](spec.md)

**Input**: `specs/001-potatogene-mvp/spec.md`, constituição 1.0.0 e tecnologias/arquitetura solicitadas pelo usuário.

## Summary

### Correção de execução do MVP First — 2026-10-13

Esta decisão substitui o uso de DataFrame/st.table na listagem do primeiro incremento (T001–T036). O diagnóstico informado identifica eventos Windows Code Integrity 3077/3033 e bloqueio de `pyarrow/arrow_python.dll` por requisitos de assinatura; a importação direta de PyArrow também falha. Nenhuma política de segurança será desativada, enfraquecida ou contornada.

O ponto afetado no catálogo era `st.table(table.set_index("Nome"))` em `potatogene/ui/varieties.py`. Streamlit 1.50.0 utiliza serialização Arrow para `st.table`, `st.dataframe` e `st.data_editor`, inclusive quando recebe coleções convertíveis em DataFrame. `st.write(DataFrame)` também aciona apresentação tabular. Fontes: [tabelas 1.50.0](https://github.com/streamlit/streamlit/blob/1.50.0/lib/streamlit/elements/arrow.py), [editor 1.50.0](https://github.com/streamlit/streamlit/blob/1.50.0/lib/streamlit/elements/widgets/data_editor.py), [st.write](https://docs.streamlit.io/develop/api-reference/write-magic/st.write).

Alternativas avaliadas: `st.write(str)` e `st.markdown(str)` não precisam renderizar DataFrames, mas interpretam Markdown. Escolha: `st.text(str)` por variedade, com os cinco campos rotulados em português, preservando literalmente acentos, barras, asteriscos e HTML digitado. A confirmação de exclusão também usa `st.text`. Remover a importação Pandas da UI; manter ordenação do serviço, seleção por ID, cadastro, edição, cancelamento, exclusão confirmada, validação e persistência SQLite sem mudanças no esquema. A baseline Pandas permanece para planejamento dos próximos incrementos; Streamlit continua declarando Pandas/PyArrow como dependências.

AppTest: todos os fluxos do catálogo devem funcionar com a importação de PyArrow indisponível simulada exclusivamente nos testes. Verificar listagem textual completa e ordenada, ausência de elementos table/dataframe, nomes literais, reabertura e CRUD. A busca de botões deve apresentar primeiro a exceção de renderização, evitando `StopIteration` sem diagnóstico. Não aumentar timeouts para ocultar falhas. Nenhum mock de PyArrow ou substituição de dependências integra a aplicação.

Evidências: **128 testes unitários e de integração aprovados** em Python 3.14.6 ao usar basetemp novo dentro do workspace e desabilitar somente o cache do pytest. A suíte completa e o servidor Streamlit param antes de executar a aplicação por `PermissionError` ao importar `google/protobuf/descriptor_pb2.py`; download pelo pip bloqueado com WinError 10013. `pip check` aprova metadados, sem provar carregamento. Esse bloqueio adicional não foi atribuído a Code Integrity. Os sete testes AppTest e a execução funcional no navegador permanecem **pendentes**; não declarar MVP First corrigido integralmente até ambos serem comprovados. Detalhes e comandos em [README.md](../../README.md).

O restante do plano descreve o escopo completo futuro. Menções abaixo a Pandas e st.table não autorizam sua reintrodução no catálogo do MVP First; incrementos de comparação/dashboard precisarão rever a apresentação para respeitar a política aplicada antes de implementar esses fluxos.

Construir um catálogo local de variedades de batata com CRUD, marcadores demonstrativos, comparação de duas variedades e dashboard de contagens. Streamlit apresenta os fluxos em português; serviços Python validam regras e coordenam operações; repositórios encapsulam SQLite. Pandas organiza listagens e comparação descritiva. pytest verifica negócio, integridade, falhas e fluxos da interface.

As decisões e fontes estão em [research.md](research.md). O desenho preserva os 13 requisitos funcionais e os sete resultados mensuráveis da especificação. Este plano entrega documentação técnica; os arquivos de aplicação, instalação e testes descritos abaixo serão criados durante a implementação.

## Technical Context

**Language/Version**: Python 3.11 ou superior; validação inicial em 3.11 e adicional em 3.14 no Windows.

**Primary Dependencies**: Streamlit 1.50.0 e Pandas 2.3.3 como baseline direta; pytest 8.4.2 em desenvolvimento. Biblioteca padrão para SQLite, modelos, caminhos, normalização e logs. Metadados de compatibilidade conferidos em [research.md](research.md); instalação integrada e locks completos devem ser verificados na implementação.

**Storage**: SQLite local em `data/potatogene.db`; esquema versão 1; duas tabelas; inicialização automática e transacional, sem exemplos pré-carregados.

**Testing**: pytest com parametrização, repositório substituto, SQLite temporário, monkeypatch e Streamlit AppTest; avaliação manual de usabilidade, rigor educacional, desempenho e operação offline.

**Target Platform**: Windows com PowerShell, navegador local e Python 64 bits. Ambiente virtual; comando sem exigir ativação do venv.

**Project Type**: Aplicação web local em um único projeto Python, sem API pública nem servidor de banco separado.

**Performance Goals**: Com 100 variedades e até 20 marcadores por variedade, resultados em até 2 segundos em 19 de 20 consultas por fluxo de listagem, comparação e dashboard (SC-002).

**Constraints**: Operação sem serviços externos após instalar dependências; um usuário por catálogo; português; sem inferências biológicas, salvamento parcial ou perda de dados em falhas; consultas parametrizadas e fechamento explícito de conexões.

**Scale/Scope**: CRUD de variedades e marcadores, comparação e resumo estatístico; três áreas de navegação: Variedades (inclui marcadores), Comparação e Dashboard. Volumes de avaliação não são limites de cadastro. Sem autenticação, importação, backup, gráficos, sincronização ou histórico.

## Constitution Check

Gates avaliados antes da pesquisa e reavaliados após o desenho. A aprovação abaixo significa conformidade do plano; a implementação ainda deverá comprovar seu cumprimento.

| Princípio | Gate e evidência de projeto | Antes | Após desenho |
| --- | --- | --- | --- |
| I — Python 3.11+ | Dependências compatíveis, locks e testes na versão mínima; instruções Windows. | Conforme | Conforme |
| II — Modularidade e documentação | Módulos por camada e funcionalidade; README, docstrings públicas e artefatos de desenho. | Conforme | Conforme |
| III — Português | Contrato de UI com rótulos, erros, confirmações e explicações educacionais. | Conforme | Conforme |
| IV — SQLite local | SQL parametrizado, integridade referencial, transações, inicialização e fechamento de conexões. | Conforme | Conforme |
| V — Validação e erros | Validadores no negócio, erros tipados, rollback, campos preservados e tratamento sem traceback na UI. | Conforme | Conforme |
| VI — pytest | Testes de negócio, limites, falhas, persistência real temporária e regressão; suíte obrigatória antes de integração. | Conforme | Conforme |
| VII — Responsabilidades | UI chama serviços; serviços usam repositórios; SQL apenas em data; negócio testável sem Streamlit e banco real. | Conforme | Conforme |
| VIII — Integridade científica | Origem fixa demonstrativa persistida e apresentada; comparação sem inferências. | Conforme | Conforme |
| IX — MVP simples | Um projeto, biblioteca padrão, duas tabelas, três áreas; sem recursos além do escopo. | Conforme | Conforme |

Resultado: nenhum desvio constitucional, nenhuma emenda necessária e nenhuma decisão pendente. [data-model.md](data-model.md), [contratos](contracts/ui.md) e [quickstart.md](quickstart.md) sustentam a revisão após o desenho.

## Project Structure

### Documentation (this feature)

```text
specs/001-potatogene-mvp/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── ui.md
│   └── services.md
├── checklists/requirements.md
└── tasks.md                     # Futuro: gerado por speckit-tasks
```

### Source Code (repository root)

Estrutura a criar na implementação:

```text
app.py                          # Ponto de entrada; composição e navegação
potatogene/
├── __init__.py
├── config.py                   # Caminho estável e override para testes
├── domain/
│   ├── __init__.py
│   ├── models.py               # Dataclasses e constantes
│   ├── validation.py           # Tipos, textos, limites e chaves
│   └── errors.py               # Erros de validação/domínio/dados
├── services/
│   ├── __init__.py
│   ├── varieties.py            # Cadastro, edição, consulta e exclusão
│   ├── markers.py              # Marcadores demonstrativos
│   ├── comparison.py           # Validação da seleção e outer merge
│   └── dashboard.py            # Resumo das contagens
├── data/
│   ├── __init__.py
│   ├── database.py             # Conexões, inicialização e transações
│   ├── schema.sql              # DDL fixo das duas tabelas e índices
│   └── repositories.py         # SQL de variedades, marcadores e resumo
└── ui/
    ├── __init__.py
    ├── varieties.py            # Lista e formulários
    ├── markers.py              # Seção nos detalhes da variedade
    ├── comparison.py           # Seleção de dois IDs e tabelas
    ├── dashboard.py            # Indicadores e tabela de tamanhos
    └── feedback.py             # Tradução de erros e mensagens
.streamlit/config.toml          # Loopback, telemetria desativada
requirements.in                # Dependências diretas fixadas
requirements.txt               # Lock completo de execução
requirements-dev.txt           # Lock completo de execução + pytest
README.md
.gitignore                     # .venv, dados locais e caches
pytest.ini                     # Diretório tests e marker performance
tests/
├── conftest.py                 # Caminhos temporários e repositório substituto
├── unit/
│   ├── test_validation.py
│   ├── test_varieties.py
│   ├── test_markers.py
│   ├── test_comparison.py
│   └── test_dashboard.py
├── integration/
│   ├── test_database.py
│   ├── test_repositories.py
│   └── test_failures.py
├── ui/test_app.py
└── performance/test_queries.py
data/potatogene.db               # Gerado na primeira execução
```

**Structure Decision**: Pacote simples na raiz para importação direta por `app.py` e `python -m pytest`; não necessita publicação de pacote. `data/` na raiz contém dados do usuário, enquanto `potatogene/data/` contém código de persistência. Não criar diretórios de implementação durante esta fase.

## Arquitetura e responsabilidades

Fluxo: UI → serviços → repositórios → SQLite. Apenas `app.py` compõe os serviços com os repositórios e chama a inicialização; telas não conhecem conexões ou SQL. Funções de negócio recebem dados tipados e dependências por construtor/parâmetro, podendo usar um repositório substituto nos testes. Não criar framework de injeção, classes-base genéricas ou camada HTTP.

Modelos simples em dataclasses definem entradas e registros. Validadores compartilhados aplicam tipo, `strip`, obrigatoriedade, limites em caracteres, ausência de quebras/controles e chaves `casefold`. Serviços verificam unicidade e existência; SQLite reforça NOT NULL, CHECK, UNIQUE e FOREIGN KEY. Conflitos finais de integridade são convertidos em erros de domínio, inclusive quando a pré-verificação passou. Origem do marcador é constante atribuída pelo serviço, sem entrada editável.

Pandas não executa consultas. Repositórios retornam registros simples; a listagem vira DataFrame na apresentação. O serviço de comparação transforma registros em tabelas estruturadas, faz junção externa por código normalizado e mantém a ausência como dado ausente. A UI define títulos em português e “Não registrado” e usa st.table para apresentação estática, evitando controles auxiliares de tabelas interativas em inglês. Dashboard usa consultas agregadas na camada de dados, retorna resumo tipado e apresenta métricas e uma tabela com as três categorias, inclusive zeros.

## Persistência e ciclo de operação

1. Resolver caminho independente do diretório corrente, com `POTATOGENE_DB_PATH` opcional. Criar diretório se necessário. Nunca usar o banco padrão nos testes.
2. Na abertura, verificar arquivo existente, integridade, versão e estrutura. Arquivo ausente ou SQLite válido vazio é inicializado em uma transação com DDL fixo e versão 1. Esquema desconhecido não é reparado automaticamente. Arquivo inválido não é excluído ou substituído.
3. Em cada conexão, ativar e verificar foreign keys; manter o padrão de restrição à thread. Usar timeout limitado de 5 segundos para bloqueios; erro orienta nova tentativa sem gravação parcial.
4. Cada escrita usa BEGIN explícito, instruções fixas com valores ligados por parâmetros, commit após sucesso e rollback em falha, com close em finally. A exclusão por ID da variedade aciona cascade na mesma transação. DDL é executado por instruções individuais, sem executescript que interfira no controle transacional.
5. Leituras compostas de comparação e resumo usam uma única conexão e transação de leitura para dados coerentes. Consultas retornam registros atuais; não usar cache de resultados persistentes nem conexão global Streamlit.
6. Após commit, UI mostra confirmação e atualiza a consulta. Exceções esperadas viram mensagens portuguesas; detalhes técnicos ficam em logging local no terminal. Erros não são silenciados nem retornam lista vazia artificial. Diante de falha inicial, suspender operações e oferecer “Tentar novamente”.

Versão do esquema: `PRAGMA user_version = 1`. Alterações futuras exigem documentar preservação dos registros e migração; o MVP não inclui mecanismo genérico de migrações.

## Interface e estado

Navegação em português com três opções. Variedades inclui listagem ordenada por chave normalizada, cadastro, seleção por ID, detalhes, edição e marcadores. Mostrar identificação da variedade ao excluir e informar a remoção dos marcadores. Remoção de marcador também exige confirmação explícita.

Formulários usam chaves estáveis específicas por operação e ID, `clear_on_submit=False` e valores do registro para edição. Guardar rascunhos e feedback apenas em session_state. Cancelar não chama escrita. Erros de validação mantêm os valores digitados e indicam campos. Limpar estado de formulário após sucesso/cancelamento respeitando as regras de atualização de widgets antes de sua instanciação; não alterar a chave de um widget já renderizado no mesmo ciclo. Usar um sinalizador consumido no próximo rerun quando necessário.

Ações persistentes ocorrem somente após submissão ou confirmação, sem repetir gravações em reruns seguintes. Comparação seleciona exatamente dois IDs existentes; nova consulta lê o banco e invalida referências excluídas. Cada apresentação de marcador informa sua origem demonstrativa, incluindo o aviso de que o cadastro não valida ciência nem permite conclusões biológicas.

## Dependências e instalação reproduzível

`requirements.in` registra Streamlit 1.50.0 e Pandas 2.3.3. Na implementação, resolver o ambiente limpo Windows/Python 3.11, produzir requirements.txt com versões exatas de todas as dependências de execução, depois requirements-dev.txt com o mesmo conjunto e pytest 8.4.2 e suas transitivas. Reinstalar ambos em ambientes limpos e executar pip check e testes. Esses locks não existem nesta fase e não foram testados em conjunto.

Não adicionar ORM, ferramentas de migrations, pacote de SQLite, gráficos ou servidor externo. AppTest já faz parte do Streamlit. Documentar Python, SQLite embutido e versões de pacotes usadas na avaliação; testar a baseline também no Python 3.14 e ajustar locks se necessário sem abandonar 3.11.

## Estratégia de implementação

1. Preparar dependências, configuração e documentação de execução; implementar modelos, erros e validadores com testes de limites (US2).
2. Implementar esquema, inicialização, repositórios e testes reais de integridade, persistência e rollback (US1 e US2).
3. Implementar serviços e UI do catálogo com consulta, CRUD, cancelamento e confirmação; validar a primeira entrega funcional persistente (US1 e US2).
4. Implementar serviços e seção de marcadores com origem fixa e avisos educacionais; testar associação, unicidade e cascade (US3).
5. Implementar comparação via Pandas, seleção inválida e marcadores ausentes (US4).
6. Implementar agregações e dashboard com contagens atuais e estado vazio (US5).
7. Completar AppTest e avaliação do quickstart; verificar os sete critérios de sucesso, offline, instalação limpa e documentação. Executar a suíte pertinente antes de integrar mudanças.

Gerar tarefas ordenadas na próxima etapa com `$speckit-tasks`; este documento não cria tasks.md nem implementa a aplicação.

## Estratégia de testes e rastreabilidade

| Cobertura | Verificação prevista | Requisitos |
| --- | --- | --- |
| Catálogo | CRUD, listagem, identidade estável, marcadores preservados, exclusão e cancelamento via AppTest. | FR-001–004 |
| Marcadores | CRUD, vínculo existente, código único por variedade, origem fixa em detalhes/reabertura/comparação; explicação sem inferências. | FR-005–007 |
| Comparação | Dois IDs distintos; seleção incompleta/removida; cinco campos; códigos iguais com caixa diferente; marcadores exclusivos; nenhum marcador. | FR-008 |
| Dashboard | Totais e três tamanhos, inclusive zeros; mesmo código em variedades diferentes; consultas após sucesso, falha e cancelamento. | FR-009 |
| Persistência | Primeira execução, inicialização repetida, banco reaberto e 10 ciclos de persistência; funcionamento sem conexão externa. | FR-010 |
| Validação | Parametrizar cada campo: tipo errado, vazio, espaços, limites 1/N/N+1, quebra de linha, controles, acentos, aspas, duplicidades e edição do próprio nome. | FR-011 |
| Falhas | Banco inválido/incompatível, falhas de leitura/escrita/commit, timeout e rollback integral; erro sem sucesso nem sobrescrita. | FR-012 |
| Português | Rótulos, estados vazios, mensagens e orientações; códigos preservados; ausência de traceback e falsos resultados. | FR-013 |

Negócio: repositório substituto em memória, sem Streamlit e sem SQLite real, cobrindo invariantes independentemente dos widgets. Integração: SQLite real em tmp_path por teste, nunca banco do usuário. AppTest: override do caminho antes do primeiro run; simular interação e chamar run após mudanças. Falhas: monkeypatch no ponto utilizado pela camada de dados e falha durante commit/operação para verificar rollback, fechamento da conexão e preservação, além de leitura inacessível. Regressões automatizáveis exigem teste específico.

Desempenho: cenário temporário com 100 variedades e 2.000 marcadores, 20 consultas por fluxo, marker performance. Medir serviço como diagnóstico e tempo percebido da submissão até tabelas visíveis no navegador como critério SC-002; pytest isoladamente não prova latência da interface. Registrar equipamento, Python e pacotes. Avaliação com cinco participantes comprova SC-001 e SC-006, sem substituir esses resultados por contagem de testes.

Execução e roteiro completo: [quickstart.md](quickstart.md). Conclusão da implementação exige suíte aprovada, medidas registradas e revisão constitucional; esta fase verificou somente documentos e rastreabilidade.
