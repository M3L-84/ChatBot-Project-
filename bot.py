# bot.py

import sqlite3

def buscar_produtos_no_banco():
    conn = sqlite3.connect('pinkchat.db')
    cursor = conn.cursor()
    cursor.execute('SELECT nome, preco, (preco * (1 - desconto))FROM produtos')
    resultados = cursor.fetchall()
    conn.close()
    return resultados

CONTEUDO = {
    "1": {
        "titulo": "Cadastro",
        "opcoes": {
            "1.1": "Não fiz cadastro",
            "1.2": "Já sou cadastrado",
            "1.3": "Admissão"
        }
    },

    "2": {
        "titulo": "Produtos",
        "tabela": [
            "Óleo de CBD 25mg/ml: R$ 315.00 - 10% = R$ 283.50",
            "Óleo de CBD 50mg/ml: R$ 420.00 - 10% = R$ 378.00",
            "Óleo de CBD/THC 1:1 25mg/ml: R$ 315.00 - 10% = R$ 283.50",
            "Óleo de THC 25mg/ml: R$ 315.00 - 10% = R$ 283.50",
            "Óleo de THC 5mg/ml: R$ 210.00 - 10% = R$ 189.00",
            "Flores de THC (10g): R$ 420.00 - 10% = R$ 378.00 (White Widow e Zkittlez)",
            "Flores de CBD (10g): R$ 280.00 - 10% = R$ 252.00 (Purple Punch)"
        ]
    },

    "3": "A mensalidade vence todo dia 10 de cada mês. A contribuição mensal é de 30.00 R$",
    "4": "O frete é calculado no momento da compra quando vc escolhe a empresa transportadora.",
    "5": "Para cancelamento, envie um email para contato@salvar-se.org.br com o assunto 'Cancelamento' e "
    "informe o motivo e em eguida e avisa no chat, para que a equipe do suporte realize o procedimento."
    
}

def exibir_menu_principal():
    print("\n" + "="*30)
    print("Bem-vindo ao Bot de Atendimento")
    print("="*30) 
    print("1. Cadastro")
    print("2. Produtos")
    print("3. Mensalidade")
    print("4. Frete")
    print("5. Cancelamento")
    print("0. Sair")
    print("="*30)

if __name__ == "__main__":
    while True:
        exibir_menu_principal()

        # O input sempre recebe o que o usuário digitar como texto (string)
        escolha = input("Digite o número da opção desejada ou digite 0 para sair: ")

        if escolha == "0":
            print("\nA Salvar agradece e deseja um bom dia!")
            break

        elif escolha in CONTEUDO:
            # Pegamos o item do dicionário baseado no número digitado
            item = CONTEUDO[escolha]

            # Se for o item 1 (Cadastro), exibimos as opções de cadastro
            if escolha == "1":
                print(f"\n--- {item['titulo']} ---")
                for opcao, descricao in item["opcoes"].items():
                    print(f"{opcao}: {descricao}")
            
            # Se for o item 2 (Produtos), exibimos a tabela de produtos
            elif escolha == "2":
                print("\n--- TABELA DE PRODUTOS (VIA BANCO DE DADOS) ---")
                produtos = buscar_produtos_no_banco()
                for p in produtos:
                    print(f"• {p[0]}: R$ {p[1]:.2f} - 10% OFF = R$ {p[2]:.2f}")

            # Para os itens 3, 4 e 5, exibimos o texto diretamente
            else:
                print(f"\n--- {item} ---")

        else:
            print("\n⚠️ Opção inválida! Por favor, escolha um número do menu.")

        # Pequena pausa visual antes de mostrar o menu novamente.
        input("\nPressione Enter para continuar...")