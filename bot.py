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
            "[1]": "Passo a passo",
            "[2]": "Já sou cadastrado",
            "[3]": "Admissão",
            "[0]": "Voltar ao menu principal",
        },
        "detalhes": {
            "[1]": (
                "Agradecemos pelo seu interesse em se associar à Salvar-se!\n\n"
                "Para adquirir os produtos da sua receita, siga os passos abaixo:\n\n"
                "1. Acesse o site: https://acesso.salvar-se.org.br/AreaAssociados\n\n"
                "2. Cadastro: abaixo de 'Recuperar minha senha', clique em 'Cadastre-se' "
                "e preencha o formulário com seus dados pessoais.\n\n"
                "3. Documentação necessária:\n"
                "   • Receita médica indicando o uso de óleo e/ou flor\n"
                "   • Laudo médico\n"
                "   • Comprovante de residência\n"
                "   • RG\n"
                "   • Termo de Ajuizamento (disponível para download no formulário)\n\n"
                "4. Revisão e aprovação: nossa equipe analisará seus documentos e, "
                "após aprovação, você se tornará um associado.\n\n"
                "5. Escolha dos produtos: acesse a Área do Associado e consulte "
                "os produtos disponíveis para compra.\n\n"
                "6. Mensalidade: R$ 30,00/mês. Produtos a partir de R$ 210,00. "
                "Pagamento via PIX, cartão ou boleto.\n\n"
                "7. Aquisição: com a mensalidade em dia, selecione e adquira seus "
                "produtos diretamente na Área do Associado.\n\n"
                "Ficou com dúvidas? Nossa equipe está disponível neste canal.\n\n"
                "Sobre o Termo de Ajuizamento:\n"
                "É a autorização do associado para ingresso em ações coletivas "
                "relacionadas ao cultivo da Associação."
            ),
            "[2]": (
                "Por gentileza, informe o nome, CPF ou número de associado para que "
                "possamos localizar o seu cadastro e iniciar o processo de admissão."
            ),
        },
    },
    "3": (
        "A mensalidade vence todo dia 10 de cada mês e o valor é de R$ 30,00. "
        "É necessário estar com a mensalidade em dia para realizar pedidos. "
        "Optamos pelo plano mensal com o objetivo de facilitar o acesso a todos os públicos."
    ),
    "4": (
        "O frete é calculado no momento da compra, ao escolher a transportadora. "
        "O prazo para expedição é de 5 dias úteis após a confirmação do pedido.\n\n"
        "Acompanhamento do pedido — os status seguem esta ordem:\n"
        "  Pago → Atendido → Em preparação → Expedido\n\n"
        "Após a atualização para 'Expedido', o código de rastreio será enviado "
        "para o seu e-mail. Você também pode acompanhar em: Área do Associado > Histórico de Pedidos.\n\n"
        "Transportadoras parceiras:\n"
        "  • JADLOG (códigos iniciados em 18): https://www.jadlog.com.br/jadlog/captcha\n"
        "  • AZUL LOGÍSTICA (demais códigos): https://www.azullogistica.com.br/Rastreio"
    ),
    "5": (
        "\n• Para cancelamento, envie um e-mail para contato@salvar-se.org.br "
        "com o assunto 'Cancelamento' e informe o motivo.\n "
        "• Após o envio, informe ao suporte, que executarão o procedimento.\n "
        "• Não será cobrada multa ou taxa, independentemente de pendências.\n "
        "• O cancelamento só será executado caso não haja envios em trânsito. "
    ),
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
    while True:
        item = CONTEUDO["1"]
        print(f"\n----- {item['titulo']} -----")
        for chave, desc in item["opcoes"].items():
            print(f"  {chave}: {desc}")

        escolha = input("\nEscolha uma opção: ").strip()

        if escolha == "0":
            break
        elif escolha == "1" or escolha == "[1]":
            print("\n" + "=" * 60)
            print(item["detalhes"]["[1]"])
            print("=" * 60)
            input("\nPressione ENTER para voltar...")
        elif escolha == "2" or escolha == "[2]":
            print("\n" + "=" * 60)
            print(item["detalhes"]["[2]"])
            print("=" * 60)
            input("\nPressione ENTER para voltar...")
        elif escolha == "3" or escolha == "[3]":
            print("\n  Em breve — opção Admissão.")
            input("\nPressione ENTER para voltar...")
        else:
            resposta = chamar_ia(escolha)
            print(f"\n[IA Pink Chat]: {resposta}")
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