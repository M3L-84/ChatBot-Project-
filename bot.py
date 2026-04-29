# bot.py — Salvar Chat (Pink Chat)
# Suporte dual: Google Gemini e Anthropic Claude
# Para trocar de IA, basta alterar IA_PROVIDER no arquivo .env

import os
import pytz
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURAÇÃO DO PROVIDER ---
IA_PROVIDER = os.getenv("IA_PROVIDER", "gemini").lower()  # "gemini" ou "anthropic"

from modules.calculadora import realizar_orcamento, exibir_resumo


# --- FUNÇÕES DE APOIO ---

def obter_saudacao_por_horario():
    try:
        fuso_br = pytz.timezone("America/Sao_Paulo")
        hora_atual = datetime.now(fuso_br).hour
    except:
        hora_atual = datetime.now().hour

    if 5 <= hora_atual < 12:
        return "Tenha um excelente dia! ☀️"
    elif 12 <= hora_atual < 18:
        return "Tenha uma ótima tarde! 🌤️"
    else:
        return "Tenha uma excelente noite! 🌙"


# --- FUNÇÕES DE IA ---

SYSTEM_PROMPT = (
    "Você é o assistente virtual da Salvar-se (Pink Chat). "
    "Sua missão é ser acolhedor e informativo sobre Cannabis Medicinal. "
    "Se não souber a resposta ou for algo complexo, oriente a falar com o suporte no menu 5. "
    "Mantenha respostas curtas, claras e amigáveis."
)

def chamar_gemini(pergunta):
    """Chama a API do Google Gemini."""
    chave = os.getenv("GOOGLE_API_KEY")
    if not chave:
        return "⚠️ GOOGLE_API_KEY não encontrada no .env"
    try:
        from google import genai
        client = genai.Client(api_key=chave)
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=f"{SYSTEM_PROMPT}\n\nPergunta do Cliente: {pergunta}"
        )
        return response.text
    except Exception as e:
        print(f"[DEBUG Gemini] {e}")
        return "No momento só consigo responder pelas opções do menu (1 a 5)."


def chamar_claude(pergunta):
    """Chama a API da Anthropic (Claude)."""
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
            messages=[{"role": "user", "content": pergunta}]
        )
        return response.content[0].text
    except Exception as e:
        print(f"[DEBUG Claude] {e}")
        return "No momento só consigo responder pelas opções do menu (1 a 5)."


def chamar_ia_pink_chat(pergunta):
    """Roteador de IA — escolhe Gemini ou Claude conforme IA_PROVIDER no .env."""
    if IA_PROVIDER == "anthropic":
        print("🤖 [IA: Claude - Anthropic]")
        return chamar_claude(pergunta)
    else:
        print("🤖 [IA: Gemini - Google]")
        return chamar_gemini(pergunta)


# --- CONTEÚDO ESTÁTICO ---

CONTEUDO = {
    "1": {
        "titulo": "Cadastro",
        "opcoes": {
            "1.1": "Não fiz cadastro",
            "1.2": "Já sou cadastrado",
            "1.3": "Admissão"
        }
    },
    "3": "A mensalidade vence todo dia 10 de cada mês. A contribuição mensal é de 30.00 R$",
    "4": "O frete é calculado no momento da compra quando vc escolhe a empresa transportadora.",
    "5": "Para cancelamento, envie um email para contato@salvar-se.org.br com o assunto 'Cancelamento' e informe o motivo."
}


def exibir_menu_principal():
    print("\n" + "="*30)
    print(" PINK CHAT - SALVAR")
    print(f" IA ativa: {'Claude' if IA_PROVIDER == 'anthropic' else 'Gemini'}")
    print("="*30)
    print("1. Cadastro\n2. Produtos\n3. Mensalidade\n4. Frete\n5. Cancelamento\n0. Sair")
    print("="*30)


# --- LOOP PRINCIPAL ---

if __name__ == "__main__":
    while True:
        exibir_menu_principal()
        escolha = input("Digite o número da opção ou sua dúvida: ")

        # 0. SAÍDA COM SAUDAÇÃO DINÂMICA
        if escolha == "0":
            saudacao = obter_saudacao_por_horario()
            print(f"\n{saudacao}")
            break

        # 1. CADASTRO
        elif escolha == "1":
            item = CONTEUDO["1"]
            print(f"\n----- {item['titulo']} -----")
            for sub, desc in item["opcoes"].items():
                print(f"{sub}: {desc}")
            input("\nPressione ENTER para voltar...")

        # 2. PRODUTOS E ORÇAMENTO
        elif escolha == "2":
            carrinho = realizar_orcamento()
            exibir_resumo(carrinho)
            input("\nPressione ENTER para voltar...")

        # 3, 4 e 5. TEXTOS FIXOS
        elif escolha in ["3", "4", "5"]:
            print(f"\nINFORMAÇÃO: {CONTEUDO[escolha]}")
            input("\nPressione ENTER para voltar...")

        # FALLBACK PARA INTELIGÊNCIA ARTIFICIAL
        else:
            resposta = chamar_ia_pink_chat(escolha)
            print(f"\n[IA Pink Chat]: {resposta}")
            input("\nPressione ENTER para voltar...")
