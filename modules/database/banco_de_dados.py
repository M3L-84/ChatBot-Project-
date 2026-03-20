import sqlite3
import os

# Localiza a raiz do projeto (/workspaces/ChatBot-Project-)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
caminho_db = os.path.join(BASE_DIR, 'pinkchat.db')

def inicializar_banco():
    print(f"\n🔍 --- SINCRONIZANDO PRODUTOS ---")
    
    try:
        conn = sqlite3.connect(caminho_db)
        cursor = conn.cursor()

        # Criar tabela de produtos
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            preco REAL NOT NULL,
            desconto REAL NOT NULL
        )
        ''')

        # LIMPANDO A TABELA para evitar duplicatas ao rodar várias vezes
        cursor.execute('DELETE FROM produtos')

        # Dados oficiais da Salvar-se
        produtos_iniciais = [
            ("Óleo de CBD 25mg/ml", 315.00, 0.10),
            ("Óleo de CBD 50mg/ml", 420.00, 0.10),
            ("Óleo de CBD/THC 1:1 25mg/ml", 315.00, 0.10),
            ("Óleo de THC 25mg/ml", 315.00, 0.10),
            ("Óleo de THC 5mg/ml", 210.00, 0.10),
            ("Flores de THC (10g)", 420.00, 0.10),
            ("Flores de CBD (10g)", 280.00, 0.10)
        ]

        cursor.executemany('''
            INSERT INTO produtos (nome, preco, desconto) VALUES (?, ?, ?)
        ''', produtos_iniciais)

        conn.commit()
        conn.close()
        print(f"✅ Sucesso! Apenas {len(produtos_iniciais)} itens cadastrados no banco.")
    except Exception as e:
        print(f"❌ Erro ao configurar banco: {e}")

if __name__ == "__main__":
    inicializar_banco()