# whatsapp_server.py
# Servidor Flask + Twilio Sandbox para WhatsApp
# Executar: python3.11 whatsapp_server.py

import os
import logging
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

load_dotenv()

from modules.calculadora import buscar_produtos, CUPONS

app = Flask(__name__)

logging.basicConfig(
    filename="salvarchat.log",
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Configuração de IA
# ──────────────────────────────────────────────

IA_PROVIDER  = os.getenv("IA_PROVIDER", "gemini").lower()

SYSTEM_PROMPT = (
    "Você é o assistente virtual da Salvar-se (Salvar). "
    "Sua missão é ser acolhedor e informativo sobre Cannabis Medicinal. "
    "Se não souber a resposta ou for algo complexo, oriente a falar com o suporte: "
    "digite 9 para falar com um atendente. "
    "Mantenha respostas curtas, claras e amigáveis."
)

def chamar_ia(pergunta: str) -> str:
    if IA_PROVIDER == "anthropic":
        return _chamar_claude(pergunta)
    return _chamar_gemini(pergunta)

def _chamar_gemini(pergunta: str) -> str:
    chave = os.getenv("GOOGLE_API_KEY")
    if not chave:
        return "⚠️ GOOGLE_API_KEY não encontrada."
    try:
        from google import genai
        client = genai.Client(api_key=chave)
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=f"{SYSTEM_PROMPT}\n\nPergunta: {pergunta}"
        )
        return response.text
    except Exception as e:
        logger.error("Gemini: %s", e)
        return "No momento não consigo responder. Digite *menu* para ver as opções."

def _chamar_claude(pergunta: str) -> str:
    chave = os.getenv("ANTHROPIC_API_KEY")
    if not chave:
        return "⚠️ ANTHROPIC_API_KEY não encontrada."
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
        return "No momento não consigo responder. Digite *menu* para ver as opções."


# ──────────────────────────────────────────────
# Sessões dos usuários
# ──────────────────────────────────────────────

sessoes: dict[str, dict] = {}

def obter_sessao(numero: str) -> dict:
    if numero not in sessoes:
        sessoes[numero] = {"etapa": "menu", "carrinho": []}
    return sessoes[numero]


# ──────────────────────────────────────────────
# Conteúdo estático
# ──────────────────────────────────────────────

MENU_PRINCIPAL = (
    "🌿 *ASSISTENTE VIRTUAL — SALVAR-SE*\n\n"
    "Como posso ajudar?\n\n"
    "*1.* Cadastro\n"
    "*2.* Produtos e orçamento\n"
    "*3.* Mensalidade\n"
    "*4.* Frete e rastreio\n"
    "*5.* Cancelamento\n"
    "*9.* Falar com atendente\n"
    "*0.* Encerrar\n\n"
    "Digite o número da opção ou sua dúvida."
)

CONTEUDO = {
    "1": (
        "📋 *CADASTRO*\n\n"
        "*1.* Passo a passo\n"
        "*2.* Já sou cadastrado\n"
        "*3.* Admissão\n"
        "*0.* Voltar ao menu"
    ),
    "1.1": (
        "📝 *PASSO A PASSO*\n\n"
        "1. Acesse: https://acesso.salvar-se.org.br/AreaAssociados\n\n"
        "2. Clique em *Cadastre-se* abaixo de 'Recuperar minha senha' e preencha o formulário.\n\n"
        "3. Documentação necessária:\n"
        "   • Receita médica (óleo e/ou flor)\n"
        "   • Laudo médico\n"
        "   • Comprovante de residência\n"
        "   • RG\n"
        "   • Termo de Ajuizamento (disponível no formulário)\n\n"
        "4. Nossa equipe analisará seus documentos e, após aprovação, você se tornará associado.\n\n"
        "5. Acesse a Área do Associado e consulte os produtos disponíveis.\n\n"
        "6. Mensalidade: R$ 30,00/mês. Produtos a partir de R$ 210,00.\n"
        "   Pagamento via PIX, cartão ou boleto.\n\n"
        "7. Com a mensalidade em dia, adquira seus produtos na Área do Associado.\n\n"
        "_Ficou com dúvidas? Digite *9* para falar com um atendente._\n\n"
        "Digite *0* para voltar ao menu."
    ),
    "1.2": (
        "Por gentileza, informe o nome, CPF ou número de associado para que "
        "possamos localizar o seu cadastro e iniciar o processo de admissão.\n\n"
        "Digite *0* para voltar ao menu."
    ),
    "3": (
        "💳 *MENSALIDADE*\n\n"
        "A mensalidade vence todo dia 10 de cada mês e o valor é de R$ 30,00. "
        "É necessário estar com a mensalidade em dia para realizar pedidos. "
        "Optamos pelo plano mensal com o objetivo de facilitar o acesso a todos os públicos.\n\n"
        "Digite *menu* para voltar."
    ),
    "4": (
        "🚚 *FRETE E RASTREIO*\n\n"
        "O frete é calculado no momento da compra, ao escolher a transportadora. "
        "O prazo para expedição é de até 5 dias úteis após a confirmação do pedido.\n\n"
        "*Status do pedido:*\n"
        "Pago → Atendido → Em preparação → Expedido\n\n"
        "Após 'Expedido', o código de rastreio é enviado para o seu e-mail. "
        "Acompanhe em: Área do Associado › Pedidos.\n\n"
        "*Transportadoras:*\n"
        "• JADLOG (código iniciado em 18): https://www.jadlog.com.br/jadlog/captcha\n"
        "• AZUL LOGÍSTICA (demais): https://www.azullogistica.com.br/Rastreio\n\n"
        "Digite *menu* para voltar."
    ),
    "5": (
        "❌ *CANCELAMENTO*\n\n"
        "Envie um e-mail para contato@salvar-se.org.br com o assunto 'Cancelamento' e informe o motivo. "
        "Após o envio, informe ao suporte, que executará o procedimento. "
        "Não será cobrada multa ou taxa, independentemente de pendências. "
        "O cancelamento só será executado caso não haja envios em trânsito.\n\n"
        "Digite *menu* para voltar."
    ),
    "9": (
        "👤 *FALAR COM ATENDENTE*\n\n"
        "Nosso horário de atendimento é de segunda a sexta, das 9h às 19h.\n\n"
        "Em breve você será direcionado a um atendente.\n\n"
        "Digite *menu* para voltar ao menu principal."
    ),
}


# ──────────────────────────────────────────────
# Lógica de orçamento via WhatsApp
# ──────────────────────────────────────────────

def montar_catalogo() -> str:
    produtos = buscar_produtos()
    if not produtos:
        return "⚠️ Produtos indisponíveis no momento."
    linhas = ["🛍️ *PRODUTOS SALVAR-SE*\n"]
    for i, (nome, preco, _) in enumerate(produtos, 1):
        linhas.append(f"*{i}.* {nome} — R$ {preco:.2f}")
    linhas.append("\nDigite o número do produto para adicionar ao carrinho.")
    linhas.append("Digite *r* para ver o resumo, *0* para finalizar ou *menu* para voltar.")
    return "\n".join(linhas)

def montar_resumo(sessao: dict) -> str:
    carrinho = sessao["carrinho"]
    if not carrinho:
        return "🛒 Carrinho vazio."

    linhas = ["🧾 *RESUMO DO PEDIDO*\n"]
    total_bruto = 0.0
    total_desconto = 0.0

    for item in carrinho:
        subtotal  = item["qtd"] * item["preco"]
        desconto  = subtotal * item["desconto"]
        total_bruto    += subtotal
        total_desconto += desconto
        linhas.append(f"• {item['qtd']}x {item['nome']}")
        linhas.append(f"  Subtotal: R$ {subtotal:.2f} | Desconto: R$ {desconto:.2f}")

    cupom_valor = total_bruto * CUPONS.get("salvar10", 0.0)
    total_final = total_bruto - total_desconto - cupom_valor

    linhas.append(f"\nValor bruto:        R$ {total_bruto:.2f}")
    linhas.append(f"Desconto produtos:  R$ {total_desconto:.2f}")
    linhas.append(f"Cupom salvar10:     R$ {cupom_valor:.2f}")
    linhas.append(f"*TOTAL:             R$ {total_final:.2f}*")
    linhas.append("\nDigite *menu* para voltar ou *0* para encerrar.")
    return "\n".join(linhas)


# ──────────────────────────────────────────────
# Roteador de mensagens
# ──────────────────────────────────────────────

def processar_mensagem(numero: str, texto: str) -> str:
    sessao = obter_sessao(numero)
    etapa  = sessao["etapa"]
    msg    = texto.strip().lower()

    # Comandos globais
    if msg in ("menu", "oi", "olá", "ola", "inicio", "início"):
        sessao["etapa"] = "menu"
        sessao["carrinho"] = []
        return MENU_PRINCIPAL

    if msg == "0":
        sessao["etapa"] = "menu"
        return "Até logo! 🌿 Digite *menu* quando precisar."

    # ── MENU PRINCIPAL ──
    if etapa == "menu":
        if msg == "1":
            sessao["etapa"] = "cadastro"
            return CONTEUDO["1"]
        if msg == "2":
            sessao["etapa"] = "produtos"
            return montar_catalogo()
        if msg in ("3", "4", "5", "9"):
            return CONTEUDO[msg]
        # Fallback IA
        return chamar_ia(texto)

    # ── CADASTRO ──
    if etapa == "cadastro":
        if msg in ("1", "[1]"):
            return CONTEUDO["1.1"]
        if msg in ("2", "[2]"):
            sessao["etapa"] = "aguardando_cadastro"
            return CONTEUDO["1.2"]
        if msg in ("3", "[3]"):
            return "Opção Admissão em breve. Digite *0* para voltar ao menu."
        return MENU_PRINCIPAL

    # ── AGUARDANDO DADOS DE CADASTRO ──
    if etapa == "aguardando_cadastro":
        sessao["etapa"] = "menu"
        return (
            f"Obrigado! Recebemos seus dados: *{texto}*\n\n"
            "Nossa equipe entrará em contato em breve. "
            "Digite *menu* para voltar ao menu principal."
        )

    # ── PRODUTOS ──
    if etapa == "produtos":
        produtos = buscar_produtos()

        if msg == "r":
            return montar_resumo(sessao)

        try:
            idx = int(msg) - 1
            if 0 <= idx < len(produtos):
                nome, preco, desconto = produtos[idx]
                sessao["etapa"] = f"qtd_{idx}"
                return f"Quantas unidades de *{nome}*? (máximo 6)"
        except ValueError:
            pass

        return chamar_ia(texto)

    # ── QUANTIDADE ──
    if etapa.startswith("qtd_"):
        idx = int(etapa.split("_")[1])
        produtos = buscar_produtos()
        try:
            qtd = int(msg)
            if 1 <= qtd <= 6:
                nome, preco, desconto = produtos[idx]
                sessao["carrinho"].append({
                    "nome": nome, "qtd": qtd,
                    "preco": preco, "desconto": desconto
                })
                sessao["etapa"] = "produtos"
                return (
                    f"✅ {qtd}x *{nome}* adicionado!\n\n"
                    + montar_catalogo()
                )
            return "⚠️ Quantidade entre 1 e 6. Tente novamente."
        except ValueError:
            return "⚠️ Digite apenas números."

    # Fallback geral
    sessao["etapa"] = "menu"
    return MENU_PRINCIPAL


# ──────────────────────────────────────────────
# Webhook Twilio
# ──────────────────────────────────────────────

@app.route("/webhook", methods=["POST"])
def webhook():
    numero  = request.form.get("From", "")
    texto   = request.form.get("Body", "").strip()
    resposta = processar_mensagem(numero, texto)

    twiml = MessagingResponse()
    twiml.message(resposta)
    response = app.make_response(str(twiml))
    response.headers["ngrok-skip-browser-warning"] = "true"
    return response


if __name__ == "__main__":
    print("🌿 *ASSISTENTE VIRTUAL — rodando na porta 5000")
    print("   Webhook: http://localhost:5000/webhook")
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)