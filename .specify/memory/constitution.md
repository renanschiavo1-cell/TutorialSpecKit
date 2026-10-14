<!--
Sync Impact Report
Versão: modelo sem versão → 1.0.0 (adoção inicial).
Princípios modificados: os cinco espaços genéricos foram substituídos pelos nove
princípios específicos do PotatoGene, listados em Core Principles.
Seções adicionadas: Restrições e escopo educacional; Fluxo de desenvolvimento e revisão.
Governance preenchida com procedimento de emenda, versionamento e revisão de conformidade.
Seções removidas: nenhuma seção estrutural; apenas exemplos e espaços do modelo.
Pendências e TODOs: nenhum. Templates dependentes não foram modificados.
Este relatório é temporário e deve ser removido antes do commit da constituição.
-->

# PotatoGene Constitution

## Core Principles

### I. Python 3.11 ou superior

O sistema DEVE ser desenvolvido em Python e executado com Python 3.11 ou superior.
A versão mínima e as dependências DEVEM estar documentadas. Dependências adotadas DEVEM
ser compatíveis com a versão mínima declarada, permitindo instalação reproduzível.

### II. Código modular, organizado e documentado

O código DEVE ser organizado em módulos com responsabilidades claras, nomes descritivos
e organização consistente. Funções públicas, regras de domínio e decisões não evidentes
DEVEM ter documentação suficiente para explicar seu uso e suas restrições. A documentação
DEVE explicar instalação, execução, testes e organização dos módulos, facilitando o
aprendizado e a manutenção.

### III. Interface simples em português

A interface DEVE usar português em rótulos, instruções, mensagens de validação e erros.
Os fluxos essenciais DEVEM apresentar ações claras e solicitar apenas informações
necessárias à operação. Termos genéticos DEVEM ter explicações acessíveis quando
necessárias à compreensão; identificadores científicos podem manter sua grafia original.
A modalidade de interface DEVE ser escolhida pela simplicidade exigida pelo MVP.

### IV. Persistência local com SQLite

Os dados persistentes DEVEM ser armazenados localmente em SQLite, sem exigir servidor de
banco de dados ou serviço externo para as operações essenciais. O acesso DEVE usar consultas
parametrizadas, restrições de integridade e transações para operações que exijam atomicidade.
Conexões DEVEM ser encerradas adequadamente. O local do arquivo e o procedimento de
inicialização do banco DEVEM estar documentados.

### V. Validação de entradas e tratamento de erros

Entradas DEVEM ser validadas quanto a obrigatoriedade, tipo, formato e limites definidos
pelas regras de domínio antes da persistência. As regras de negócio DEVEM validar seus
próprios invariantes, independentemente da interface. Erros esperados de entrada e acesso
a dados DEVEM ser tratados com mensagens claras em português, sem expor rastreamentos
técnicos ao usuário. Falhas NÃO DEVEM ser silenciadas nem deixar gravações parciais.

### VI. Testes automatizados com pytest

O projeto DEVE utilizar pytest para testes automatizados. Regras de negócio, validações,
tratamento de falhas e persistência SQLite DEVEM ter testes com casos válidos, inválidos
e limites relevantes. Testes de persistência DEVEM usar bancos temporários ou em memória,
sem alterar dados reais do usuário. Correções de defeitos DEVEM incluir testes de regressão
quando o comportamento for automatizável. A suíte DEVE passar antes de integrar alterações,
e seu comando de execução DEVE estar documentado.

### VII. Separação de responsabilidades

A arquitetura DEVE separar interface, regras de negócio e acesso a dados. A interface
DEVE coletar entradas e apresentar resultados; a camada de negócio DEVE aplicar as regras
do domínio; a camada de dados DEVE encapsular SQLite e as operações de persistência.
A interface NÃO DEVE executar SQL nem concentrar regras de domínio. As regras de negócio
NÃO DEVEM depender de detalhes de apresentação e DEVEM poder ser testadas isoladamente,
sem exigir uma interface em execução ou um banco real do usuário.

### VIII. Integridade científica dos dados genéticos

Marcadores genéticos DEVEM ser demonstrativos ou informados pelo usuário, com essa origem
identificada no registro e na apresentação. Dados demonstrativos DEVEM ser sinalizados
como exemplos educacionais. Dados fornecidos pelo usuário NÃO DEVEM ser apresentados como
cientificamente validados apenas por terem sido cadastrados.

O sistema NÃO DEVE inferir características biológicas de variedades de batata a partir
de marcadores sem evidências científicas documentadas e pertinentes à relação apresentada.
Qualquer associação biológica exibida DEVE indicar sua fonte, contexto e limitações.
Na ausência de evidência, o sistema DEVE limitar-se a registrar e apresentar os dados,
sem converter exemplos ou informações não verificadas em conclusões biológicas.

### IX. MVP simples e funcional

O desenvolvimento DEVE priorizar o menor conjunto de funcionalidades que permita cumprir
o objetivo educacional de controlar informações genéticas de variedades de batata.
Cada funcionalidade DEVE ter um objetivo de usuário e critérios de aceitação definidos.
Dependências, abstrações e recursos adicionais DEVEM ter justificativa ligada a uma
necessidade atual do MVP. Melhorias sem essa necessidade DEVEM ser adiadas. A simplicidade
NÃO DEVE eliminar validação, testes, integridade dos dados ou rigor científico.

## Restrições e escopo educacional

PotatoGene é um sistema educacional de controle de informações genéticas de variedades
de batata. O escopo de cada entrega DEVE distinguir dados cadastrais, marcadores e
eventuais associações científicas, preservando a origem das informações.

As operações essenciais DEVEM funcionar com Python 3.11 ou superior e SQLite local.
A especificação do MVP DEVE definir os campos, as operações e as validações necessárias;
esta constituição não estabelece uma interface específica nem amplia o escopo funcional.
Dados de exemplo DEVEM permanecer identificáveis como demonstrativos durante todo o fluxo.

## Fluxo de desenvolvimento e revisão

Cada mudança DEVE partir de requisitos e critérios de aceitação compatíveis com esta
constituição. O planejamento DEVE indicar a responsabilidade de cada camada e as
validações, operações de persistência e testes necessários ao comportamento proposto.

A revisão antes da integração DEVE verificar:

- Compatibilidade com Python 3.11 ou superior e documentação atualizada.
- Separação entre interface, negócio e dados.
- Clareza e uso de português nos fluxos e mensagens da interface.
- Validação de entradas, tratamento de falhas e integridade da persistência SQLite.
- Execução bem-sucedida dos testes pertinentes com pytest.
- Identificação da origem dos marcadores e evidências de associações biológicas exibidas.
- Necessidade de cada recurso e dependência para o MVP.

Desvios DEVEM ser corrigidos antes da integração ou tratados por uma emenda formal à
constituição. Alterações no formato persistido DEVEM documentar seu impacto nos dados
existentes e o procedimento necessário para preservá-los.

## Governance

Esta constituição prevalece sobre especificações, planos e práticas de desenvolvimento
do PotatoGene. Todas as entregas DEVEM demonstrar conformidade com seus princípios nos
critérios de aceitação e na revisão, inclusive quando o trabalho for realizado individualmente.

Emendas DEVEM registrar a motivação, os princípios afetados, o impacto sobre os artefatos
e dados existentes e, quando aplicável, a forma de adequação. O responsável pelo projeto
DEVE aprovar a emenda antes de sua adoção. A atualização DEVE ajustar a versão e a data
da última alteração, preservando a data de ratificação original.

O versionamento DEVE seguir MAJOR.MINOR.PATCH: MAJOR para remoções ou redefinições
incompatíveis de princípios ou governança; MINOR para novos princípios, seções ou ampliações
materiais; PATCH para esclarecimentos e correções sem mudança normativa. A versão 1.0.0
representa a adoção inicial desta constituição.

Após uma emenda, especificações, planos e tarefas afetados DEVEM ser revisados quanto à
conformidade antes de orientar novas implementações. Toda revisão de mudança DEVE verificar
o cumprimento dos princípios e justificar qualquer complexidade adicionada.

**Version**: 1.0.0 | **Ratified**: 2026-10-13 | **Last Amended**: 2026-10-13
