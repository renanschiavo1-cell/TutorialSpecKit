# Execução e validação no Windows — PotatoGene

Este guia descreve os comandos e cenários a executar **após a implementação**. Nesta fase foram criados apenas documentos; app.py, requirements e testes ainda serão entregues. Referências: [plano](plan.md), [modelo de dados](data-model.md), [UI](contracts/ui.md) e [serviços](contracts/services.md).

## Pré-requisitos

- Windows, PowerShell, navegador local e Python 3.11 ou superior, preferencialmente 64 bits.
- Para validação mínima, Python 3.11 instalado; a baseline também deverá ser testada em Python 3.14. Registrar versões efetivamente testadas no README.
- Acesso de gravação à pasta do catálogo. Instalação inicial precisa obter pacotes; o aplicativo instalado não exige internet, conta, hospedagem ou servidor de banco.

## Preparar o ambiente

No PowerShell, na raiz do projeto:

```powershell
Set-Location C:\Users\renan\TutorialSpecKit
py -3.11 --version
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m pytest -m "not performance"
```

Usar requirements.txt para instalação somente de execução. requirements-dev.txt contém também execução e pytest. Se for usada outra versão instalada e já validada, substituir `py -3.11` pela versão correspondente; o mínimo permanece 3.11. Não usar `pip` de outro Python. Chamar o executável do venv dispensa ativação e mudança da política de execução do PowerShell.

Resultado esperado: instalação sem conflito, pip check aprovado e suíte sem falhas. Os locks completos serão produzidos e validados durante a implementação, conforme [research.md](research.md).

## Executar

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true --browser.gatherUsageStats false
```

Abrir `http://127.0.0.1:8501` no navegador. Encerrar com Ctrl+C no terminal. As mesmas configurações deverão constar em .streamlit/config.toml para permitir execução curta com `python -m streamlit run app.py`. O servidor e SQLite funcionam na máquina do usuário.

Primeiro uso: criar automaticamente data/potatogene.db com esquema versão 1 e catálogo vazio. Usos seguintes: preservar e validar o arquivo existente. O caminho é relativo à raiz do projeto, não ao diretório de trabalho. Não excluir arquivo para resolver erro de acesso ou incompatibilidade.

## Usar um catálogo separado para avaliação

Para não modificar registros reais, usar um caminho novo de avaliação antes de iniciar o aplicativo:

```powershell
$env:POTATOGENE_DB_PATH = Join-Path $env:TEMP 'potatogene-avaliacao-mvp.db'
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.headless true --browser.gatherUsageStats false
```

Se esse arquivo já tiver dados, escolher outro nome para o cenário de catálogo vazio, sem apagá-lo automaticamente. Ao encerrar a avaliação, restaurar o caminho padrão no terminal:

```powershell
Remove-Item Env:POTATOGENE_DB_PATH -ErrorAction SilentlyContinue
```

Os testes automatizados usam tmp_path próprio e substituem o caminho **antes** da inicialização, independentemente dessa configuração manual; não usam o catálogo real.

## Roteiro de aceitação

1. **Catálogo vazio e inicialização** — Abrir um caminho novo: listagem orienta cadastro; dashboard tem todos os valores zero; comparação orienta cadastrar duas variedades. Reabrir não recria registros nem exemplos (US1.1, US2.6, US5.2).
2. **Cadastro** — Criar “Ágata Demo”, origem “Brasil”, casca “Amarela”, polpa “Creme”, tamanho Pequeno; “Asterix Demo”, “Desconhecida”, “Vermelha”, “Amarela”, Médio; “Batata Roxa Demo”, “Exemplo educacional”, “Roxa”, “Roxa”, Grande. São dados inventados para o teste, sem afirmação científica. Conferir os cinco campos e listagem ordenada (US1.2).
3. **Validação e edição** — Tentar nome vazio, espaços, 101 caracteres e “ áGATA dEMO ”. Ver mensagens e rascunhos preservados, sem novo registro. Aceitar limites da tabela da spec; testar todos os campos, tipos/controles nos serviços e categorias inválidas. Editar origem de Ágata Demo, salvar e cancelar outra edição; identidade permanece (US1.3, US2.2–3).
4. **Marcadores** — Adicionar MK-01=A e MK-02=B à primeira variedade e mk-01=C à segunda; terceira permanece sem marcadores. Conferir origem “Demonstrativo — exemplo educacional” em todos. Código repetido na mesma variedade é rejeitado; em outra é permitido. Editar valor, cancelar edição, cancelar remoção e confirmar remoção de um marcador temporário; variedade permanece (US3).
5. **Comparação** — Comparar primeira e segunda: cinco campos completos; MK-01/mk-01 alinhados, valores preservados; MK-02 ausente à direita como “Não registrado”; origem visível. Comparar com a terceira sem marcadores, tentar IDs iguais/seleção incompleta e verificar orientação. Não há conclusões biológicas ou ranking (US4).
6. **Dashboard** — Antes de alterações adicionais, conferir 3 variedades, 3 marcadores, 2 variedades com marcadores, uma em cada tamanho. Mudar o tamanho e verificar nova distribuição, preservando totais. Cancelamentos não alteram os indicadores (US5).
7. **Persistência e exclusão** — Encerrar e reabrir dez vezes após operações confirmadas; conferir os dados. Cancelar exclusão da primeira variedade: ela e seus marcadores permanecem. Confirmar: ambos desaparecem, dashboard atualiza e seleção antiga da comparação exige nova escolha. Excluir restantes confirma estado vazio e zeros (US1.4, US2.1, US4.4, US5.3).
8. **Falhas** — Executar testes de arquivo inválido/incompatível, leitura indisponível e falha de escrita/commit. Esperar mensagens controladas, nenhum sucesso falso, rollback integral e arquivo preservado; não transformar falha de leitura em catálogo vazio. Usar somente arquivos temporários e injeção de falhas, nunca corromper banco real (US2.4–5).
9. **Offline e português** — Após instalar pacotes, desativar acesso externo à internet mantendo loopback e repetir fluxos essenciais no navegador. Inspecionar rótulos, mensagens e controles, incluindo auxiliares das tabelas: português e ausência de rastreamentos técnicos (US2.6–7).

## Comandos de testes

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit tests/integration tests/ui
.\.venv\Scripts\python.exe -m pytest -m performance
```

pytest.ini deve registrar marker performance para não emitir aviso. Os testes de desempenho são separados porque dependem do equipamento; executar o conjunto completo pertinente antes de integrar a entrega. Para validar compatibilidade adicional, repetir instalação limpa, pip check e suíte em venv separado com Python 3.14, sem modificar o ambiente de referência 3.11.

## Evidências dos critérios de sucesso

| Critério | Evidência a registrar |
| --- | --- |
| SC-001 | Cinco participantes, conclusão de CRUD sem intervenção; pelo menos quatro concluem em até cinco minutos. |
| SC-002 | Catálogo temporário de 100 variedades e 2.000 marcadores; vinte consultas de cada fluxo; pelo menos dezenove por fluxo em até dois segundos, medidos da submissão ao resultado visível. Registrar equipamento e versões. |
| SC-003 | Dez ciclos de reabertura e comparação integral com o último estado confirmado. |
| SC-004 | Suíte parametrizada de validação/limites e falhas com rollback, sem alteração parcial. |
| SC-005 | Conferência de contagens e comparação em catálogo vazio e após cadastro, edição, exclusão, falha e cancelamento. |
| SC-006 | Pelo menos quatro de cinco participantes explicam a natureza demonstrativa e a impossibilidade de inferir biologia. |
| SC-007 | Fluxos concluídos offline e revisão das mensagens portuguesas previstas. |

AppTest e pytest não substituem a avaliação com participantes nem a medição de tempo percebido no navegador. Registrar resultados reais antes de declarar a implementação concluída.
