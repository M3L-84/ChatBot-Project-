# modules/calculadora.py
import sqlite3, os, logging
logger = logging.getLogger(__name__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMINHO_DB = os.path.join(BASE_DIR, "pinkchat.db")
QTDE_MAX = 6
LARGURA = 58
COL_NOME = 40
CUPONS = {"salvar10": 0.10, "salvar15": 0.15, "salvar20": 0.20}

def buscar_produtos():
    try:
        with sqlite3.connect(CAMINHO_DB) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT nome, preco, desconto FROM produtos")
            return cursor.fetchall()
    except sqlite3.Error as e:
        logger.error("Erro: %s", e)
        print(f"Erro ao acessar banco: {e}")
        return []

def _exibir_catalogo(produtos, carrinho):
    print("\n" + "=" * LARGURA)
    print(f"{'TABELA DE PRODUTOS SALVAR-SE':^{LARGURA}}")
    print("=" * LARGURA)
    for i, (nome, preco, _) in enumerate(produtos, 1):
        print(f"  {i:2}. {nome:.<{COL_NOME}} R$ {preco:>7.2f}")
    print("-" * LARGURA)
    itens = sum(item["qtd"] for item in carrinho)
    status = f"Carrinho: {itens} item(s)" if carrinho else "Carrinho vazio"
    print(f"  {status}")
    print("  [r] Ver resumo   [e] Editar   [v] Voltar ao menu   [0] Finalizar")
    print("=" * LARGURA)

def _exibir_carrinho(carrinho):
    if not carrinho:
        print("\n  Carrinho vazio.")
        return
    print("\n" + "-" * LARGURA)
    for i, item in enumerate(carrinho, 1):
        subtotal = item["qtd"] * item["preco_original"]
        print(f"  {i}. {item['qtd']}x {item['nome']} = R$ {subtotal:.2f}")
    print("-" * LARGURA)

def _exibir_item_resumo(item):
    subtotal = item["qtd"] * item["preco_original"]
    economia = subtotal * item["desconto_percentual"]
    print(f"  {item['qtd']}x {item['nome']}")
    print(f"     Subtotal:     R$ {subtotal:>8.2f}")
    print(f"     Desconto:     R$ {economia:>8.2f}")
    print(f"     Com desconto: R$ {(subtotal - economia):>8.2f}")
    print("  " + "-" * 38)

def _editar_carrinho(carrinho):
    if not carrinho:
        print("  Carrinho vazio.")
        return
    while True:
        _exibir_carrinho(carrinho)
        entrada = input("  Numero para remover ou 0 para voltar: ").strip()
        if entrada == "0":
            break
        try:
            idx = int(entrada) - 1
            if 0 <= idx < len(carrinho):
                r = carrinho.pop(idx)
                print(f"  Removido: {r['qtd']}x {r['nome']}")
            else:
                print("  Numero invalido.")
        except ValueError:
            print("  Digite apenas numeros.")

def _solicitar_cupom(total_bruto):
    codigo = "salvar10"
    percentual = CUPONS[codigo]
    valor = total_bruto * percentual
    return codigo, valor

def _ler_escolha(produtos):
    entrada = input("\nEscolha: ").strip().lower()
    if entrada in ("r", "e", "v", "0"):
        return entrada
    try:
        n = int(entrada)
        if 1 <= n <= len(produtos):
            return entrada
        print("  Numero fora da lista.")
    except ValueError:
        print("  Opcao invalida.")
    return ""

def _solicitar_quantidade(nome):
    try:
        qtd = int(input(f"  Quantidade de {nome} (1-{QTDE_MAX}): "))
    except ValueError:
        print("  Digite apenas numeros.")
        return None
    if 1 <= qtd <= QTDE_MAX:
        return qtd
    print(f"  Maximo {QTDE_MAX} unidades.")
    return None

def realizar_orcamento():
    produtos = buscar_produtos()
    if not produtos:
        print("Nenhum produto encontrado.")
        return []
    carrinho = []
    cupom_codigo, cupom_valor = "", 0.0
    while True:
        _exibir_catalogo(produtos, carrinho)
        escolha = _ler_escolha(produtos)
        if not escolha:
            continue
        if escolha == "v":
            print("  Voltando ao menu...")
            return []
        if escolha == "0":
            if carrinho:
                total = sum(i["qtd"] * i["preco_original"] for i in carrinho)
                cupom_codigo, cupom_valor = _solicitar_cupom(total)
            break
        if escolha == "r":
            exibir_resumo(carrinho)
            input("  ENTER para continuar...")
            continue
        if escolha == "e":
            _editar_carrinho(carrinho)
            continue
        nome, preco, desconto = produtos[int(escolha) - 1]
        qtd = _solicitar_quantidade(nome)
        if qtd is None:
            continue
        carrinho.append({"nome": nome, "qtd": qtd, "preco_original": preco, "desconto_percentual": desconto})
        print(f"  Adicionado: {qtd}x {nome}")
    for item in carrinho:
        item["cupom_codigo"] = cupom_codigo
        item["cupom_valor"] = cupom_valor
    return carrinho

def exibir_resumo(carrinho):
    if not carrinho:
        print("\n  Nenhum item selecionado.")
        return
    print("\n" + "=" * LARGURA)
    print(f"{'RESUMO DO SEU PEDIDO':^{LARGURA}}")
    print("=" * LARGURA)
    total_bruto, total_desconto = 0.0, 0.0
    for item in carrinho:
        _exibir_item_resumo(item)
        s = item["qtd"] * item["preco_original"]
        total_bruto += s
        total_desconto += s * item["desconto_percentual"]
    total_liquido = total_bruto - total_desconto
    cupom_codigo = carrinho[0].get("cupom_codigo", "")
    cupom_valor = carrinho[0].get("cupom_valor", 0.0)
    total_final = total_liquido - cupom_valor
    print(f"\n{'TOTAL DO ORCAMENTO':^{LARGURA}}")
    print("-" * LARGURA)
    print(f"  Valor Total Bruto:   R$ {total_bruto:>8.2f}")
    print(f"  Desconto produtos:   R$ {total_desconto:>8.2f}")
    if cupom_codigo:
        label = f"Cupom {cupom_codigo}:"
        print(f"  {label:<20} R$ {cupom_valor:>8.2f}")
    print("-" * LARGURA)
    print(f"  TOTAL COM DESCONTO:  R$ {total_final:>8.2f}")
    print("=" * LARGURA)
