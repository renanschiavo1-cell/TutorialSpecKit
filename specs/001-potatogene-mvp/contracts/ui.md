# Contrato de interface Streamlit — PotatoGene

Aplicação web local em português. Navegação: **Variedades**, **Comparação**, **Dashboard**. Cada ação utiliza os [serviços](services.md); SQL não aparece nas telas. IDs servem como valores internos das seleções; nomes são os rótulos exibidos.

## Variedades e marcadores — US1, US2 e US3

- Listagem em tabela Pandas somente para leitura, ordenada por nome; estado vazio informa “Nenhuma variedade cadastrada” e oferece “Cadastrar variedade”.
- Cadastro e edição apresentam Nome, Origem, Cor da casca, Cor da polpa e Tamanho; este último usa seleção Pequeno/Médio/Grande com estado inicial não escolhido no cadastro. Origem admite “Desconhecida”.
- Ações explícitas: Salvar e Cancelar. Não persistir ao mudar widgets. Erro de campo mantém todos os valores digitados; sucesso mostra confirmação e atualiza a listagem. Cancelar mantém o registro salvo.
- Seleção abre detalhes e ações Editar/Excluir. Exclusão mostra o nome e “Os marcadores desta variedade também serão excluídos”, com Confirmar exclusão/Cancelar. Cancelar não chama serviço de escrita.
- Detalhes apresentam seção Marcadores genéticos demonstrativos, com Código, Valor e Origem. Sem registros: “Nenhum marcador registrado”, acompanhado da explicação de que isso não significa ausência biológica.
- Adicionar/editar marcador pede somente Código e Valor. A indicação “Demonstrativo — exemplo educacional” é visível e não editável. Remover exige confirmação e afeta apenas o marcador selecionado.
- Texto educativo: “Marcadores são identificadores usados aqui como exemplos para aprendizagem. Os valores cadastrados não foram cientificamente validados e não permitem concluir parentesco ou prever características biológicas.”

Formulários têm chaves por operação e ID; session_state guarda apenas rascunho, seleção, confirmação e feedback. Em erro não limpar formulário. Após sucesso ou cancelamento, consumir sinalizador de limpeza antes de renderizar widgets no próximo ciclo. Rerun não pode repetir escrita já concluída.

## Comparação — US4

- Dois seletores: Variedade A e Variedade B, com ação Comparar. Com menos de duas variedades, orientar o cadastro de outra. Seleção incompleta, igual ou inválida não produz comparação.
- Tabela de campos: linhas Nome/Origem/Cor da casca/Cor da polpa/Tamanho; colunas identificam as variedades.
- Tabela de marcadores: código e valor de cada lado, com origem de cada registro presente. Códigos equivalentes são alinhados mesmo se a grafia variar. Exibir “Não registrado” apenas nas células sem registro; não substituir valor real igual a esse texto por ausência.
- Se ambas não possuem marcadores, apresentar orientação sem conclusão biológica. Exibir o aviso educativo junto à comparação. Não mostrar ranking, escore de similaridade, parentesco ou previsão.
- Comparar novamente lê registros atuais; se ID tiver sido removido, invalidar a seleção e orientar nova escolha, sem apresentar resultado antigo como atual.

## Dashboard — US5

- Indicadores: Total de variedades, Total de marcadores, Variedades com marcadores.
- Tabela: Tamanho e Quantidade, com Pequeno, Médio e Grande, mesmo quando zero.
- Catálogo vazio: todos os indicadores são zero e ação/orientação de cadastro. Ao entrar ou consultar novamente, ler dados atuais; cancelamento e falha não alteram contagens.

## Erros, inicialização e operação local — US2

- Primeira execução inicializa catálogo vazio; não inserir exemplos automaticamente.
- Falha ao abrir dados apresenta orientação e ação Tentar novamente; suspender operações, sem dashboard zerado ou listagem vazia que sugira leitura bem-sucedida.
- Falha de escrita não mostra sucesso e mantém dados anteriores e rascunho quando aplicável. Mensagens esperadas não exibem SQL ou traceback.
- Configuração local: servidor em 127.0.0.1, sem estatísticas de uso, assets remotos ou integrações externas. Verificar funcionamento offline após instalar dependências.
- Rótulos, confirmações e mensagens definidos pela aplicação são em português; identificadores científicos preservam grafia. Apresentar DataFrames com st.table e rótulos portugueses, sem a barra de ferramentas de tabelas interativas; inspeção no navegador confirma FR-013.

AppTest verifica entradas, confirmações, mensagens, cancelamento, origem e atualização de tabelas com banco temporário. O navegador verifica legibilidade, controles, desempenho e operação offline. Roteiro: [quickstart.md](../quickstart.md).
