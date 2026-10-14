# Feature Specification: PotatoGene — MVP educacional

**Feature Branch**: Nenhuma branch criada; feature identificada por `specs/001-potatogene-mvp`.

**Created**: 2026-10-13

**Status**: Draft — validada para planejamento.

**Input**: Especificação funcional conforme a constituição existente: cadastrar, editar e excluir variedades; registrar nome, origem, cores da casca e polpa e tamanho; associar marcadores demonstrativos; comparar duas variedades; exibir estatísticas; salvar localmente; validar entradas e tratar erros. MVP educacional simples.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Gerenciar variedades (Priority: P1)

Como estudante ou educador, quero cadastrar, consultar, editar e excluir variedades para manter um catálogo local com informações básicas de batatas.

**Why this priority**: O catálogo entrega valor educacional mesmo sem comparação ou estatísticas.

**Independent Test**: Partir de um catálogo vazio, cadastrar uma variedade, consultar os campos, editar e excluir, verificando cada resultado.

**Acceptance Scenarios**:

1. **Given** um catálogo vazio, **When** consulto a listagem, **Then** vejo uma mensagem em português indicando a ausência de variedades e uma ação para cadastrar.
2. **Given** cinco campos válidos, **When** confirmo o cadastro, **Then** vejo confirmação, a variedade na listagem e todos os campos na consulta de detalhes.
3. **Given** uma variedade cadastrada, **When** altero seus campos e salvo, **Then** vejo os novos valores, com a mesma identidade e os mesmos marcadores; cancelar mantém os valores anteriores.
4. **Given** uma variedade com marcadores, **When** solicito exclusão, **Then** vejo sua identificação e um aviso de que os marcadores também serão removidos; confirmar remove ambos, cancelar preserva ambos.

### User Story 2 - Preservar dados e corrigir entradas (Priority: P1)

Como usuário, quero encontrar meus dados ao reabrir o aplicativo e receber orientações diante de entradas inválidas ou falhas para corrigir problemas sem perder registros válidos.

**Why this priority**: A confiabilidade do catálogo é essencial desde a primeira entrega.

**Independent Test**: Cadastrar e reabrir; exercitar valores válidos, inválidos e limites das regras de entrada; simular falhas de leitura e gravação usando dados de teste.

**Acceptance Scenarios**:

1. **Given** registros salvos, **When** fecho e reabro no mesmo ambiente local, **Then** encontro os mesmos campos, associações e origens, inclusive edições e exclusões confirmadas.
2. **Given** entradas nos limites da tabela de validação, **When** salvo, **Then** valores válidos são aceitos; vazios, excesso de caracteres, formato inválido, duplicidades e associações inexistentes são rejeitados antes de alterar os dados.
3. **Given** entrada inválida, **When** tento salvar, **Then** uma mensagem em português identifica campo e regra violada e posso corrigir sem redigitar os demais campos válidos.
4. **Given** falha de gravação, inclusive durante exclusão de variedade com marcadores, **When** confirmo a operação, **Then** vejo uma mensagem de falha sem confirmação de sucesso; nenhum registro é alterado parcialmente e os dados anteriores são preservados.
5. **Given** dados locais inacessíveis ou ilegíveis, **When** abro o catálogo, **Then** vejo uma mensagem para verificar o acesso e tentar novamente; os dados não são sobrescritos nem apresentados como um catálogo vazio válido.
6. **Given** primeiro uso sem dados anteriores, **When** inicio o aplicativo, **Then** posso usar um catálogo vazio sem servidor ou serviço externo; no ambiente preparado, todas as operações essenciais funcionam sem internet.
7. **Given** qualquer fluxo essencial, **When** consulto ações, instruções, confirmações e erros, **Then** os textos estão em português, os termos genéticos têm explicações acessíveis e nenhuma falha esperada expõe rastreamentos técnicos.

### User Story 3 - Organizar marcadores demonstrativos (Priority: P2)

Como estudante ou educador, quero associar marcadores demonstrativos a uma variedade para organizar exemplos de informações genéticas.

**Why this priority**: Acrescenta conteúdo genético sem exigir análise científica ou dados laboratoriais.

**Independent Test**: Usar uma variedade previamente cadastrada como condição de teste, adicionar dois marcadores, consultar, editar e remover um deles.

**Acceptance Scenarios**:

1. **Given** uma variedade sem marcadores, **When** consulto seus detalhes, **Then** vejo que nenhum marcador foi registrado, sem afirmar ausência biológica.
2. **Given** uma variedade existente, **When** registro código e valor válidos, **Then** o marcador fica associado somente a ela, com origem “Demonstrativo — exemplo educacional”, inclusive quando digitado pelo usuário.
3. **Given** um marcador existente, **When** edito código ou valor e salvo, **Then** os dados são atualizados preservando associação e origem; cancelar mantém os dados anteriores.
4. **Given** um marcador existente, **When** solicito sua remoção, **Then** confirmar remove apenas esse marcador e cancelar o preserva; a variedade permanece em ambos os casos.
5. **Given** marcadores apresentados nos detalhes ou na comparação, **When** consulto a explicação, **Then** entendo que são exemplos registrados sem validação científica e sem inferências de parentesco ou características biológicas.

### User Story 4 - Comparar duas variedades (Priority: P2)

Como estudante ou educador, quero consultar duas variedades lado a lado para reconhecer semelhanças e diferenças nos dados cadastrados.

**Why this priority**: Permite explorar o catálogo sem cálculos genéticos ou interpretações científicas adicionais.

**Independent Test**: Preparar duas variedades com informações conhecidas, inclusive uma sem marcadores, e conferir a comparação com os registros.

**Acceptance Scenarios**:

1. **Given** duas variedades distintas, **When** seleciono ambas e comparo, **Then** vejo nome, origem, cor da casca, cor da polpa e tamanho lado a lado.
2. **Given** marcadores nas variedades selecionadas, **When** comparo, **Then** vejo os marcadores alinhados por código, seus valores e origens e “Não registrado” quando um código existe apenas na outra variedade.
3. **Given** menos de duas variedades, seleção incompleta ou a mesma variedade selecionada duas vezes, **When** tento comparar, **Then** recebo orientação em português para selecionar duas variedades distintas, sem resultado enganoso.
4. **Given** uma comparação exibida, **When** altero ou excluo uma variedade e solicito nova comparação, **Then** vejo dados atuais ou uma orientação para refazer a seleção se a variedade não existir mais.

### User Story 5 - Consultar estatísticas (Priority: P3)

Como estudante ou educador, quero visualizar um dashboard simples para acompanhar a quantidade e a distribuição dos registros.

**Why this priority**: Resume o catálogo; os fluxos principais funcionam sem esse resumo.

**Independent Test**: Preparar três variedades, uma de cada tamanho, com dois, um e zero marcadores, conferir os indicadores e repetir após alterações.

**Acceptance Scenarios**:

1. **Given** três variedades de tamanhos distintos e três marcadores presentes em duas variedades, **When** abro o dashboard, **Then** vejo 3 variedades, 3 marcadores, 2 variedades com marcadores e 1 variedade em cada categoria de tamanho.
2. **Given** catálogo vazio, **When** abro o dashboard, **Then** todos os totais e contagens por tamanho são zero e vejo orientação para cadastrar dados.
3. **Given** inclusão, edição ou exclusão concluída, **When** consulto novamente o dashboard, **Then** todas as contagens refletem os dados salvos, sem incluir alterações canceladas ou malsucedidas.

### Edge Cases

- Campos contendo somente espaços são vazios; espaços externos são removidos antes da validação e gravação.
- Nomes que diferem apenas por maiúsculas/minúsculas ou espaços externos são duplicados; manter o nome da própria variedade em uma edição é permitido.
- Código de marcador repetido na mesma variedade é rejeitado; o mesmo código em variedades diferentes é permitido.
- Aspas, acentos e hífens em textos válidos são preservados como conteúdo sem provocar falha de gravação.
- Ausência de marcador é ausência de informação registrada, sem significado biológico negativo.
- Excluir o último registro retorna à listagem vazia e zera o dashboard na consulta seguinte.
- Seleção que referencia variedade removida exige nova seleção; marcador não pode ser associado a variedade inexistente.
- Dados ilegíveis não acionam reinicialização destrutiva; falhas em operações com variedade e marcadores preservam integralmente o estado anterior.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE cadastrar variedades com nome, origem, cor da casca, cor da polpa e tamanho, todos obrigatórios. Aceitação: US1.2 e US2.2.
- **FR-002**: O sistema DEVE listar variedades por nome e consultar seus cinco campos e marcadores; a listagem vazia DEVE orientar o cadastro. Aceitação: US1.1–2 e US3.1.
- **FR-003**: O sistema DEVE editar os cinco campos mantendo identidade e marcadores; cancelar preserva o estado anterior. Aceitação: US1.3.
- **FR-004**: O sistema DEVE confirmar a exclusão de uma variedade, avisar sobre seus marcadores e remover ambos como uma única operação; cancelar preserva ambos. Aceitação: US1.4 e US2.4.
- **FR-005**: O sistema DEVE adicionar, consultar, editar e remover marcadores de variedade existente, com código, valor e origem; remoção exige confirmação, e cancelamentos preservam os dados. Aceitação: US3.1–4.
- **FR-006**: Todos os marcadores deste MVP DEVEM ter origem “Demonstrativo — exemplo educacional”, preservada ao salvar, editar, reabrir e comparar. Valores digitados pelo usuário também são exemplos sem validação científica. Aceitação: US3.2–5, US4.2 e US2.1.
- **FR-007**: O sistema DEVE limitar a comparação aos dados registrados, sem inferir parentesco, resistência, produtividade, superioridade ou outras características biológicas. DEVE explicar a natureza educacional dos marcadores. Aceitação: US3.5 e US4.1–2.
- **FR-008**: O sistema DEVE comparar exatamente duas variedades distintas, com cinco campos lado a lado e marcadores alinhados por código; ausência é “Não registrado”. Seleções inválidas recebem orientação e cada nova consulta reflete os dados atuais. Aceitação: US4.1–4.
- **FR-009**: O dashboard DEVE mostrar total de variedades, total de registros de marcadores, total de variedades com pelo menos um marcador e contagens de variedades pequenas, médias e grandes. Um código em duas variedades conta como dois registros. As contagens refletem os dados salvos e são zero no catálogo vazio. Aceitação: US5.1–3.
- **FR-010**: O sistema DEVE salvar localmente cada operação confirmada, manter os dados entre sessões no mesmo ambiente e funcionar sem serviço externo ou internet após a preparação do ambiente. O primeiro uso inicia um catálogo vazio. Aceitação: US2.1 e US2.6.
- **FR-011**: O sistema DEVE validar obrigatoriedade, formato, limites, unicidade e associação a variedade existente conforme as regras abaixo, antes de salvar. Registros inválidos não alteram os dados persistidos. Aceitação: US2.2–3 e casos de duplicidade e associação em Edge Cases.
- **FR-012**: O sistema DEVE tratar erros de entrada, leitura e gravação com mensagens claras em português, sem rastreamentos técnicos nem falsas confirmações. Falhas de gravação preservam o estado anterior; falhas de leitura não sobrescrevem dados nem aparentam catálogo vazio válido. Aceitação: US2.3–5.
- **FR-013**: Rótulos, instruções, confirmações, estados vazios e erros DEVEM estar em português, com ações explícitas e explicações acessíveis dos termos genéticos; códigos científicos podem manter sua grafia original. Aceitação: US2.7.

#### Regras de campos e validação

Os limites contam caracteres após remover espaços externos. Textos são de uma linha, sem quebras de linha ou caracteres de controle; acentos, aspas, hífens e pontuações visíveis são permitidos. Textos compostos apenas de espaços são inválidos.

| Campo | Regra | Critério de aceitação |
| --- | --- | --- |
| Nome da variedade | Texto obrigatório de 1 a 100 caracteres; único, ignorando maiúsculas/minúsculas e espaços externos. | Aceitar 1 e 100 caracteres; rejeitar vazio, 101 caracteres e nome equivalente de outra variedade. |
| Origem da variedade | Procedência como texto obrigatório de 1 a 100 caracteres; “Desconhecida” é permitido. | Aceitar limites e origem desconhecida explícita; rejeitar vazio e 101 caracteres. |
| Cor da casca | Texto obrigatório de 1 a 50 caracteres. | Aceitar limites e descrições de mais de uma cor; rejeitar vazio e 51 caracteres. |
| Cor da polpa | Texto obrigatório de 1 a 50 caracteres. | Aceitar limites; rejeitar vazio e 51 caracteres. |
| Tamanho | Categoria obrigatória: Pequeno, Médio ou Grande. | Aceitar somente essas três opções; rejeitar ausência e outro valor. |
| Código do marcador | Texto obrigatório de 1 a 50 caracteres; único dentro da variedade, ignorando maiúsculas/minúsculas e espaços externos. | Aceitar limites e código igual em outra variedade; rejeitar vazio, 51 caracteres e duplicidade na mesma variedade. |
| Valor do marcador | Texto obrigatório de 1 a 100 caracteres, descritivo e demonstrativo, sem exigir sequência genética real. | Aceitar limites; rejeitar vazio e 101 caracteres, sem avaliar validade científica. |
| Origem do marcador | Atribuída pelo sistema: “Demonstrativo — exemplo educacional”. | Apresentar no registro e comparação, preservar entre sessões e impedir troca por afirmação de validação científica. |

As regras se aplicam a cadastros e edições. A identidade de variedades e marcadores é estável nas edições e não exige preenchimento pelo usuário. Comparação de códigos usa a mesma equivalência da unicidade e exibe a grafia registrada. A ordenação da listagem ignora maiúsculas/minúsculas.

### Key Entities *(include if feature involves data)*

- **Variedade de batata**: Registro com identidade estável, nome único, procedência, cores da casca e polpa e categoria de tamanho; possui zero ou mais marcadores.
- **Marcador genético demonstrativo**: Registro com identidade estável, associado a exatamente uma variedade, com código, valor e origem educacional. Não constitui evidência científica; é removido quando sua variedade é excluída.
- **Comparação**: Apresentação temporária de duas variedades e seus marcadores atuais; não é um novo registro salvo.
- **Resumo estatístico**: Contagens dos registros atuais, sem edição independente nem conclusões biológicas.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Pelo menos 4 de 5 participantes representativos de estudantes ou educadores conseguem cadastrar, consultar, editar e excluir uma variedade sem intervenção do facilitador, em até 5 minutos, usando dados fornecidos.
- **SC-002**: Com 100 variedades e até 20 marcadores por variedade, listagem, comparação e dashboard apresentam resultados em até 2 segundos em pelo menos 19 de 20 consultas de cada fluxo no ambiente de demonstração documentado.
- **SC-003**: Em 10 ciclos de fechar e reabrir após operações confirmadas, 100% dos campos, associações, origens e exclusões correspondem ao último estado salvo.
- **SC-004**: Todos os casos válidos, inválidos e limites da tabela apresentam o resultado esperado; nenhuma entrada rejeitada ou falha simulada de gravação altera parcialmente os dados anteriores.
- **SC-005**: Contagens do dashboard coincidem integralmente com os registros nos cenários vazio, inicial, após cadastro, edição e exclusão; a comparação apresenta todos os campos e marcadores corretamente, inclusive ausências.
- **SC-006**: Pelo menos 4 de 5 participantes, após consultar detalhes e comparação, conseguem explicar que os marcadores são demonstrativos e não permitem concluir parentesco ou prever características biológicas.
- **SC-007**: Todos os cenários essenciais são concluídos sem internet no ambiente local preparado; todas as mensagens dos cenários de validação e falha estão em português e orientam a próxima ação.

## Assumptions

- Público-alvo: estudantes e educadores; um usuário opera um catálogo local por vez, sem contas, permissões diferenciadas ou edição simultânea.
- Tamanho é uma categoria informada pelo usuário, sem medição nem faixas físicas de peso ou diâmetro. Cores e procedência são textos livres sujeitos aos limites definidos.
- Todos os marcadores são demonstrativos, inclusive os fornecidos pelo usuário. Origem geográfica da variedade é distinta da origem educacional do marcador. Importação científica e associações biológicas ficam fora do MVP.
- Os dados permanecem no mesmo ambiente local até exclusão explícita. Backup, exportação, importação, sincronização e recuperação de arquivos corrompidos ficam fora do escopo; preservar dados diante de falhas de operação continua obrigatório.
- O catálogo inicia vazio, sem carregamento automático de exemplos. Os volumes de SC-002 são referências de avaliação, sem impor limites funcionais de 100 variedades ou 20 marcadores.
- Dashboard é um resumo consultável das contagens definidas; gráficos, filtros, relatórios, histórico e estatísticas genéticas avançadas ficam fora do escopo. A modalidade da interface será escolhida no planejamento conforme a simplicidade exigida.
- A dependência normativa é a [constituição do PotatoGene, versão 1.0.0](../../.specify/memory/constitution.md), que permanece inalterada e prevalece sobre esta especificação. Suas obrigações de implementação, documentação, separação de responsabilidades e testes devem ser verificadas no planejamento e na revisão; aqui são definidos comportamentos observáveis, sem escolher novas tecnologias.
- O ambiente deve estar preparado e permitir acesso aos dados locais. Falhas de acesso são abrangidas por FR-012; nenhuma operação essencial depende de integração externa.

