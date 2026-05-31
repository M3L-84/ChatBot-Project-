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

# Roteador de mensagens do Flask
# Configurações de IA


IA_PROVIDER  = os.getenv("IA_PROVIDER", "gemini").lower()

SYSTEM_PROMPT = (
    "VocÃª Ã© o assistente virtual da Salvar-se (Salvar). "
    "Sua missÃ£o Ã© ser acolhedor e informativo sobre Cannabis Medicinal. "
    "Se nÃ£o souber a resposta ou for algo complexo, oriente a falar com o suporte: "
    "digite 9 para falar com um atendente. "
    "Mantenha respostas curtas, claras e amigÃ¡veis."
)

def chamar_ia(pergunta: str) -> str:
    if os.getenv("IA_ATIVA", "false").lower() != "true":
        return (
            "Não entendi sua mensagem. 😊\n\n"
            "Use as opções do menu:\n"
            "*1.* Cadastro\n"
            "*2.* Produtos\n"
            "*3.* Mensalidade\n"
            "*4.* Frete\n"
            "*5.* Cancelamento\n"
            "*9.* Falar com atendente\n\n"
            "Ou digite *menu* para ver tudo."
        )
    if IA_PROVIDER == "anthropic":
        return _chamar_claude(pergunta)
    return _chamar_gemini(pergunta)

def _chamar_gemini(pergunta: str) -> str:
    chave = os.getenv("GOOGLE_API_KEY")
    if not chave:
        return "âš ï¸ GOOGLE_API_KEY nÃ£o encontrada."
    try:
        from google import genai
        client = genai.Client(api_key=chave)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"{SYSTEM_PROMPT}\n\nPergunta: {pergunta}"
        )
        return response.text
    except Exception as e:
        logger.error("Gemini: %s", e)
        print(f"[ERRO GEMINI] {e}", flush=True)
        return "No momento não consigo responder. Digite *menu* para ver as opções."
    
def _chamar_claude(pergunta: str) -> str:
    chave = os.getenv("ANTHROPIC_API_KEY")
    if not chave:
        return "âš ï¸ ANTHROPIC_API_KEY não encontrada."
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=chave)
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=512,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": pergunta}],
        )
        return response.content[0].text
    except Exception as e:
        logger.error("Claude: %s", e)
        print(f"[ERRO CLAUDE] {type(e).__name__}: {e}", flush=True)
        import traceback; traceback.print_exc()


# Sessões dos usuários

sessoes: dict[str, dict] = {}

def obter_sessao(numero: str) -> dict:
    if numero not in sessoes:
        sessoes[numero] = {"etapa": "menu", "carrinho": []}
    return sessoes[numero]


# Conteúdo estático do bot

MENU_PRINCIPAL = (
    "🌿 *ASSISTENTE VIRTUAL - SALVAR-SE*\n\n"
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
        "ðŸ“‹ *CADASTRO*\n\n"
        "*1.* Passo a passo\n"
        "*2.* JÃ¡ sou cadastrado\n"
        "*3.* AdmissÃ£o\n"
        "*0.* Voltar ao menu"
    ),
    "1.1": (
        "ðŸ“ *PASSO A PASSO*\n\n"
        "1. Acesse: https://acesso.salvar-se.org.br/AreaAssociados\n\n"
        "2. Clique em *Cadastre-se* abaixo de 'Recuperar minha senha' e preencha o formulÃ¡rio.\n\n"
        "3. DocumentaÃ§Ã£o necessÃ¡ria:\n"
        "   â€¢ Receita mÃ©dica (Ã³leo e/ou flor)\n"
        "   â€¢ Laudo mÃ©dico\n"
        "   â€¢ Comprovante de residÃªncia\n"
        "   â€¢ RG\n"
        "   â€¢ Termo de Ajuizamento (disponÃ­vel no formulÃ¡rio)\n\n"
        "4. Nossa equipe analisarÃ¡ seus documentos e, apÃ³s aprovaÃ§Ã£o, vocÃª se tornarÃ¡ associado.\n\n"
        "5. Acesse a Ãrea do Associado e consulte os produtos disponÃ­veis.\n\n"
        "6. Mensalidade: R$ 30,00/mÃªs. Produtos a partir de R$ 210,00.\n"
        "   Pagamento via PIX, cartÃ£o ou boleto.\n\n"
        "7. Com a mensalidade em dia, adquira seus produtos na Ãrea do Associado.\n\n"
        "_Ficou com dÃºvidas? Digite *9* para falar com um atendente._\n\n"
        "Digite *0* para voltar ao menu."
    ),
    "1.2": (
        "Por gentileza, informe o nome, CPF ou nÃºmero de associado para que "
        "possamos localizar o seu cadastro e iniciar o processo de admissÃ£o.\n\n"
        "Digite *0* para voltar ao menu."
    ),
    "3": (
        "ðŸ’³ *MENSALIDADE*\n\n"
        "A mensalidade vence todo dia 10 de cada mÃªs e o valor Ã© de R$ 30,00. "
        "Ã‰ necessÃ¡rio estar com a mensalidade em dia para realizar pedidos. "
        "Optamos pelo plano mensal com o objetivo de facilitar o acesso a todos os pÃºblicos.\n\n"
        "Digite *menu* para voltar."
    ),
    "4": (
        "ðŸšš *FRETE E RASTREIO*\n\n"
        "O frete Ã© calculado no momento da compra, ao escolher a transportadora. "
        "O prazo para expediÃ§Ã£o Ã© de atÃ© 5 dias Ãºteis apÃ³s a confirmaÃ§Ã£o do pedido.\n\n"
        "*Status do pedido:*\n"
        "Pago â†’ Atendido â†’ Em preparaÃ§Ã£o â†’ Expedido\n\n"
        "ApÃ³s 'Expedido', o cÃ³digo de rastreio Ã© enviado para o seu e-mail. "
        "Acompanhe em: Ãrea do Associado â€º Pedidos.\n\n"
        "*Transportadoras:*\n"
        "â€¢ JADLOG (cÃ³digo iniciado em 18): https://www.jadlog.com.br/jadlog/captcha\n"
        "â€¢ AZUL LOGÃSTICA (demais): https://www.azullogistica.com.br/Rastreio\n\n"
        "Digite *menu* para voltar."
    ),
    "5": (
        "âŒ *CANCELAMENTO*\n\n"
        "Envie um e-mail para contato@salvar-se.org.br com o assunto 'Cancelamento' e informe o motivo. "
        "ApÃ³s o envio, informe ao suporte, que executarÃ¡ o procedimento. "
        "NÃ£o serÃ¡ cobrada multa ou taxa, independentemente de pendÃªncias. "
        "O cancelamento sÃ³ serÃ¡ executado caso nÃ£o haja envios em trÃ¢nsito.\n\n"
        "Digite *menu* para voltar."
    ),
    "9": (
        "ðŸ‘¤ *FALAR COM ATENDENTE*\n\n"
        "Nosso horÃ¡rio de atendimento Ã© de segunda a sexta, das 9h Ã s 19h.\n\n"
        "Em breve vocÃª serÃ¡ direcionado a um atendente.\n\n"
        "Digite *menu* para voltar ao menu principal."
    ),
}

# Lógica de orçamento via Whatsapp

def montar_catalogo() -> str:
    produtos = buscar_produtos()
    if not produtos:
        return "âš ï¸ Produtos indisponÃ­veis no momento."
    linhas = ["ðŸ›ï¸ *PRODUTOS SALVAR-SE*\n"]
    for i, (nome, preco, _) in enumerate(produtos, 1):
        linhas.append(f"*{i}.* {nome} â€” R$ {preco:.2f}")
    linhas.append("\nDigite o nÃºmero do produto para adicionar ao carrinho.")
    linhas.append("Digite *r* para ver o resumo, *0* para finalizar ou *menu* para voltar.")
    return "\n".join(linhas)

def montar_resumo(sessao: dict) -> str:
    carrinho = sessao["carrinho"]
    if not carrinho:
        return "ðŸ›’ Carrinho vazio."

    linhas = ["ðŸ§¾ *RESUMO DO PEDIDO*\n"]
    total_bruto = 0.0
    total_desconto = 0.0

    for item in carrinho:
        subtotal  = item["qtd"] * item["preco"]
        desconto  = subtotal * item["desconto"]
        total_bruto    += subtotal
        total_desconto += desconto
        linhas.append(f"â€¢ {item['qtd']}x {item['nome']}")
        linhas.append(f"  Subtotal: R$ {subtotal:.2f} | Desconto: R$ {desconto:.2f}")

    cupom_valor = total_bruto * CUPONS.get("salvar10", 0.0)
    total_final = total_bruto - total_desconto - cupom_valor

    linhas.append(f"\nValor bruto:        R$ {total_bruto:.2f}")
    linhas.append(f"Desconto produtos:  R$ {total_desconto:.2f}")
    linhas.append(f"Cupom salvar10:     R$ {cupom_valor:.2f}")
    linhas.append(f"*TOTAL:             R$ {total_final:.2f}*")
    linhas.append("\nDigite *menu* para voltar ou *0* para encerrar.")
    return "\n".join(linhas)
# Roteador de mensagens

def processar_mensagem(numero: str, texto: str) -> str:
    sessao = obter_sessao(numero)
    etapa  = sessao["etapa"]
    msg    = texto.strip().lower()

    # Comandos globais
    if msg in ("menu", "oi", "olÃ¡", "ola", "inicio", "inÃ­cio"):
        sessao["etapa"] = "menu"
        sessao["carrinho"] = []
        return MENU_PRINCIPAL

    if msg == "0":
        sessao["etapa"] = "menu"
        return "AtÃ© logo! ðŸŒ¿ Digite *menu* quando precisar."

    # MENU PRINCIPAL 
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

    # CADASTRO 
    if etapa == "cadastro":
        if msg in ("1", "[1]"):
            return CONTEUDO["1.1"]
        if msg in ("2", "[2]"):
            sessao["etapa"] = "aguardando_cadastro"
            return CONTEUDO["1.2"]
        if msg in ("3", "[3]"):
            return "OpÃ§Ã£o AdmissÃ£o em breve. Digite *0* para voltar ao menu."
        return MENU_PRINCIPAL

    # AGUARDANDO DADOS DE CADASTRO 
    if etapa == "aguardando_cadastro":
        sessao["etapa"] = "menu"
        return (
            f"Obrigado! Recebemos seus dados: *{texto}*\n\n"
            "Nossa equipe entrarÃ¡ em contato em breve. "
            "Digite *menu* para voltar ao menu principal."
        )

    # PRODUTOS 
    if etapa == "produtos":
        produtos = buscar_produtos()

        if msg == "r":
            return montar_resumo(sessao)

        try:
            idx = int(msg) - 1
            if 0 <= idx < len(produtos):
                nome, preco, desconto = produtos[idx]
                sessao["etapa"] = f"qtd_{idx}"
                return f"Quantas unidades de *{nome}*? (mÃ¡ximo 6)"
        except ValueError:
            pass

        return chamar_ia(texto)

    #  QUANTIDADE 

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
                    f"âœ… {qtd}x *{nome}* adicionado!\n\n"
                    + montar_catalogo()
                )
            return "âš ï¸ Quantidade entre 1 e 6. Tente novamente."
        except ValueError:
            return "âš ï¸ Digite apenas nÃºmeros."

    # Fallback geral
    sessao["etapa"] = "menu"
    return MENU_PRINCIPAL

# Webhook Twilio

@app.route("/webhook", methods=["GET"])
def webhook_ping():
    return "OK", 200

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
    port = int(os.environ.get("PORT", 5000))
    print(f"ðŸŒ¿ ASSISTENTE VIRTUAL â€” rodando na porta {port}")
    app.run(host="0.0.0.0", port=port)
