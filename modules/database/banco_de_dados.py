import sqlite3

conn = sqlite3.connect('pinkchat.db')
cursor = conn.cursor()

# Criar tabela de produtos
cursor.execute('''
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    preco REAL NOT NULL,
    desconto REAL NOT NULL
)
''')

# Inserir produtos na tabela
produtos_iniciais = [
    ("Óleo de CBD 25mg/ml", 315.00, 0.10),
    ("Óleo de CBD 50mg/ml", 420.00, 0.10),
    ("Óleo de CBD/THC 1:1 25mg/ml", 315.00, 0.10),
    ("Óleo de THC 25mg/ml", 315.00, 0.10),
    ("Óleo de THC 5mg/ml", 210.00, 0.10),
    ("Flores de THC (10g)", 420.00, 0.10),
    ("Flores de CBD (10g)", 280.00, 0.10)
]

for produto in produtos_iniciais:
    cursor.execute('''
        INSERT OR REPLACE INTO produtos (nome, preco, desconto) VALUES (?, ?, ?)
    ''', produto)

conn.commit()
conn.close()
print("Banco de dados criado e produtos inseridos com sucesso!")