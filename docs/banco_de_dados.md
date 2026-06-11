# Modelagem do Banco de Dados

O banco de dados utilizado é o **SQLite3**, configurado e operado localmente através do arquivo `tcc_assistant.db`. 

## 1. Schema do Banco de Dados

O banco é dividido essencialmente em duas tabelas que formam um relacionamento lógico (Um-Para-Muitos).

### Tabela `projects`
Guarda os dados contextuais da avaliação, incluindo quem é o autor do TCC e qual arquivo PDF está atrelado a ele.

| Coluna | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Chave primária do projeto. |
| `student_name` | TEXT | NOT NULL | Nome do aluno/autor. |
| `thesis_title` | TEXT | NOT NULL | Título da monografia. |
| `advisor_name` | TEXT | DEFAULT '' | Nome do orientador do trabalho. |
| `advisor_email`| TEXT | DEFAULT '' | E-mail do orientador (usado para envio automático). |
| `pdf_path` | TEXT | NOT NULL | Caminho absoluto para o arquivo PDF na máquina local. |
| `general_opinion`| TEXT | DEFAULT '' | Texto descritivo final (Parecer geral) do avaliador. |
| `status` | TEXT | DEFAULT 'In Progress' | Estado da avaliação ('In Progress', 'Concluído'). |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Data da última interação ou edição no projeto. |

### Tabela `annotations`
Cada registro aponta uma correção, sugestão ou comentário feito pelo professor em cima de uma página e um trecho textual.

| Coluna | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Chave primária da anotação. |
| `project_id` | INTEGER | NOT NULL, FK | Refere-se à tabela `projects`. Possui `ON DELETE CASCADE`. |
| `page_number` | INTEGER | NOT NULL | Página literal dentro do PDF na qual ocorreu o apontamento. |
| `selected_text`| TEXT | - | Trecho do texto extraído pelo "Rubber Band" (caixa) do PyMuPDF. |
| `category` | TEXT | - | "Apontamentos", "Dúvida" ou "Sugestão". |
| `professor_notes`| TEXT | - | Redação elaborada pelo avaliador apontando a correção/crítica. |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Data da criação da anotação. |

---

## 2. Padrões de Acesso aos Dados

Para viabilizar a UI reativa, criamos os seguintes padrões de persistência:

### Row Factories
No `database.py`, as requisições SELECT utilizam `sqlite3.Row` na configuração do cursor (`conn.row_factory = sqlite3.Row`). Isso força o banco a retornar as tuplas não por index numérico (`row[0]`), mas convertidas para mapeamento estilo dicionário (`row['student_name']`), melhorando absurdamente a legibilidade do frontend no `main.py`.

### Timestamps Automatizados e Cascatas
Sempre que uma Anotação for atualizada (`update_annotation`), adicionada (`add_annotation`) ou excluída (`delete_annotation`), uma trigger invisível de negócio (via SQL UPDATE secundário na mesma transação) garante que o `updated_at` do projeto mãe receba um "touch" (`get_brt_time()`). Isso garante que, na lista de dashboard, os projetos mais recentemente mexidos sempre flutuem para o topo.

A exclusão física do arquivo (`delete_project()`) apaga recursivamente todas as anotações do projeto devido ao pragma habilitado (`PRAGMA foreign_keys = ON`) atrelado à chave estrangeira `ON DELETE CASCADE`.
