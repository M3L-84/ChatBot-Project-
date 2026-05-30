# bot.py — Salvar Chat (Pink Chat)
# Suporte dual: Google Gemini e Anthropic Claude
# Para trocar de IA, basta alterar IA_PROVIDER no .env

import os
import logging
import pytz
from datetime import datetime
from dotenv import load_dotenv

from modules.calculadora import realizar_orcamento, exibir_resumo

load_dotenv()

# ──────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────

logging.basicConfig(
    filename="pinkchat.log",
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# Configuração
# ──────────────────────────────────────────────

IA_PROVIDER = os.getenv("IA_PROVIDER", "gemini").lower()  # "gemini" ou "anthropic"

SYSTEM_PROMPT = (
    "Você é o assistente virtual da Salvar-se (Pink Chat). "
    "Sua missão é ser acolhedor e informativo sobre Cannabis Medicinal. "
    "Se não souber a resposta ou for algo complexo, oriente a falar com o suporte no menu 5. "
    "Mantenha respostas curtas, claras e amigáveis."
)

CONTEUDO = {
    "1": {
        "titulo": "Cadastro",
        "opcoes": {
            "1.1": "Não fiz cadastro",
            "1.2": "Já sou cadastrado",
            "1.3": "Admissão",
        },
    },
    "3": "A mensalidade vence todo dia 10 de cada mês. A contribuição mensal é de R$ 30,00.",
    "4": "O frete é calculado no momento da compra quando você escolhe a empresa transportadora.",
    "5": "Para cancelamento, envie um e-mail para contato@salvar-se.org.br com o assunto 'Cancelamento' e informe o motivo.",
}


# ──────────────────────────────────────────────
# Saudação dinâmica
# ──────────────────────────────────────────────

def obter_saudacao() -> str:
    try:
        hora = datetime.now(pytz.timezone("America/Sao_Paulo")).hour
    except Exception:
        hora = datetime.now().hour

    if 5 <= hora < 12:
        return "Tenha um excelente dia! ☀️"
    if 12 <= hora < 18:
        return "Tenha uma ótima tarde! 🌤️"
    return "Tenha uma excelente noite! 🌙"


# ──────────────────────────────────────────────
# Camada de IA
# ──────────────────────────────────────────────

def chamar_gemini(pergunta: str) -> str:
    chave = os.getenv("GOOGLE_API_KEY")
    if not chave:
        return "⚠️ GOOGLE_API_KEY não encontrada no .env"
    try:
        from google import genai
        client = genai.Client(api_key=chave)
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=f"{SYSTEM_PROMPT}\n\nPergunta do Cliente: {pergunta}",
        )
        return response.text
    except Exception as e:
        logger.error("Gemini: %s", e)
        return "No momento só consigo responder pelas opções do menu (1 a 5)."


def chamar_claude(pergunta: str) -> str:
    chave = os.getenv("ANTHROPIC_API_KEY")
    if not chave:
        return "⚠️ ANTHROPIC_API_KEY não encontrada no .env"
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=chave)
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": pergunta}],
        )
        return response.content[0].text
    except Exception as e:
        logger.error("Claude: %s", e)
        return "No momento só consigo responder pelas opções do menu (1 a 5)."


def chamar_ia(pergunta: str) -> str:
    """Roteador — escolhe Gemini ou Claude conforme IA_PROVIDER no .env."""
    if IA_PROVIDER == "anthropic":
        print("🤖 [IA: Claude - Anthropic]")
        return chamar_claude(pergunta)
    print("🤖 [IA: Gemini - Google]")
    return chamar_gemini(pergunta)


# ──────────────────────────────────────────────
# Handlers de menu
# ──────────────────────────────────────────────

def handle_cadastro() -> None:
    item = CONTEUDO["1"]
    print(f"\n----- {item['titulo']} -----")
    for sub, desc in item["opcoes"].items():
        print(f"  {sub}: {desc}")
    input("\nPressione ENTER para voltar...")


def handle_produtos() -> None:
    carrinho = realizar_orcamento()
    exibir_resumo(carrinho)
    input("\nPressione ENTER para voltar...")


def handle_informacao(chave: str) -> None:
    print(f"\nINFORMAÇÃO: {CONTEUDO[chave]}")
    input("\nPressione ENTER para voltar...")


def handle_ia(texto: str) -> None:
    resposta = chamar_ia(texto)
    print(f"\n[IA Pink Chat]: {resposta}")
    input("\nPressione ENTER para voltar...")


# ──────────────────────────────────────────────
# Menu e loop principal
# ──────────────────────────────────────────────

OPCOES_INFO = {"3", "4", "5"}

HANDLERS = {
    "1": handle_cadastro,
    "2": handle_produtos,
    **{k: (lambda k=k: handle_informacao(k)) for k in OPCOES_INFO},
}


def exibir_menu() -> None:
    ia_label = "Claude" if IA_PROVIDER == "anthropic" else "Gemini"
    print("\n" + "=" * 30)
    print(" PINK CHAT - SALVAR")
    print(f" IA ativa: {ia_label}")
    print("=" * 30)
    print("1. Cadastro\n2. Produtos\n3. Mensalidade\n4. Frete\n5. Cancelamento\n0. Sair")
    print("=" * 30)


def main() -> None:
    while True:
        exibir_menu()
        escolha = input("Digite o número da opção ou sua dúvida: ").strip()

        if escolha == "0":
            print(f"\n{obter_saudacao()}")
            break

        handler = HANDLERS.get(escolha)
        if handler:
            handler()
        else:
            handle_ia(escolha)


if __name__ == "__main__":
    main()