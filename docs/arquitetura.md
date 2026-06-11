# Arquitetura de Software

Este documento descreve as decisões arquiteturais e a divisão de módulos do **Assistente de Revisão de TCC**. A arquitetura foi pensada de maneira modular, separando a interface gráfica da lógica de persistência e do motor de validação de citações.

## Visão Geral do Sistema

O sistema segue o padrão conceitual **Model-View-Controller (MVC)** de forma adaptada para aplicações desktop:
- **Model**: Módulo `database.py` (Gerencia banco de dados e objetos de negócio).
- **View/Controller**: Módulo `main.py` (Lida com o layout PyQt6 e reage às ações do usuário em tela).
- **Core Engine (Serviço)**: Módulo `validador_citacoes.py` (Lógica de processamento de texto e expressões regulares).

## Pilha Tecnológica (Tech Stack)

1. **Python 3.x**: Linguagem base escolhida pela vasta disponibilidade de bibliotecas de processamento de texto e dados.
2. **PyQt6**: Framework escolhido para a UI por oferecer suporte robusto a controles customizados (QSS), multithreading e visualização de canvas de PDF (`QGraphicsScene`).
3. **PyMuPDF (`fitz`)**: Motor de PDF ultra-rápido para leitura do documento em tela e extração de coordenadas de texto.
4. **SQLite3 (`database.py`)**: Banco de dados relacional embarcado, garantindo que o app possa ser usado offline sem instalações pesadas.
5. **python-docx / QPdfWriter**: Bibliotecas responsáveis pela geração e exportação de relatórios locais (.docx e .pdf).
6. **Pandas / Openpyxl**: Exportação e modelagem das planilhas de relatórios de validação de citação em `.xlsx`.

## Descrição dos Módulos

### 1. `main.py` (Interface Gráfica e Lógica de Fluxo)
Este é o ponto de entrada da aplicação (`entry point`). Responsável por instanciar a `QApplication`.
- **`TCCAssistantApp` (QMainWindow)**: Classe principal que gerencia o estado da navegação. Controla o que é exibido no painel central (Dashboard de Projetos vs. Workspace de Revisão).
- **`PDFViewer` (QGraphicsView)**: Um componente customizado herdado do Qt. Ele gerencia o carregamento de páginas do PyMuPDF, rasteriza-as como `QPixmap` e desenha na tela. Implementa também a seleção com "Rubber Band" e a extração de texto via caixa delimitadora (`get_textbox()`).
- **Exportação e E-mail**: Utiliza bibliotecas internas como `smtplib` em junção com o parser DOCX/QTextDocument para formatar os anexos e submeter vias de e-mail ao orientador configurado no projeto.

### 2. `database.py` (Persistência)
Camada isolada para lidar com requisições SQL. Garante que os formulários e listas da UI possam carregar dados limpos em formato de dicionários (`sqlite3.Row`).
- Gerencia duas entidades fundamentais: **Projetos** (metadados do aluno, orientador, caminhos) e **Anotações** (vínculo 1:N com Projeto, armazenando recortes, páginas e anotações do revisor).
- Possui uma lógica simples de **migrations** no `init_db()` usando `PRAGMA table_info` para criar dinamicamente novas colunas (como `advisor_email` caso não existam).

### 3. `validador_citacoes.py` (Motor de Expressões Regulares)
Este arquivo é puramente focado em extração de NLP/Regex. Ele processa PDFs inteiros de maneira invisível ao usuário.
- **Extração da Bibliografia**: Navega nas páginas do documento de trás para frente até identificar a seção "REFERÊNCIAS". Isola o conteúdo e corta com segurança ao encontrar blocos delimitadores como "ANEXO" ou "APÊNDICE".
- **Busca por Padrões**: Utiliza RegEx compiladas (`pattern1`, `pattern2`) para capturar chamadas no texto como `Autor (Ano)` ou `(AUTOR, Ano)`.
- **Heurística de Ignorar Falsos Positivos**: Ignora citações vindas de imagens e tabelas (ex: "Fonte: Autor (2023)") graças a regras explícitas (verifica listas de palavras restritas como "AUTOR", "AUTORAL").
- **Cruzamento e Score**: Realiza o match entre a autoria/ano extraída das chamadas em texto contra a string completa da lista de referências. Produz um payload tabular mapeando '✅ OK', '❌ FALTA NA BIBLIOGRAFIA' e 'ℹ️ SOBRANDO'.

---

## Estrutura de Diretórios
```text
/tcc_analizer
│
├── main.py                   # Ponto de entrada e Interface Gráfica
├── database.py               # Manipulação do SQLite
├── validador_citacoes.py     # Motor Regex de validação ABNT
├── tcc_assistant.db          # Arquivo SQLite gerado localmente
├── .env                      # Variáveis de ambiente (SMTP)
├── README.md                 # Guia rápido
│
└── docs/                     # Documentação de arquitetura e uso
    ├── arquitetura.md
    ├── banco_de_dados.md
    ├── diagramas.md
    ├── tutorial_uso_ui.md
    └── spec.md
```
