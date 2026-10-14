# Modelo de dados — PotatoGene

Base: [spec.md](spec.md), [plan.md](plan.md) e [contratos dos serviços](contracts/services.md). SQLite local, duas tabelas persistentes; comparação e dashboard são resultados de consulta.

## Variedade — tabela `varieties`

| Campo | Tipo | Regra |
| --- | --- | --- |
| id | INTEGER PRIMARY KEY AUTOINCREMENT | Gerado pelo banco; estável em edições; não reutilizar IDs excluídos para evitar seleções antigas apontando para novos registros. |
| name | TEXT NOT NULL | Nome exibido, de 1 a 100 caracteres após strip; único pela chave abaixo. |
| name_key | TEXT NOT NULL UNIQUE | name.strip().casefold(), calculado pelo negócio e gravado pelo repositório junto ao nome. |
| origin | TEXT NOT NULL | Procedência, de 1 a 100 caracteres; “Desconhecida” é permitido. |
| skin_color | TEXT NOT NULL | Cor da casca, de 1 a 50 caracteres. |
| flesh_color | TEXT NOT NULL | Cor da polpa, de 1 a 50 caracteres. |
| size | TEXT NOT NULL | Uma das opções: Pequeno, Médio, Grande. |

CHECKs do esquema: comprimentos mínimos/máximos dos textos de exibição, texto não vazio após trim básico e tamanho pertencente ao conjunto permitido. Chave normalizada não vazia, sem limite máximo igual ao texto exibido: casefold pode expandir caracteres. O serviço aplica a normalização Unicode completa; SQL UNIQUE protege a chave já calculada.

## Marcador — tabela `markers`

| Campo | Tipo | Regra |
| --- | --- | --- |
| id | INTEGER PRIMARY KEY AUTOINCREMENT | Gerado pelo banco; estável em edições. |
| variety_id | INTEGER NOT NULL | FOREIGN KEY para varieties.id, ON DELETE CASCADE. Não editável pelo formulário de edição do marcador. |
| code | TEXT NOT NULL | Código de 1 a 50 caracteres após strip, preservando grafia. |
| code_key | TEXT NOT NULL | code.strip().casefold(); único dentro da variedade. |
| value | TEXT NOT NULL | Texto de 1 a 100 caracteres; não interpretado como sequência científica, número ou traço biológico. |
| source | TEXT NOT NULL | Valor fixo “Demonstrativo — exemplo educacional”, atribuído pelo serviço e persistido. |

Restrições: UNIQUE(variety_id, code_key); CHECKs de comprimentos, textos não vazios e source igual à constante. Chave normalizada não vazia. Mesmo código em duas variedades é permitido. Uma variedade admite zero ou mais marcadores; cada marcador possui exatamente uma variedade existente.

## Índices e acesso

- A unicidade de name_key e de (variety_id, code_key) cria índices adequados ao volume do MVP; o índice composto também atende busca por variety_id. Não criar índices redundantes.
- Listar variedades com ORDER BY name_key, id; comparação não depende da ordenação original de cadastros.
- Identificadores são inteiros positivos; validação rejeita bool como ID, IDs inexistentes e associação órfã. IDs não são editados pelo usuário.
- Parâmetros de usuário entram somente como valores ligados a placeholders `?`. Nomes de tabelas, colunas e instruções de PRAGMA/DDL são constantes internas.
- Consultas do dashboard: COUNT de variedades; COUNT de registros de marcadores; COUNT DISTINCT de variety_id; GROUP BY size. Completar categorias ausentes com zero, evitando somas infladas por joins.

## Validação compartilhada

Validar antes de qualquer escrita, em cadastro e edição, independentemente da interface:

1. Campo textual precisa ser str; não converter objetos/números/None automaticamente.
2. Aplicar strip, validar tamanho com len (caracteres Unicode, não bytes) e rejeitar vazio.
3. Rejeitar quebras de linha, categorias Unicode Cc/Cf (controles/formatação invisível) e separadores de linha/parágrafo Zl/Zp; preservar pontuação, acentos e espaços internos visíveis.
4. Validar categorias de tamanho; nomes de tamanho traduzidos não viram números ou faixas físicas.
5. Calcular chaves casefold sem remover acentos, sem condensar espaços internos e sem normalização científica. Verificar duplicidade excluindo o próprio ID ao editar.
6. Verificar variedade de destino e marcador existente, e atribuir source fixo sem aceitar esse campo da UI.
7. Repositório aplica operação e trata conflitos de UNIQUE/FK/CHECK como falhas sem commit parcial; a UI recebe erro de domínio apropriado.

SQL reforça regras de integridade básicas; não substitui os validadores Unicode e de tipos do negócio. O repositório é a única porta de escrita da aplicação e recebe valores validados e chaves coerentes. Consultas parametrizadas preservam aspas e textos parecidos com SQL como dados.

## Resultados não persistentes

**Comparação**: IDs e nomes de duas variedades; tabela com os cinco campos e duas colunas de valores; tabela de marcadores obtida por outer merge em code_key com validação one_to_one. Preservar code e source de cada lado, inclusive se a grafia do mesmo código variar. Células ausentes permanecem ausentes no resultado do serviço; a UI as exibe como “Não registrado”. Caso ambas não tenham marcadores, devolver tabela vazia com colunas definidas e orientação, sem afirmar ausência biológica.

**Resumo**: total_varieties, total_markers, varieties_with_markers e counts_by_size, com Pequeno/Médio/Grande sempre presentes. Todos são inteiros não negativos; total de tamanhos igual ao total de variedades. Não persistir snapshots nem conclusões biológicas.

## Transições e atomicidade

| Operação | Antes | Após sucesso | Cancelamento ou falha |
| --- | --- | --- | --- |
| Criar variedade | Sem registro | Um registro e ID novo | Nenhuma alteração |
| Editar variedade | Registro existente | Mesmo ID e marcadores; novos campos/chave | Registro anterior íntegro |
| Excluir variedade | Variedade e seus marcadores | Ambos removidos no mesmo commit | Ambos preservados |
| Criar marcador | Variedade existente | Novo marcador demonstrativo associado | Nenhuma alteração |
| Editar marcador | Marcador existente | Mesmo ID, variety_id e source; novo código/valor | Registro anterior íntegro |
| Excluir marcador | Marcador existente | Somente ele removido | Ele e sua variedade preservados |

Cancelamento ocorre na UI antes de chamar escrita. Cada mutação confirmada usa transação explícita; commit falho aciona rollback e fecha conexão. Linhas afetadas inexistentes geram erro de registro não encontrado; nenhuma operação faz upsert silencioso.

## Inicialização, leitura e versão

Arquivo padrão: `data/potatogene.db` na raiz do projeto; config resolve a raiz pelo local do módulo, sem depender do diretório corrente. POTATOGENE_DB_PATH permite caminho alternativo, relativo à raiz ou absoluto, especialmente em testes. Não mudar caminho automaticamente diante de erro.

Banco ausente ou SQLite válido vazio (user_version=0 e nenhuma tabela de aplicação) recebe esquema e user_version=1 em uma transação, sem registros iniciais. Banco reconhecido versão 1 tem tabelas, campos, índices/restrições e relações conferidos; inicialização repetida não altera registros. Em arquivo existente, verificar integrity_check e foreign_key_check antes de permitir escrita. Esquema inesperado, versão desconhecida, relações inválidas ou arquivo ilegível impedem operações com mensagem controlada; nunca apagar, substituir ou reparar automaticamente.

Na inicialização, verificar também regras dos registros existentes com os validadores compartilhados, incluindo chaves normalizadas e origem fixa; recusar uso de dados incompatíveis, sem corrigir conteúdo silenciosamente. Ler toda comparação/resumo dentro de uma transação de leitura, sem usar estado de sessão como fonte de registros.

`schema.sql` será um conjunto pequeno de instruções DDL fixas executadas individualmente; não é uma migração existente. Mudanças futuras de versão devem documentar impacto e preservação dos dados, conforme a constituição.
