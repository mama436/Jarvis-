import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

HISTORY_FILE = Path("history.json")

DEFAULT_MODEL = os.getenv("DEEPSEEK_MODEL")

MAX_TOKENS = int(
    os.getenv("DEEPSEEK_MAX_TOKENS")
)

AVAILABLE_MODELS = {
    "flash": "deepseek-flash",
    "pro": "deepseek-v4-pro",
}


def load_history():
    if not HISTORY_FILE.exists():
        return []

    try:
        with HISTORY_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return data if isinstance(data, list) else []

    except (json.JSONDecodeError, OSError):
        return []


def save_history(history):
    with HISTORY_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            history,
            file,
            ensure_ascii=False,
            indent=2
        )


def show_history(history):
    if not history:
        print("\n Histórico vazio.\n")
        return

    print("\n===== HISTÓRICO =====")

    user_number = 0

    for message in history:
        role = message.get("role")
        content = message.get("content", "").replace("\n", " ")

        if role == "user":
            user_number += 1
            print(f"{user_number}. Você: {content}")

        elif role == "assistant":
            print(f"   JARVIS: {content}")

    print("=====================\n")


def forget_message(history, number):
    user_positions = [
        index
        for index, message in enumerate(history)
        if message.get("role") == "user"
    ]

    if number < 1 or number > len(user_positions):
        print(" Número de mensagem inválido.")
        return history

    position = user_positions[number - 1]

    del history[position]

    if (
        position < len(history)
        and history[position].get("role") == "assistant"
    ):
        del history[position]

    save_history(history)

    print(f" Mensagem {number} esquecida.")

    return history


def print_help():
    print("""
===== COMANDOS =====

/ajuda
Mostra esta ajuda.

/historico
Mostra o histórico da conversa.

/esquecer <n>
Esquece uma mensagem específica.

/limpar
Apaga todo o histórico.

/modelo
Mostra o modelo atual.

/modelo <nome>
Troca o modelo.

/modelos
Mostra os modelos disponíveis.

/sair
Encerra o JARVIS.

====================
""")


def print_models(current_model):
    print("\n===== MODELOS =====")

    for name, model_id in AVAILABLE_MODELS.items():
        marker = " ← atual" if model_id == current_model else ""
        print(f"{name}: {model_id}{marker}")

    print("===================\n")


def clean_answer(answer):
    if not answer:
        return ""

    # Remove Markdown de negrito.
    answer = answer.replace("**", "")

    return answer.strip()


def main():
    api_key = os.getenv("DEEPSEEK_API_KEY")

    if not api_key or api_key == "SUA_CHAVE_AQUI":
        print(" API Key invalida.")
        print("Abra o arquivo .env e coloque sua chave onde está escrito 'SUA_CHAVE_AQUI'")
        return

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
        timeout=60.0,
        max_retries=1
    )

    history = load_history()

    model = DEFAULT_MODEL

    if model not in AVAILABLE_MODELS.values():
        model = AVAILABLE_MODELS["flash"]

    print(" JARVIS iniciado!")
    print(f" Modelo: {model}")
    print(" API: DeepSeek")
    print(" Modo rápido")
    print()
    print("Digite /ajuda para ver os comandos.")
    print("Digite /sair para sair.")
    print()
#==
    while True:
        try:
            user_input = input("Você: ").strip()

        except (KeyboardInterrupt, EOFError):
            print("\n JARVIS encerrado.")
            break

        if not user_input:
            continue

        command = user_input.lower()

        # ==============================
        # SAIR
        # ==============================

        if command == "/sair":
            print(" JARVIS encerrado.")
            break

        # ==============================
        # AJUDA
        # ==============================

        if command == "/ajuda":
            print_help()
            continue

        # ==============================
        # HISTÓRICO
        # ==============================

        if command == "/historico":
            show_history(history)
            continue

        # ==============================
        # LIMPAR
        # ==============================

        if command == "/limpar":
            history.clear()
            save_history(history)
            print(" Histórico apagado.")
            continue

        # ==============================
        # MODELOS
        # ==============================

        if command == "/modelos":
            print_models(model)
            continue

        # ==============================
        # MODELO ATUAL
        # ==============================

        if command == "/modelo":
            print(f" Modelo atual: {model}")
            continue

        # ==============================
        # TROCAR MODELO
        # ==============================

        if command.startswith("/modelo "):
            chosen = user_input.split(maxsplit=1)[1].strip().lower()

            if chosen in AVAILABLE_MODELS:
                model = AVAILABLE_MODELS[chosen]
                print(f" Modelo alterado para: {model}")

            elif chosen in AVAILABLE_MODELS.values():
                model = chosen
                print(f" Modelo alterado para: {model}")

            else:
                print(" Modelo inválido. Use /modelos.")

            continue

        # ==============================
        # ESQUECER
        # ==============================

        if command.startswith("/esquecer"):
            parts = user_input.split()

            if len(parts) != 2 or not parts[1].isdigit():
                print("Use: /esquecer <n>")
                continue

            history = forget_message(
                history,
                int(parts[1])
            )

            continue

        # ==============================
        # MENSAGEM DO USUÁRIO
        # ==============================

        history.append({
            "role": "user",
            "content": user_input
        })

        print("JARVIS: ", end="", flush=True)

        try:
            stream = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Você é o JARVIS, um assistente virtual. "
                            "Responda sempre em português do Brasil. "
                            "Use linguagem natural, clara e objetiva. "
                            "Não use Markdown de negrito. "
                            "Nunca use dois asteriscos seguidos (**). "
                            "Prefira texto simples e natural."
                        )
                    },
                    *history
                ],
                stream=True,
                max_tokens=MAX_TOKENS,
                extra_body={
                    "thinking": {
                        "type": "disabled"
                    }
                }
            )

            answer_parts = []

            for chunk in stream:
                if not chunk.choices:
                    continue

                content = chunk.choices[0].delta.content

                if content:
                    answer_parts.append(content)
                    print(content, end="", flush=True)

            answer = clean_answer(
                "".join(answer_parts)
            )

            print()
            print()

        except Exception as error:
            history.pop()

            print()
            print(" Erro ao consultar a API:")
            print(error)
            print()

            continue

        history.append({
            "role": "assistant",
            "content": answer
        })

        save_history(history)


if __name__ == "__main__":
    main()