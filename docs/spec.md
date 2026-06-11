# Especificação Completa do TCC Analyzer

## 1. Visão Geral
O **TCC Analyzer** (Assistente de Revisão de TCC) é um aplicativo desktop construído em Python, com interface gráfica utilizando **PyQt6**, projetado para auxiliar professores e membros de bancas examinadoras na revisão e avaliação de Trabalhos de Conclusão de Curso (TCC) em formato PDF.

O aplicativo permite a leitura e navegação do PDF diretamente na ferramenta, seleção de trechos com captura automática de texto e a criação de anotações categorizadas que podem ser posteriormente exportadas para um documento Word (.docx) formatado.

---

## 2. Tecnologias Utilizadas
- **Linguagem:** Python 3
- **Interface Gráfica (GUI):** PyQt6
- **Leitura e Processamento de PDF:** PyMuPDF (`fitz`)
- **Banco de Dados:** SQLite (`sqlite3`)
- **Geração de Relatórios:** python-docx (`docx`)
- **Análise de Dados e Exportação:** pandas (`pd`), openpyxl (exportação para `.xlsx`)

---

## 3. Arquitetura do Sistema
O projeto é dividido em arquivos e módulos principais:
- `main.py`: Contém toda a lógica de Interface de Usuário (UI), componentes PyQt6 (Dialogs, MainWindow), o visualizador de PDF (QGraphicsView customizado) e as integrações de eventos.
- `database.py`: Módulo responsável pela interação com o banco de dados SQLite (`tcc_assistant.db`), provendo um modelo CRUD (Create, Read, Update, Delete) para Projetos e Anotações.
- `validador_citacoes.py`: Módulo autônomo (CLI) responsável pela extração das referências e validação de citações no formato ABNT com base no texto do PDF, com relatórios em planilhas.
- `iniciar_tcc_analizer.bat`: Script em lote do Windows usado para inicializar rapidamente a aplicação.

### Modelo de Dados
O banco de dados possui duas tabelas:
1. **projects:** 
   - `id` (PK), `student_name`, `thesis_title`, `pdf_path`, `general_opinion`, `status`, `updated_at`.
2. **annotations:** 
   - `id` (PK), `project_id` (FK -> projects.id), `page_number`, `selected_text`, `category`, `professor_notes`, `created_at`.

A exclusão de um projeto tem efeito cascata (CASCADE) sobre as suas anotações, e modificações nas anotações atualizam a data de `updated_at` do projeto associado.

---

## 4. Funcionalidades Principais

### 4.1. Painel de Controle (Dashboard)
A tela inicial lista todos os projetos de revisão cadastrados.
- **Nova Revisão:** Abre um formulário para criar um novo projeto informando Nome do Aluno, Título do TCC e o caminho do arquivo PDF correspondente.
- **Abrir Revisão:** Abre a área de trabalho (Workspace) do projeto selecionado.
- **Excluir Revisão:** Apaga o projeto selecionado e todas as suas anotações do banco de dados (solicita confirmação prévia).
- **Lista de Projetos:** Tabela interativa exibindo ID, Nome, Título, Status (ex: "Em Andamento") e Data da última atualização.

### 4.2. Área de Trabalho (Workspace)
A área de trabalho é dividida em duas colunas (usando `QSplitter`), priorizando o layout 65% para o PDF e 35% para anotações.

#### Visualizador de PDF (Esquerda)
- Renderiza as páginas do PDF como imagens (QPixmap) em um QGraphicsScene.
- Controles disponíveis: Zoom In (🔍+), Zoom Out (🔍-), Página Anterior (⬅️), Próxima Página (➡️), além de um campo de entrada numérico para salto direto de página.
- **Seleção de Texto Inteligente:** Ao arrastar o mouse criando uma caixa de seleção (Rubber Band) sobre o PDF, a área selecionada é mapeada, e o texto presente nela é extraído automaticamente pelo PyMuPDF. Este texto capturado, junto ao número da página atual, é enviado automaticamente para o painel de anotações à direita.

#### Painel de Anotações (Direita)
- **Cabeçalho:** Exibe informações do aluno e título do projeto.
- **Formulário de Anotação:**
  - **Categorias:** Abas coloridas indicando "Apontamentos" (Vermelho), "Dúvida" (Amarelo) e "Sugestão" (Azul).
  - **Página e Trecho:** Podem ser preenchidos automaticamente pela seleção no visualizador ou digitados manualmente. Os campos forçam formatação em **texto simples** (`QPlainTextEdit`) para evitar colagens indesejadas ricas em formatação de fontes externas.
  - **Observação:** Campo livre para o professor digitar comentários (também em texto simples).
  - **Ações:** Botões para "Salvar Anotação" (ou "Atualizar Anotação", se em modo de edição) e "Cancelar Edição".
- **Lista de Anotações:**
  - Tabela exibindo a Página, Categoria e um resumo do Trecho de todas as anotações feitas no projeto.
  - **Edição e Exclusão:** Selecionando uma anotação na lista, o usuário pode clicar em "Editar Selecionada" (que devolve os dados para o formulário superior) ou "Excluir Selecionada" (remove a anotação).
- **Parecer Geral:**
  - Área de texto para avaliação global do projeto. Possui recurso de *Auto-save* com atraso (debounced) de 2 segundos após a digitação.
- **Exportação e Saída:**
  - **Exportar Relatório:** Abre a janela `ExportDialog`, permitindo que o usuário informe o "Nome do Avaliador", selecione uma data e escolha o formato de saída (**PDF (.pdf)** ou **Word (.docx)**). 
    - O relatório é formatado de forma padronizada.
    - O PDF é gerado nativamente pelo `QPdfWriter` do PyQt6 (sem necessidade de conversores externos).
    - O documento final inclui uma seção de rodapé com o nome do avaliador escrito em uma **fonte cursiva**, servindo como uma assinatura digital.
  - **Salvar Rascunho e Sair:** Retorna o usuário para o Dashboard principal.

### 4.3. Validação Automática de Citações (CLI)
Através do script autônomo `validador_citacoes.py`, o projeto oferece uma ferramenta complementar (via linha de comando) para automatizar a verificação das normas ABNT no texto do PDF:
- **Extração de Referências:** Identifica automaticamente a seção de "REFERÊNCIAS BIBLIOGRÁFICAS" no final do PDF e isola cada entrada bibliográfica.
- **Identificação de Citações:** Utiliza expressões regulares (RegEx) para localizar citações no formato ABNT ao longo do texto (ex: `(AUTOR, 2023)` ou `Autor (2023)`), filtrando menções a "próprio autor".
- **Cruzamento e Verificação:** Relaciona as citações mapeadas ao longo do documento com a lista de referências ao final.
- **Relatório Detalhado:** Identifica citações sem referência ("Falta na Bibliografia"), citações corretas ("OK"), e referências presentes no final mas não citadas no texto ("Sobrando"). Exporta todos os resultados com o contexto do parágrafo e página para um arquivo Excel (`.xlsx`) ou `.csv`.

---

## 5. Interface Gráfica e UX
O sistema utiliza um tema QSS (Qt Style Sheets) embutido no código chamado `DARK_GLASS_QSS`, caracterizado por:
- Design *Dark Mode* (#0b0f19 background).
- Efeitos visuais de vidro fosco para contêineres e tabelas.
- Botões estilizados e responsivos (verde para criação, azul para neutro/edição, vermelho para cancelamento/exclusão, laranja para ações de salvar/navegação).
- Layout fluido ajustável pela alça do `QSplitter`.

## 6. Fluxo de Execução
1. O aplicativo chama `db.init_db()` na inicialização do programa, garantindo que o SQLite database e as tabelas existam.
2. É renderizada a `QMainWindow` principal inicializada pelo `init_dashboard()`.
3. Caso o usuário crie ou selecione abrir um projeto, a janela troca os widgets chamando `init_workspace(project_id)`.
4. Os salvamentos de anotações disparam transações isoladas (`update_annotation`, `add_annotation`, `delete_annotation`), enquanto o Parecer Geral usa um temporizador em background (`autosave_timer`).
5. A exportação coleta as preferências do usuário no `ExportDialog` e converte a base relacional local para gerar um HTML renderizado como PDF (pelo motor do PyQt6) ou chama a biblioteca `python-docx` gerando o arquivo Word localmente.
