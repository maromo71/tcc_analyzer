# Diagramas do Assistente de Revisão de TCC

Este documento apresenta diagramas que explicam a arquitetura e o fluxo de funcionamento profundo do **Assistente de Revisão de TCC**, incluindo UI, Banco de Dados e a Motor de Validação.

## 1. Diagrama de Casos de Uso

Representa as principais interações que o Avaliador (usuário) tem com o sistema.

```mermaid
flowchart LR
    Avaliador((Avaliador))
    
    subgraph Sistema [Assistente de Revisão de TCC]
        direction TB
        UC1([Gerenciar Projetos de Revisão])
        UC2([Visualizar e Dar Zoom em PDF])
        UC3([Selecionar Trechos do PDF])
        UC4([Criar/Editar/Excluir Anotações])
        UC5([Redigir Parecer Geral])
        UC6([Exportar Relatório PDF/DOCX])
        UC7([Enviar Avaliação por E-mail])
        UC8([Validar Citações da ABNT])
    end

    Avaliador --> UC1
    Avaliador --> UC2
    Avaliador --> UC3
    Avaliador --> UC4
    Avaliador --> UC5
    Avaliador --> UC6
    Avaliador --> UC7
    Avaliador --> UC8
    
    UC3 -.->|Alimenta| UC4
```

## 2. Diagrama de Atividades: Fluxo Principal do Avaliador

Mostra o fluxo de trabalho típico, desde abrir o projeto até o envio do relatório.

```mermaid
flowchart TD
    Start([Início]) --> OpenProject[Abrir ou Criar Projeto]
    OpenProject --> ViewPDF[Navegar pelo PDF]
    ViewPDF --> FoundIssue{Encontrou erro/dúvida?}
    
    FoundIssue -- Sim --> SelectText[Selecionar área com texto no PDF]
    SelectText --> AutoFill[Sistema extrai texto automaticamente via PyMuPDF]
    AutoFill --> FillNotes[Digitar notas e sugestões do Professor]
    
    FillNotes --> ChooseCategory[Escolher Categoria]
    ChooseCategory --> SaveAnnotation[Salvar no SQLite]
    SaveAnnotation --> MoreIssues{Continuar revisando?}
    
    FoundIssue -- Não --> MoreIssues
    MoreIssues -- Sim --> ViewPDF
    
    MoreIssues -- Não --> WriteOpinion[Escrever Parecer Geral do TCC]
    WriteOpinion --> Validate{Validar Citações ABNT?}
    
    Validate -- Sim --> RunVal[Cruza texto vs. bibliografia]
    RunVal --> Export[Exportar / Enviar E-mail]
    Validate -- Não --> Export
    
    Export --> End([Fim da Avaliação])
```

## 3. Diagrama de Sequência: Motor Inteligente de Validação de Citações

Detalha como funciona o cruzamento entre as chamadas do texto vs a lista de referências quando o avaliador pressiona o botão de Validação.

```mermaid
sequenceDiagram
    actor Avaliador
    participant UI as TCCAssistantApp
    participant Val as validador_citacoes.py
    participant Fitz as PyMuPDF (fitz)
    
    Avaliador->>UI: Clica em "Validar Citações"
    UI->>Val: run_validation(pdf_path)
    
    Val->>Fitz: Abre PDF e varre as páginas
    Fitz-->>Val: Páginas de texto brutas
    
    Val->>Val: find_references_section()<br>(Separa Corpo vs Referências)
    Note right of Val: Procura de trás pra frente por 'REFERÊNCIAS'.<br>Isola blocos de "ANEXOS" se existirem.
    
    Val->>Val: parse_references()<br>(Gera lista de bibliografia)
    
    Val->>Val: find_citations_in_body()<br>(Extrai Autor/Ano via RegEx)
    Note right of Val: Ignora falsos positivos (Autor, Autores)<br>Comuns em subtítulos de figuras.
    
    Val->>Val: match_citations()<br>(Cruza Autoria com Referências)
    Val-->>UI: Retorna Lista com status (✅/❌/ℹ️)
    
    UI-->>Avaliador: Exibe modal com grid (Tabela)
```

## 4. Diagrama de Sequência: Exportação e Envio de E-mail

```mermaid
sequenceDiagram
    actor Avaliador
    participant UI as ExportDialog
    participant DOCX as python-docx / QPdfWriter
    participant SMTP as SMTP (email.message)
    participant DB as database.py

    Avaliador->>UI: "Enviar por E-mail"
    UI->>UI: Verifica E-mail do Orientador (DB)
    UI->>Avaliador: Solicita Formato, Data e Nome
    Avaliador->>UI: Confirma
    
    UI->>DB: get_annotations()
    DB-->>UI: Lista de Anotações do Avaliador
    
    alt PDF Escolhido
        UI->>DOCX: Gera HTML e printa QPdfWriter (tmp)
    else DOCX Escolhido
        UI->>DOCX: Constrói documento Word (tmp)
    end
    
    UI->>SMTP: Conecta via TLS (porta 587)
    UI->>SMTP: Anexa o Parecer + Planilha de Citações
    SMTP-->>UI: E-mail enviado com Sucesso
    UI-->>Avaliador: Notificação de Confirmação
```

## 5. Arquitetura MVC Adaptada / Classes Base

```mermaid
classDiagram
    class TCCAssistantApp {
        +current_project_id: int
        +init_dashboard()
        +init_workspace(project_id)
        +run_citation_validation()
        +send_reports_by_email()
    }

    class PDFViewer {
        +pdf_document: fitz.Document
        +load_pdf(file_path)
        +render_page()
        +mouseReleaseEvent(event)
    }

    class database {
        <<module>>
        +create_project()
        +get_project()
        +add_annotation()
        +delete_annotation()
    }
    
    class validador_citacoes {
        <<module>>
        +extract_text_from_pdf()
        +find_references_section()
        +match_citations()
    }

    TCCAssistantApp *-- PDFViewer : Embutido na QSplitter
    TCCAssistantApp ..> database : Envia/Pede Dados
    TCCAssistantApp ..> validador_citacoes : Executa Rotina Pesada
```
