# PotatoGene — catálogo educacional

Primeiro incremento de implementação, restrito a T001–T036 (MVP First): cadastro, listagem, consulta, edição e exclusão de variedades com persistência SQLite, validação e tratamento de falhas. Interface Streamlit em português; listagem e detalhes em texto literal, sem renderização de DataFrames.

**Estado da verificação (2026-10-13):** 128 testes de negócio e integração aprovados. A suíte completa e a execução funcional no navegador continuam pendentes: Streamlit/AppTest não conseguem importar um arquivo Protobuf por acesso negado neste ambiente. A correção da apresentação está implementada, mas o MVP First ainda não está liberado como entrega verificada. As evidências abaixo distinguem esses bloqueios do diagnóstico de Code Integrity do PyArrow.

## Instalar no Windows

Requer Python **3.11 ou superior**, 64 bits recomendado, PowerShell e navegador. A preparação inicial obtém os pacotes; a operação do aplicativo instalado não necessita serviço externo.

Na raiz do projeto, em um ambiente com acesso aos pacotes:

```powershell
Set-Location C:\Users\renan\TutorialSpecKit
py -3.11 --version
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pip check
```

Se o Python instalado for outra versão ≥3.11, use, por exemplo, `py -3.14 -m venv .venv`. O ambiente `.venv` deste workspace contém Python 3.14.6 e os pacotes necessários, mas apresenta bloqueios de acesso descritos abaixo. Não é necessário ativar o venv ou mudar a política de execução do PowerShell.

Dependências diretas fixadas: Streamlit 1.50.0, Pandas 2.3.3 e pytest 8.4.2 para desenvolvimento. SQLite vem no módulo sqlite3 da biblioteca padrão; não instalar um pacote separado de SQLite.

O código do MVP First não importa Pandas nem PyArrow. Streamlit ainda declara essas dependências; esta mudança não remove pacotes nem altera a instalação do framework. Pandas permanece na baseline do plano para incrementos futuros.

requirements.txt e requirements-dev.txt, nesta entrega parcial, contêm somente as versões diretas, **não um lock transitivo verificado**. Para concluir T002: resolver em venv limpo Windows/Python 3.11, fixar todas as transitivas de execução em requirements.txt, manter o mesmo conjunto e as dependências pytest em requirements-dev.txt e reinstalar/verificar pip check. A versão mínima e os locks não foram validados neste ambiente.

## Iniciar e usar

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Abrir **http://127.0.0.1:8501**. Encerrar com Ctrl+C no terminal. A configuração do projeto usa loopback, modo headless e estatísticas de uso desativadas.

1. Clicar em **Cadastrar variedade** e preencher Nome, Origem, Cor da casca, Cor da polpa e Tamanho.
2. Usar **Salvar** para persistir; mudar campos ou cancelar não grava dados.
3. Selecionar uma variedade para consultar detalhes e usar **Editar** ou **Excluir**.
4. A exclusão exige confirmação e informa que os marcadores associados também serão removidos.

Erros de entrada indicam o campo e preservam o rascunho. Falhas de armazenamento não mostram sucesso nem alteram parcialmente os registros. Falha na abertura oferece **Tentar novamente**, sem aparentar um catálogo vazio válido. Detalhes técnicos ficam somente no terminal.

## Dados e validação

Arquivo padrão: **data/potatogene.db**, ancorado na raiz do projeto, independentemente do diretório corrente. A primeira execução cria automaticamente diretório e esquema versão 1, com catálogo vazio. Inicializações seguintes inspecionam integridade, versão, estrutura, associações e valores existentes; banco desconhecido ou ilegível não é apagado, substituído ou reparado automaticamente.

Para usar outro catálogo, especialmente em avaliação:

```powershell
$env:POTATOGENE_DB_PATH = Join-Path $env:TEMP 'potatogene-avaliacao.db'
.\.venv\Scripts\python.exe -m streamlit run app.py
# Após encerrar, restaurar o caminho padrão:
Remove-Item Env:POTATOGENE_DB_PATH -ErrorAction SilentlyContinue
```

Um caminho relativo na variável também é resolvido a partir da raiz. Escolha outro nome se quiser um catálogo novo sem excluir dados existentes.

| Campo | Regra |
| --- | --- |
| Nome | Texto obrigatório, 1–100 caracteres, único por strip().casefold(). |
| Origem | Texto obrigatório, 1–100 caracteres; “Desconhecida” é permitido. |
| Cor da casca / cor da polpa | Cada texto obrigatório, 1–50 caracteres. |
| Tamanho | Pequeno, Médio ou Grande. |

Textos rejeitam quebras/controles, preservam acentos e pontuação e removem espaços externos. Caracteres, não bytes, definem os limites. A comparação de nomes mantém acentos e espaços internos; manter o próprio nome ao editar é permitido. IDs são estáveis, positivos e não reutilizados após exclusão.

## Arquitetura

```text
app.py                      composição e inicialização
potatogene/config.py        caminho dos dados
potatogene/domain/          dataclasses, erros, validações e constantes
potatogene/services/        regras de negócio do catálogo
potatogene/data/            conexões, esquema e repositório SQLite
potatogene/ui/              formulários, listagem, detalhes e feedback
tests/unit/                 validações e negócio com repositório substituto
tests/integration/          SQLite real temporário e falhas injetadas
tests/ui/                   contratos Streamlit com AppTest
```

UI → serviço → repositório → SQLite. A UI não executa SQL, e negócio não importa Streamlit. Repositórios usam SQL fixo com parâmetros `?`; cada operação abre e fecha sua conexão. Transações explícitas fazem commit somente após sucesso e rollback em falhas. Foreign keys são habilitadas por conexão; ON DELETE CASCADE remove marcadores atomicamente com a variedade. Os testes usam catálogos temporários e nunca dados reais.

## Testar

Depois de instalar as dependências:

```powershell
.\.venv\Scripts\python.exe -m pytest
# Ou selecionar as três categorias deste incremento:
.\.venv\Scripts\python.exe -m pytest tests/unit tests/integration tests/ui
```

AppTest exercita formulários, confirmações, cancelamentos e mensagens sem navegador. A avaliação visual e offline precisa ser feita no navegador após a instalação. O roteiro completo está em [quickstart.md](specs/001-potatogene-mvp/quickstart.md); nesta etapa aplicam-se somente os cenários de catálogo, validação, persistência e erros, sem executar as funcionalidades de T037–T070.

Os testes de interface simulam PyArrow indisponível somente no processo de teste, verificam listagem literal dos cinco campos, ordenação, reabertura e CRUD. Não há substituição de módulos nem tratamento especial de importações no código de produção. A busca por botões verifica primeiro as exceções do AppTest para não ocultar uma falha de renderização com `StopIteration`; o timeout padrão não foi aumentado.

Quando o diretório temporário padrão ou o cache do pytest não forem acessíveis, usar um diretório **novo** dentro do workspace (pytest limpa o caminho fornecido como basetemp):

```powershell
$potatoTestPath = Join-Path (Get-Location).Path ('.cache/pytest-' + [guid]::NewGuid().ToString('N'))
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider --basetemp "$potatoTestPath"
```

## PyArrow e integridade de código

Diagnóstico fornecido: Windows Code Integrity, eventos **3077 e 3033**, bloqueando `pyarrow/arrow_python.dll` porque a assinatura não atende à política aplicada. `import pyarrow` também falha diretamente; não é uma falha de SQLite nem motivo para aumentar o timeout dos testes.

No MVP First, a chamada afetada era `st.table(DataFrame)` em `potatogene/ui/varieties.py`. Streamlit 1.50.0 serializa essa tabela com Arrow; `st.dataframe` e `st.data_editor` também usam PyArrow. Trocar o DataFrame por listas/dicionários dentro de `st.table` mantém a serialização Arrow. [Código de tabelas 1.50.0](https://github.com/streamlit/streamlit/blob/1.50.0/lib/streamlit/elements/arrow.py), [editor 1.50.0](https://github.com/streamlit/streamlit/blob/1.50.0/lib/streamlit/elements/widgets/data_editor.py).

`st.write(DataFrame)` também encaminha para apresentação tabular. `st.write(str)` e `st.markdown(str)` apresentam Markdown, mas exigem cuidado com a pontuação dos dados. Foi escolhido `st.text(str)` para cada registro: mostra Nome, Origem, Cor da casca, Cor da polpa e Tamanho sem interpretar Markdown/HTML ou produzir tabelas Arrow. O nome na confirmação de exclusão também usa texto literal. A seleção continua por ID, com formulários, validação, confirmação, transações e esquema SQLite preservados. [Documentação de st.write](https://docs.streamlit.io/develop/api-reference/write-magic/st.write).

Nenhuma política de segurança, assinatura, permissão do sistema ou DLL foi modificada. A ausência de renderização tabular evita a necessidade dessa DLL nos fluxos do catálogo; ainda exige comprovação pelos testes de interface e pelo navegador.

## Evidências desta execução

- Python disponível: **3.14.6**, Windows 64 bits; SQLite **3.50.4**.
- `python -m pytest tests/unit tests/integration -p no:cacheprovider --basetemp <diretório novo no workspace>`: **128 passed**, incluindo validação, CRUD, rollback, unicidade, cascade e reabertura. A primeira tentativa encontrou acesso negado ao diretório temporário padrão; usar um diretório gravável resolveu esse problema sem alterar permissões.
- Suíte completa com `python -m pytest -p no:cacheprovider`: interrompida na coleta de `tests/ui/test_app.py` por **PermissionError** em `.venv/Lib/site-packages/google/protobuf/descriptor_pb2.py`. Os sete testes AppTest atualizados ainda não têm resultado de execução.
- Ao repetir a suíte com basetemp novo e `--continue-on-collection-errors --tb=short`, resultado **128 passed, 1 error**: o erro permanece na coleta de AppTest. Esse resultado não aprova a suíte completa.
- `python -m streamlit run app.py`: encerra antes de iniciar o servidor pelo mesmo **PermissionError** de Protobuf. Portanto, **execução funcional no navegador não comprovada**. Disponibilidade HTTP sozinha também não seria suficiente para aprovar CRUD no navegador.
- `python -c "import pyarrow"`: **ImportError: DLL load failed while importing lib: Acesso negado**, coerente com o diagnóstico fornecido. Não foram alteradas políticas de Code Integrity.
- `pip check`: **No broken requirements found**; isso verifica metadados, não acesso a arquivos nem carregamento de DLLs. Tentativa de download de Protobuf pelo pip falhou com **WinError 10013**. Não se atribui o PermissionError de Protobuf a Code Integrity sem evidência adicional.
- Python 3.11, locks transitivos, avaliação offline, desempenho e participantes continuam pendentes. Não há aprovação integral dos critérios SC-001–SC-007. Para liberar o MVP First, é necessário executar a suíte completa e confirmar no navegador cadastro, listagem, validação, edição, cancelamento, exclusão e persistência após reabertura, em um ambiente com dependências acessíveis e as políticas de segurança mantidas.

## Escopo e próximos incrementos

O esquema e os modelos básicos de marcadores existem como fundação para integridade e fixtures. Não há gerenciamento de marcadores na UI ou em serviços, comparação ou dashboard neste incremento; T037–T070 permanecem intocadas e pendentes.

Marcadores de teste têm origem fixa **“Demonstrativo — exemplo educacional”**. Nenhum dado é apresentado como cientificamente validado, e o catálogo não infere parentesco, resistência, produtividade ou outras características biológicas.

Não há contas, serviços externos, sincronização, importação, backups, recuperação automática de bancos incompatíveis, gráficos ou histórico. O projeto segue a [constituição](.specify/memory/constitution.md), a [especificação](specs/001-potatogene-mvp/spec.md) e o [plano](specs/001-potatogene-mvp/plan.md), com validação integrada ainda pendente.
