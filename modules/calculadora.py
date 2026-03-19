import sqlite3
import os

def buscar_produtos_no_banco():
    """Conecta ao banco de dados e retorna a lista de produtos com preços e descontos."""
    # Garante o caminho correto para o banco na raiz
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    caminho_db = os.path.join(BASE_DIR, 'pinkchat.db')
    
    try:
        conn = sqlite3.connect(caminho_db)
        cursor = conn.cursor()
        # Busca Nome, Preço Original e a porcentagem de desconto (ex: 0.10)
        cursor.execute('SELECT nome, preco, desconto FROM produtos')
        resultados = cursor.fetchall()
        conn.close()
        return resultados
    except sqlite3.Error as e:
        print(f"⚠️ Erro ao acessar o banco de dados: {e}")
        return []

def realizar_orcamento():
    """Executa a lógica de seleção de produtos no terminal."""
    carrinho = []
    produtos = buscar_produtos_no_banco()
    
    if not produtos:
        print("⚠️ Nenhum produto encontrado no banco.")
        return []

    while True:
        print("\n" + "="*45)
        print(f"{'TABELA DE PRODUTOS SALVAR-SE':^45}")
        print("="*45)
        for i, p in enumerate(produtos, 1):
            # p[0]=nome, p[1]=preco_cheio
            print(f" {i:2}. {p[0]:.<30} R$ {p[1]:>8.2f}")
        
        print(f" 0. {'Finalizar seleções e ver resumo':.<30}")
        print("="*45)
        
        try:
            escolha = int(input("\nEscolha o número do produto (ou 0 para sair): "))
            if escolha == 0: break
            
            if 1 <= escolha <= len(produtos):
                p_sel = produtos[escolha-1]
                qtd = int(input(f"Quantidade de '{p_sel[0]}'? (Máx 6): "))
                
                if 1 <= qtd <= 6:
                    carrinho.append({
                        "nome": p_sel[0], 
                        "qtd": qtd, 
                        "preco_original": p_sel[1],
                        "desconto_percentual": p_sel[2]
                    })
                    print(f"✅ Adicionado: {qtd}x {p_sel[0]}")
                else:
                    print("⚠️ Quantidade permitida: 1 a 6 unidades.")
            else:
                print("⚠️ Opção inválida.")
        except ValueError:
            print("⚠️ Digite apenas números.")
            
    return carrinho

def exibir_resumo(carrinho):
    """Exibe o resumo conforme solicitado: Total, Com Desconto e Economia."""
    if not carrinho:
        print("\n[!] Nenhum item selecionado.")
        return

    print("\n" + "─"*45)
    print(f"{'RESUMO DO SEU PEDIDO':^45}")
    print("─"*45)
    
    total_bruto_geral = 0
    total_com_desconto_geral = 0
    
    for item in carrinho:
        # Cálculos por item
        subtotal_bruto = item['qtd'] * item['preco_original']
        valor_desconto = subtotal_bruto * item['desconto_percentual']
        subtotal_com_desconto = subtotal_bruto - valor_desconto
        
        # Exibição individual conforme o exemplo: 2 Óleo de CBD 25mg/ml = 630,00
        print(f"{item['qtd']} {item['nome']} = {subtotal_bruto:.2f}")
        print(f"Com 10% de desconto = {subtotal_com_desconto:.2f}")
        print(f"Economia de - {valor_desconto:.2f} R$")
        print("-" * 20)
        
        total_bruto_geral += subtotal_bruto
        total_com_desconto_geral += subtotal_com_desconto

    if len(carrinho) > 1:
        economia_total = total_bruto_geral - total_com_desconto_geral
        print(f"\n{'TOTAL DO ORÇAMENTO':^45}")
        print(f"Valor Total Bruto: {' ':<12} R$ {total_bruto_geral:>8.2f}")
        print(f"Total com Desconto: {' ':<11} R$ {total_com_desconto_geral:>8.2f}")
        print(f"ECONOMIA TOTAL: {' ':<15} R$ {economia_total:>8.2f}")
    
    print("─"*45)