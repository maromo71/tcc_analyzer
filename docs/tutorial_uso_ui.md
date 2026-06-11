# Tutorial de Uso UI/UX (Avaliadores e Professores)

Bem-vindo ao **Assistente de Revisão de TCC**! Preparamos este tutorial com o olhar afiado de um designer de UX (User Experience) para guiar você desde o seu primeiro projeto até a geração final do relatório em e-mail.

## 1. Visão Geral: O Painel de Projetos (Dashboard)

Logo ao abrir o aplicativo (`python main.py`), você verá uma interface imersiva com estética "Glassmorphism" — janelas semi-transparentes sob um modo noturno (Dark Mode) relaxante para leitura prolongada.

- O painel exibe uma **tabela listando todos os trabalhos** já avaliados ou em avaliação.
- **Botões Dinâmicos**: A parte superior dispõe botões para "Nova Revisão", "Abrir", "Editar" e "Excluir". Apenas funcionam se um projeto da tabela estiver clicado e em destaque (azul).

### Iniciando a Jornada: Nova Revisão
1. Clique no botão **`Nova Revisão`** (em tom verde vibrante, indicando "Criação").
2. Um modal flutuante será aberto.
3. Preencha o `Nome do Aluno`, o `Título do Trabalho`.
4. **IMPORTANTE**: Insira o **`E-mail do Orientador`**, pois será essencial para automatizar o envio mais para frente.
5. Selecione o arquivo em formato **PDF**.
6. Confirme em **Criar Projeto**. O sistema automaticamente mudará de tela para o seu **"Workspace"**.

---

## 2. Workspace de Correção: Divisão Lógica

O espaço de trabalho é dividido através de um controle ajustável (aquele traço vertical no meio que você pode arrastar para ajustar o tamanho dos painéis a sua preferência):

- **Esquerda (Aproximadamente 65%)**: Área limpa de exibição focada na navegação do PDF.
- **Direita (Aproximadamente 35%)**: Seus apontamentos, formulários e fluxos de trabalho gerencial.

### 2.1 Navegando e Analisando o TCC (Painel Esquerdo)
- No topo, use os botões **`🔍+`** e **`🔍-`** para deixar a leitura confortável aos olhos. 
- Use **`⬅️`** e **`➡️`** para trocar de páginas, role com o mouse, ou digite o número da página no campo e clique em **`Ir`** (ou tecle Enter) para navegar rapidamente.

### 2.2 Capturando Textos Magicamente (Killer Feature)
Se durante a leitura você achar um parágrafo duvidoso, um erro ou frase incompleta:
1. Com o mouse, clique, segure e arraste um "Retângulo Transparente" (`Rubber Band`) ao redor do trecho direto na página do PDF.
2. Ao soltar o clique do mouse... a mágica acontece!
3. Olhe para a lateral Direita da tela: **O campo de "Página" e "Trecho" foram preenchidos instantaneamente**.

### 2.3 Fazendo suas Observações (Painel Direito)
Com o trecho preenchido, você pode:
1. Ir na caixa central e digitar a sua crítica ou **Observação**.
2. No topo, selecione a aba adequada para definir o tipo do problema: 
   - **🔴 Apontamentos**
   - **🟡 Dúvida**
   - **🔵 Sugestão**
3. Clique em **`Salvar Anotação`** (Laranja). A anotação irá preencher a grade inferior e ficará imutável lá até você desejar alterar.

*(Você pode seguir lendo e repetindo esse loop - Captura -> Observa -> Salva. É rápido e produtivo).*

---

## 3. O Parecer Final da Banca 

Quando terminar de ler todo o TCC, vá para a última caixa de texto (Painel Direito, parte inferior) chamada **"Parecer Geral de Membro da Banca Avaliadora"**.
- Aqui é o espaço livre, para a sua dissertação final e aprovação/reprovação.
- Você não precisa de um botão "Salvar" para o parecer geral. O aplicativo conta com *Autosave* silencioso a cada 2 segundos!

---

## 4. O Validador Inteligente de Citações ABNT

Antes de fechar tudo, o sistema pode verificar se o aluno esqueceu de referenciar os autores na bibliografia.
1. No final do painel, clique em **`Validar Citações`** (Verde).
2. O sistema "congelará" o mouse por 1 ou 2 segundos lendo as referências e cruzando-as com o conteúdo.
3. Uma tela imponente exibirá uma tabela em tela cheia mapeando os acertos (✅) e as falhas (❌). 
4. Você pode clicar em "Editar" para ajustar as verificações ou "Exportar para Excel" e enviar essa análise dura ao aluno para ele ajustar.

---

## 5. Fechamento de Ouro: Exportação e E-mail

Pronto, seu trabalho manual chegou ao fim. É hora de compilar tudo.

- Botão **`Exportar Relatório`**: Pede seu nome (para assinar) e se prefere um documento em `.PDF` moderno e bem formatado, ou `.DOCX` (para o aluno conseguir colar e editar nos arquivos dele). O sistema gerará o arquivo e te mostrará na tela.
  
- Botão **`Enviar por E-mail`**: Executa a mesma rotina acima (pedindo seu nome e formato), mas em vez de pedir onde "Salvar" em seu disco rígido, ele anexa o Relatório Final + a Planilha do Excel das Citações validadas, formata um e-mail com boas práticas corporativas e submete usando a caixa postal (SMTP) configurada.

Caso o processo não esteja finalizado, basta utilizar o botão **`Salvar Rascunho e Sair`**. Seu andamento estará seguro na lista de projetos (Dashboard) esperando seu retorno na próxima inicialização do software.
