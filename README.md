# JARVIS — OpenAI Terminal Chatbot

Chatbot de terminal em Python para usar no VS Code com a API da OpenAI.

## Recursos

- Conversa pelo terminal
- Histórico persistente em `history.json`
- `/esquecer <n>`
- `/historico`
- `/limpar`
- `/modelo`
- `/modelos`
- `/ajuda`
- `/sair`
- API Key carregada pelo arquivo `.env`
- `.env` e o histórico ficam fora do Git

## Instalação

1. Crie um ambiente virtual (opcional, mas recomendado):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Instale as dependências:

```powershell
pip install -r requirements.txt
```

3. Copie `.env.example` para `.env`.

4. No `.env`, coloque sua chave real:

```text
OPENAI_API_KEY=CHAVE_API_AQUI
OPENAI_MODEL=gpt-5.6-luna
```

Nunca publique sua chave no GitHub.

5. Execute:

```powershell
python jarvis.py
```

## Modelos

Os atalhos disponíveis são:

- `luna` → `gpt-5.6-luna`
- `terra` → `gpt-5.6-terra`
- `sol` → `gpt-5.6-sol`

Use `/modelo luna`, `/modelo terra` ou `/modelo sol`.

## Histórico

O histórico é salvo localmente em `history.json`. Esse arquivo está no `.gitignore`, então não será enviado para o GitHub.
