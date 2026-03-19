# bot.py
import os
import pytz
from datetime import datetime
from dotenv import load_dotenv
from google import genai
import sqlite3

load_dotenv()
chave = os.getenv("GOOGLE_API_KEY")

# --- FUNÇÕES DE APOIO ---

def obter_saudacao_por_horario():
    fuso_br = pytz.timezone("America/Sao_Paulo")
    hora_atual = datetime.now(fuso_br).hour
    
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

def buscar_produtos_no_banco():
    conn = sqlite3.connect('pinkchat.db')
    cursor = conn.cursor()
    cursor.execute('SELECT nome, preco, (preco * (1 - desconto)) FROM produtos')
    resultados = cursor.fetchall()
    conn.close()
    return resultados

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
    print("1. Cadastro")
    print("2. Produtos")
    print("3. Mensalidade")
    print("4. Frete")
    print("5. Cancelamento")
    print("0. Sair")
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
            print("A Salvar agradece e deseja um bom dia! 👋")
            break

        # 1. CADASTRO
        elif escolha == "1":
            item = CONTEUDO["1"]
            print(f"\n--- {item['titulo']} ---")
            for sub, desc in item["opcoes"].items():
                print(f"{sub}: {desc}")
            input("\nPressione ENTER para voltar...")

        # 2. PRODUTOS E ORÇAMENTO (SISTEMA DE CARRINHO)
        elif escolha == "2":
            carrinho = []
            while True:
                print("\n------ PRODUTOS E ORÇAMENTO ------")
                produtos = buscar_produtos_no_banco()
                for i, p in enumerate(produtos, 1):
                    print(f" {i}. {p[0]} - R$ {p[2]:.2f}")
                print("0. Finalizar orçamento e retornar")
                
                try:
                    sub_escolha = int(input("\nEscolha o produto ou 0 para sair: "))
                    if sub_escolha == 0: break
                    
                    if 1 <= sub_escolha <= len(produtos):
                        p_sel = produtos[sub_escolha-1]
                        qtd = int(input(f"Quantidade de '{p_sel[0]}'? (Máx 6): "))
                        if 1 <= qtd <= 6:
                            carrinho.append({"nome": p_sel[0], "qtd": qtd, "subtotal": p_sel[2] * qtd})
                            print("✅ Adicionado!")
                        else:
                            print("⚠️ Máximo 6 unidades.")
                    else:
                        print("⚠️ Opção inválida.")
                except ValueError:
                    print("⚠️ Digite apenas números.")

            if carrinho:
                print("\n" + "="*40)
                print("         RESUMO DO ORÇAMENTO")
                print("="*40)
                total = 0
                for item_c in carrinho:
                    print(f"{item_c['qtd']}x {item_c['nome']:.<25} R$ {item_c['subtotal']:>8.2f}")
                    total += item_c['subtotal']
                print("-" * 40)
                print(f"TOTAL GERAL: {' ':<18} R$ {total:>8.2f}")
                print("="*40)
            input("\nPressione ENTER para continuar...")

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