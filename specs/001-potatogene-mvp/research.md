# Pesquisa técnica — PotatoGene

Data: 2026-10-13. Base: [spec.md](spec.md) e constituição 1.0.0. Pesquisa concluída antes do desenho; nenhuma decisão exige esclarecimento. Fontes primárias consultadas pelos agentes de pesquisa e pelo responsável pelo plano.

## 1. Dependências e compatibilidade

**Decisão**: Python 3.11+; baseline direta `streamlit==1.50.0`, `pandas==2.3.3` e `pytest==8.4.2`. `sqlite3`, `pathlib`, `dataclasses`, `unicodedata` e `logging` pertencem à biblioteca padrão. Não instalar pacote chamado SQLite.

**Justificativa**: Releases identificáveis com metadados compatíveis com Python 3.11, sem necessidade das versões mais recentes para os fluxos definidos. São uma baseline de planejamento, ainda sem validação integrada de instalação. Na implementação, resolver transitivas em Windows/Python 3.11, fixar todas em `requirements.txt` e `requirements-dev.txt`, executar `pip check` e a suíte e repetir em Python 3.14. Se os ambientes precisarem de resoluções diferentes, manter locks nomeados por versão e documentar a escolha. Não declarar suporte a versões futuras sem validação.

**Alternativas consideradas**: Dependências sem versão dificultam reprodução; ORM, ferramentas de empacotamento adicionais e plugins de testes não atendem a necessidade atual.

Fontes: [Streamlit 1.50.0](https://pypi.org/project/streamlit/1.50.0/), [Pandas 2.3.3](https://pypi.org/project/pandas/2.3.3/), [pytest 8.4.2](https://pypi.org/project/pytest/8.4.2/).

## 2. Formulários e execução da interface

**Decisão**: Formulários com submissão explícita; `session_state` guarda rascunhos, seleção por ID, confirmação e mensagens transitórias. SQLite é a fonte dos dados salvos. Preservar os campos diante de erro, limpar apenas após sucesso ou cancelamento. Reconsultar após alterações e usar rerun somente depois de concluir a operação.

**Justificativa**: Streamlit reexecuta o script; formulários agrupam entradas e evitam gravações por simples alteração de widget. Estado de sessão pode desaparecer com recarga e não serve como persistência. Não usar cache para catálogo nem compartilhar conexão SQLite entre sessões.

**Alternativas consideradas**: Autosalvamento, callbacks com gravações e dados persistentes em sessão foram descartados por contrariar confirmação e preservação dos dados.

Fontes: [Forms](https://docs.streamlit.io/develop/concepts/architecture/forms), [Session State](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state), [rerun](https://docs.streamlit.io/develop/api-reference/execution-flow/st.rerun).

## 3. SQLite e atomicidade

**Decisão**: Conexão por operação, SQL fixo com placeholders `?`, `PRAGMA foreign_keys = ON` antes de transações; `isolation_level=None`, `BEGIN`, commit ou rollback explícitos e fechamento em `finally`. Usar a API disponível em Python 3.11, sem depender do argumento `autocommit` de versões posteriores. Exclusão da variedade usa chave estrangeira com `ON DELETE CASCADE`.

**Justificativa**: Impede entradas interpretadas como SQL, registros órfãos e gravações parciais. O context manager de conexão não fecha a conexão automaticamente. Não usar `executescript` dentro das transações previstas; executar instruções de esquema individualmente.

**Alternativas consideradas**: Conexão global, exclusão em duas operações independentes e interpolação de SQL foram rejeitadas por integridade e gerenciamento de recursos.

Fontes: [Python 3.11 sqlite3](https://docs.python.org/3.11/library/sqlite3.html), [SQLite foreign keys](https://www.sqlite.org/foreignkeys.html).

## 4. Inicialização e arquivos existentes

**Decisão**: Caminho padrão estável `data/potatogene.db`, relativo à raiz obtida do arquivo de configuração, com substituição por `POTATOGENE_DB_PATH` para testes. Inicializar banco ausente ou SQLite válido e vazio sem tabelas de aplicação; criar esquema e `user_version=1` na mesma transação. Antes de escrever em arquivo existente, verificar integridade, versão e estrutura. Esquema desconhecido, dados ilegíveis ou falta de acesso geram erro controlado, sem apagar ou substituir o arquivo.

**Justificativa**: Inicialização repetida deve preservar o catálogo. `IF NOT EXISTS` não comprova compatibilidade de esquema. Usar `PRAGMA integrity_check` e `foreign_key_check` na abertura da aplicação; resultados inesperados impedem uso, em vez de serem convertidos em lista vazia. As checagens não substituem validações de negócio.

**Alternativas consideradas**: Reinicialização destrutiva e reparo automático de schema foram rejeitados. `quick_check` é mais limitado; o catálogo pequeno permite a checagem completa inicial.

Fontes: [CREATE TABLE](https://www.sqlite.org/lang_createtable.html), [PRAGMAs de integridade](https://www.sqlite.org/pragma.html#pragma_integrity_check).

## 5. Unicidade e comparação

**Decisão**: Exibir textos com grafia preservada após `strip()` e guardar chaves calculadas com `strip().casefold()` para nomes e códigos. Não remover acentos nem condensar espaços internos. A comparação usa Pandas outer merge por chave do código com `validate='one_to_one'`; ausências são representadas por dados ausentes e traduzidas apenas na interface.

**Justificativa**: Uma regra compartilhada cobre unicidade, ordenação e alinhamento, inclusive letras não ASCII. A junção externa preserva marcadores exclusivos. Valores permanecem textos demonstrativos, sem pontuações de similaridade ou inferência científica.

**Alternativas consideradas**: `COLLATE NOCASE` sozinho não implementa toda a equivalência Unicode escolhida. Inner merge ocultaria exclusivos. Não normalizar valores genéticos como números ou sequências científicas.

Fontes: [str.casefold](https://docs.python.org/3.11/library/stdtypes.html#str.casefold), [Pandas merge](https://pandas.pydata.org/pandas-docs/version/2.3/reference/api/pandas.DataFrame.merge.html).

## 6. Operação local e testes

**Decisão**: Escutar em `127.0.0.1`, desativar envio de estatísticas de uso, usar apenas widgets e recursos locais. pytest testa negócio com repositório substituto e persistência real em `tmp_path`; `monkeypatch` injeta falhas e caminho temporário. AppTest exercita os fluxos Streamlit; validação no navegador complementa aspectos visuais e funcionamento offline.

**Justificativa**: O aplicativo não necessita hospedagem, conta ou serviço externo. A instalação inicial obtém pacotes; a operação após preparação é local. AppTest permite verificar entradas e mensagens sem adicionar automação de navegador.

**Alternativas consideradas**: Cloud, chamadas externas, banco real em testes e uma ferramenta adicional de testes de navegador não são necessários ao MVP.

Fontes: [Configuração Streamlit](https://docs.streamlit.io/develop/api-reference/configuration/config.toml), [AppTest](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest), [pytest tmp_path](https://docs.pytest.org/en/stable/how-to/tmp_path.html), [pytest monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html).
