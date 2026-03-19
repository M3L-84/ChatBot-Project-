import sqlite3

def buscar_produtos_no_banco():
    """Conecta ao banco de dados e retorna a lista de produtos com preços e descontos."""
    conn = sqlite3.connect('pinkchat.db')
    cursor = conn.cursor()
    # Busca Nome, Preço Original e Preço com Desconto
    cursor.execute('SELECT nome, preco, (preco * (1 - desconto)) FROM produtos')
    resultados = cursor.fetchall()
    conn.close()
    return resultados

def realizar_orcamento():
    """
    Executa a lógica de seleção de produtos e cálculo de subtotal.
    Retorna uma lista de dicionários com os itens do carrinho.
    """
    carrinho = []
    while True:
        print("\n--- PRODUTOS E ORÇAMENTO ---")
        produtos = buscar_produtos_no_banco()
        
        for i, p in enumerate(produtos, 1):
            print(f" {i}. {p[0]} - R$ {p[2]:.2f}")
        
        print("0. Finalizar orçamento e retornar")
        
        try:
            sub_escolha = int(input("\nEscolha o produto ou 0 para sair: "))
            if sub_escolha == 0: 
                break
            
            if 1 <= sub_escolha <= len(produtos):
                p_sel = produtos[sub_escolha-1]
                nome_produto = p_sel[0]
                preco_unitario = p_sel[2]
                
                qtd = int(input(f"Quantidade de '{nome_produto}'? (Máx 6): "))
                
                if 1 <= qtd <= 6:
                    carrinho.append({
                        "nome": nome_produto, 
                        "qtd": qtd, 
                        "subtotal": preco_unitario * qtd
                    })
                    print(f"✅ {qtd}x {nome_produto} adicionado!")
                else:
                    print("⚠️ Limite de 6 unidades por produto excedido.")
            else:
                print("⚠️ Opção inválida. Escolha um número da lista.")
                
        except ValueError:
            print("⚠️ Erro: Digite apenas números inteiros.")
            
    return carrinho

def exibir_resumo(carrinho):
    """Formata e exibe o resumo visual do orçamento final."""
    if not carrinho:
        print("\nNenhum item selecionado para orçamento.")
        return

    print("\n" + "="*40)
    print("         RESUMO DO ORÇAMENTO")
    print("="*40)
    total_geral = 0
    for item in carrinho:
        print(f"{item['qtd']}x {item['nome']:.<25} R$ {item['subtotal']:>8.2f}")
        total_geral += item['subtotal']
    
    print("-" * 40)
    print(f"TOTAL GERAL: {' ':<18} R$ {total_geral:>8.2f}")
    # Usando o cupom salvar10, o cliente tem 10% de desconto no total
    desconto = total_geral * 0.10
    print(f"DESCONTO (salvar10): {' ':<11} R$ {desconto:>8.2f}")
    print(f"TOTAL COM DESCONTO: {' ':<7} R$ {total_geral - desconto:>8.2f}")
    print("="*40)