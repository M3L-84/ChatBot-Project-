# bot.py

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
    print("\n--- MENU PRINCIPAL ---") 
    print("1. Cadastro")
    print("2. Produtos")
    print("3. Mensalidade")
    print("4. Frete")
    print("5. Cancelamento")
    print("0. Sair")    

if __name__ == "__main__":
    exibir_menu_principal()
