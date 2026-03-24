# ChatBot-Project-

"Bot de atendimento para o Pink Chat com Menu e IA".

# 🌸 Salvar Chat - Assistente Virtual Salvar-se

O **Salvar Chat** é um chatbot híbrido desenvolvido em Python, focado no atendimento de pacientes de Cannabis Medicinal. O projeto combina lógica de menu estruturada, persistência de dados em SQLite e inteligência artificial generativa.

## 🚀 Funcionalidades

- **Menu Interativo:** Navegação guiada por opções numeradas.
- **Calculadora de Orçamento:** Sistema dinâmico que consulta preços no Banco de Dados, permite múltiplas escolhas e limita a 6 unidades por produto.
- **Banco de Dados Relacional:** Uso de SQLite para gerenciamento de produtos e preços sem alteração no código-fonte.
- **Integração com IA (Gemini 1.5 Flash):** Suporte inteligente para dúvidas fora do menu fixo.
- **Saudação Dinâmica:** Despedida personalizada baseada no fuso horário (Brasília/BR).

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** [Python 3.12](https://www.python.org/)
- **Banco de Dados:** [SQLite](https://sqlite.org/)
- **IA Generativa:** [Google Gemini API](https://ai.google.dev/)
- **Bibliotecas:** `google-genai`, `python-dotenv`, `pytz`, `sqlite3`

---

## 📥 Instalação e Configuração

Siga os passos abaixo para rodar o projeto localmente ou no Codespaces:

### 1. Clonar o repositório

```bash
git clone [https://github.com/M3L-84/ChatBot-Project-.git](https://github.com/M3L-84/ChatBot-Project-.git)
cd ChatBot-Project-
```

### 2. Configurar Variáveis de Ambiente

Crie um arquivo chamado .env na raiz do projeto e adicione sua chave da API do Google.

> **Nota:** Este arquivo é ignorado pelo Git por segurança.

```text
GOOGLE_API_KEY=sua_chave_aqui_do_gemini
```

### 3. Instalar Dependências

Certifique-se de ter o Python instalado e execute:

```
Bash
pip install -r requirements.txt
```

### 4. Inicializar o Banco de Dados (Obrigatório)

Este passo cria o arquivo pinkchat.db e insere os produtos iniciais. Sem ele, a calculadora de orçamento não funcionará.

```
Bash
python3 setup_db.py
```

### 5. Executar o Bot

Agora você já pode iniciar o atendimento:

```
Bash
python3 bot.py
```
