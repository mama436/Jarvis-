import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

HISTORY_FILE = Path("history.json")
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")

AVAILABLE_MODELS = {
    "luna": "gpt-5.6-luna",
    "terra": "gpt-5.6-terra",
    "sol": "gpt-5.6-sol",
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
        json.dump(history, file, ensure_ascii=False, indent=2)


def show_history(history):
    if not history:
        print("\n📭 Histórico vazio.\n")
        return

    print("\n===== HISTÓRICO =====")
    for index, message in enumerate(history, start=1):
        role = "Você" if message["role"] == "user" else "JARVIS"
        content = message["content"].replace("\n", " ")
        print(f"{index}. {role}: {content}")
    print("=====================\n")


def forget_message(history, number):
    user_positions = [
        index for index, message in enumerate(history)
        if message["role"] == "user"
    ]

    if number < 1 or number > len(user_positions):
        print("❌ Número de mensagem inválido.")
        return history

    position = user_positions[number - 1]
    del history[position]

    # Remove a resposta do JARVIS logo depois, se existir.
    if position < len(history) and history[position]["role"] == "assistant":
        del history[position]

    save_history(history)
    print(f"🗑️ Mensagem {number} esquecida.")
    return history


def print_help():
    print("""
===== COMANDOS =====
/ajuda              Mostra esta ajuda
/historico          Mostra o histórico
/esquecer <n>       Esquece a mensagem do usuário de número n
/limpar             Apaga todo o histórico
/modelo             Mostra o modelo atual
/modelo <nome>      Troca o modelo (luna, terra ou sol)
/modelos            Mostra os modelos disponíveis
/sair               Encerra o JARVIS
====================
""")


def main():
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key or api_key == "CHAVE_API_AQUI":
        print("❌ API Key não configurada.")
        print("Crie um arquivo .env e coloque:")
        print("OPENAI_API_KEY=CHAVE_API_AQUI")
        return

    client = OpenAI(api_key=api_key)
    history = load_history()

    model = DEFAULT_MODEL
    if model not in AVAILABLE_MODELS.values():
        model = AVAILABLE_MODELS["luna"]

    print("🤖 JARVIS iniciado!")
    print(f"🧠 Modelo: {model}")
    print("Digite /ajuda para ver os comandos.")
    print("Digite /sair para sair.\n")

    while True:
        try:
            user_input = input("Você: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n👋 JARVIS encerrado.")
            break

        if not user_input:
            continue

        command = user_input.lower()

        if command == "/sair":
            print("👋 JARVIS encerrado.")
            break

        if command == "/ajuda":
            print_help()
            continue

        if command == "/historico":
            show_history(history)
            continue

        if command == "/limpar":
            history.clear()
            save_history(history)
            print("🧹 Histórico apagado.")
            continue

        if command == "/modelos":
            print("\n===== MODELOS =====")
            for name, model_id in AVAILABLE_MODELS.items():
                marker = " ← atual" if model_id == model else ""
                print(f"{name}: {model_id}{marker}")
            print("===================\n")
            continue

        if command == "/modelo":
            print(f"🧠 Modelo atual: {model}")
            continue

        if command.startswith("/modelo "):
            chosen = user_input.split(maxsplit=1)[1].strip().lower()
            if chosen in AVAILABLE_MODELS:
                model = AVAILABLE_MODELS[chosen]
                print(f"🧠 Modelo alterado para: {model}")
            elif chosen in AVAILABLE_MODELS.values():
                model = chosen
                print(f"🧠 Modelo alterado para: {model}")
            else:
                print("❌ Modelo inválido. Use /modelos.")
            continue

        if command.startswith("/esquecer"):
            parts = user_input.split()
            if len(parts) != 2 or not parts[1].isdigit():
                print("Use: /esquecer <n>")
                continue
            history = forget_message(history, int(parts[1]))
            continue

        history.append({"role": "user", "content": user_input})

        try:
            response = client.responses.create(
                model=model,
                input=history,
            )
            answer = response.output_text.strip()
        except Exception as error:
            history.pop()
            print(f"\n❌ Erro ao consultar a API: {error}\n")
            continue

        print(f"JARVIS: {answer}\n")

        history.append({"role": "assistant", "content": answer})
        save_history(history)


if __name__ == "__main__":
    main()
