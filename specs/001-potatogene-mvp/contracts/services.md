# Contrato interno dos serviços — PotatoGene

Este contrato liga UI e negócio, sem API HTTP. Funções em módulos pequenos, com dataclasses de entrada/resultado e repositórios recebidos por dependência. UI não envia conexões, SQL, chaves normalizadas ou origem científica. Serviços não importam Streamlit.

## Operações

| Módulo/operação | Entrada | Resultado e regra |
| --- | --- | --- |
| varieties.create | VarietyInput(name, origin, skin_color, flesh_color, size) | Variedade salva com ID; valida todos os campos e nome único. |
| varieties.list | Sem filtros | Lista de variedades ordenada por name_key e ID; lista vazia somente após leitura válida. |
| varieties.get | variety_id | Variedade existente e consulta de marcadores associada para detalhes; inexistência gera erro. |
| varieties.update | variety_id e VarietyInput completo | Variedade com mesmo ID e marcadores preservados; não altera criação/identidade. |
| varieties.delete | variety_id | Remove variedade e marcadores atomicamente; UI já obteve confirmação. |
| markers.list | variety_id | Lista de marcadores por code_key; verifica variedade, inclusive quando lista é vazia. |
| markers.create | variety_id e MarkerInput(code, value) | Marcador salvo; atribui source fixo e valida unicidade dentro da variedade. |
| markers.update | marker_id e MarkerInput completo | Mantém ID, variety_id e source; atualiza somente código e valor. |
| markers.delete | marker_id | Remove somente marcador existente; UI já obteve confirmação. |
| comparison.compare | left_id, right_id | ComparisonResult com dados atuais, tabela de cinco campos e DataFrame de marcadores alinhados por chave; IDs distintos e existentes. |
| dashboard.summarize | Sem filtros | DashboardSummary com os três totais e três categorias de tamanho, inclusive zeros. |

Criação/edição só retorna sucesso depois do commit. Exclusão retorna conclusão apenas após commit; registro inexistente não é tratado como sucesso. A UI pode compor get e markers.list para detalhes; comparação e resumo devem obter seus dados numa única leitura consistente no repositório.

## Erros

| Erro | Contexto | Resposta na UI |
| --- | --- | --- |
| ValidationError | Tipo, campo vazio, limite, formato ou categoria inválida; contém erros por campo. | Mensagem junto ao campo e rascunho preservado. |
| DuplicateError | Nome ou código já registrado no escopo correspondente. | Indicar duplicidade e permitir correção, sem commit. |
| NotFoundError | ID excluído/inexistente, marcador inexistente ou variedade de destino ausente. | Orientar nova seleção; não criar substituto. |
| InvalidComparisonError | Seleção incompleta ou IDs iguais. | “Selecione duas variedades distintas.” |
| StorageError | Falha de leitura, escrita, bloqueio, arquivo ou acesso. | “Não foi possível acessar/salvar os dados. Verifique o acesso e tente novamente.” Sem confirmação de sucesso. |
| IncompatibleDatabaseError | Versão, estrutura ou conteúdo não reconhecido. | Informar incompatibilidade e preservar arquivo; não reinicializar. |

Repositórios encapsulam exceções sqlite3 e garantem rollback/close. Violações reconhecidas de unicidade e relacionamento são mapeadas para domínio; falhas inesperadas de integridade não são ocultadas como validação bem-sucedida. Causas técnicas são registradas localmente no terminal; nunca exibir traceback nos fluxos de erro previstos.

## Contrato de dependência de dados

Repositórios de variedades e marcadores oferecem CRUD e buscas de unicidade; um componente de consulta oferece comparação e agregações. SQL fica somente em potatogene/data. Entradas de escrita incluem chaves calculadas pelo negócio; o repositório não aceita parâmetros arbitrários de SQL. Uma conexão local por operação, com foreign_keys habilitado, escrita transacional e fechamento garantido.

Serviços podem receber um substituto com as mesmas operações nos testes unitários. Não é necessário criar uma hierarquia abstrata ou framework de injeção. Leituras compostas são operações específicas do repositório, evitando chamadas separadas que produzam snapshots diferentes.

As regras completas e estruturas persistentes estão em [data-model.md](../data-model.md). Ausência de marcador nunca vira ausência biológica, e nenhuma operação calcula parentesco, resistência ou desempenho da batata.
