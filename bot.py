# bot.py
import os
import pytz
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from calculadora import realizar_orcamento, exibir_resumo

load_dotenv()
chave = os.getenv("GOOGLE_API_KEY")

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

def chamar_ia_pink_chat(perguntar_usuario):
    if not chave:
        return "Ops! Meu sistema de IA está descansando. Use o menu!"
    try:
        client = genai.Client(api_key=chave)
        prompt = (
            "Você é o assistente virtual da Salvar-se (Pink Chat). "
            "Sua missão é ser acolhedor e informativo sobre Cannabis Medicinal. "
            "Se não souber a resposta ou for algo complexo, oriente a falar com o suporte no menu 5."
            "Mantenha respostas curtas, claras e amigáveis."
        )
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=f"{prompt}\n\nPergunta do Cliente: {perguntar_usuario}"
        )
        return response.text
    except Exception:
        return "No momento só consigo responder pelas opções do menu (1 a 5)."

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
    print("      PINK CHAT - SALVAR")
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

        # 2. PRODUTOS E ORÇAMENTO (Usando o novo módulo)
        elif escolha == "2":
            # Chamamos a lógica que está no arquivo calcularora.py
            carrinho = realizar_orcamento()
            exibir_resumo(carrinho)
            input("\nPressione ENTER para voltar...")

        # 3, 4 e 5. TEXTOS FIXOS
        elif escolha in ["3", "4", "5"]:
            print(f"\nINFORMAÇÃO: {CONTEUDO[escolha]}")
            input("\nPressione ENTER para voltar...")

        # FALLBACK PARA INTELIGÊNCIA ARTIFICIAL
        else:
            print("\n🤖 Consultando assistente IA...")
            resposta = chamar_ia_pink_chat(escolha)
            print(f"\n[IA Pink Chat]: {resposta}")
            input("\nPressione ENTER para voltar...")