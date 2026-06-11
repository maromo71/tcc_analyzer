# Assistente de Revisão de TCC (TCC Analyzer)

Este é um software desenvolvido em Python com interface gráfica PyQt6 para auxiliar professores, orientadores e bancas examinadoras na revisão e avaliação de Trabalhos de Conclusão de Curso (TCC).

O programa permite carregar um PDF do TCC, extrair trechos facilmente com o mouse, organizá-los por categorias (Apontamentos, Dúvida, Sugestão), redigir um parecer geral, validar citações ABNT de forma automatizada (cruzando citações no texto com as referências bibliográficas) e, finalmente, exportar o relatório para PDF ou DOCX e enviá-lo por e-mail para o orientador.

## Funcionalidades Principais

- **Visualizador de PDF Integrado**: Navegue pelas páginas do TCC com zoom e capture trechos de texto automaticamente apenas selecionando-os com o mouse.
- **Gerenciador de Anotações**: Organize os apontamentos por categoria e por página para facilitar o feedback ao aluno.
- **Validação Automática de Citações**: Um motor inteligente que lê o texto, extrai citações no formato (Autor, Ano) e cruza com a lista de referências, avisando o que está sobrando ou faltando.
- **Exportação de Relatórios**: Exporte todas as anotações e o parecer geral diretamente para arquivos `.pdf` e `.docx`.
- **Integração com E-mail**: Envie os relatórios automaticamente ao orientador através de credenciais SMTP.

---

## 🛠 Pré-requisitos e Instalação

Você precisará do **Python 3.9+** instalado na sua máquina.

1. **Clone ou baixe o repositório** para a sua máquina.
2. **Abra um terminal** (Prompt de Comando, PowerShell ou Terminal do Linux/Mac) na pasta raiz do projeto (`c:\tcc_analizer` por exemplo).
3. **Crie um ambiente virtual (Opcional, mas recomendado)**:
   ```bash
   python -m venv venv
   # No Windows:
   venv\Scripts\activate
   # No Linux/Mac:
   source venv/bin/activate
   ```
4. **Instale as dependências** do projeto através do `pip`:
   ```bash
   pip install PyQt6 PyMuPDF python-docx pandas openpyxl python-dotenv
   ```
5. **Configuração de Variáveis de Ambiente (.env)**:
   Crie ou edite o arquivo `.env` na raiz do projeto com as suas credenciais SMTP caso deseje usar a funcionalidade de envio de e-mails:
   ```env
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=seu-email@gmail.com
   SMTP_PASSWORD=sua-senha-de-app
   ```
   *(Dica: Se você usa o Gmail, será necessário criar uma "Senha de App" nas configurações de segurança da sua conta Google, pois a senha normal não funcionará).*

---

## 🚀 Como Executar

Com as dependências instaladas, basta executar o arquivo principal:

```bash
python main.py
```

Uma janela com a interface gráfica escura e moderna (Glassmorphism) abrirá.

---

## 📚 Documentação do Projeto

O projeto conta com uma documentação extensa técnica e visual na pasta `docs/`. Recomendamos a leitura dos arquivos abaixo para entender a fundo a engenharia do software e o tutorial de uso:

- [docs/arquitetura.md](./docs/arquitetura.md): Estrutura do projeto, tecnologias e módulos.
- [docs/banco_de_dados.md](./docs/banco_de_dados.md): Modelagem de dados e esquemas do SQLite.
- [docs/diagramas.md](./docs/diagramas.md): Fluxogramas e diagramas de sequência.
- [docs/tutorial_uso_ui.md](./docs/tutorial_uso_ui.md): Tutorial completo de ponta a ponta focado no usuário final.

---
**Desenvolvido para otimizar o tempo e a precisão em correções acadêmicas.**
