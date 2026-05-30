# -*- coding: utf-8 -*-
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CAMINHO_DB = os.path.join(BASE_DIR, "pinkchat.db")

PRODUTOS_INICIAIS = [
    ("Óleo de CBD 25mg/ml",                  315.00, 0.10),
    ("Óleo de CBD 50mg/ml",                  420.00, 0.10),
    ("Óleo de CBD/THC 1:1 25mg/ml",          315.00, 0.10),
    ("Óleo de THC 25mg/ml",                  315.00, 0.10),
    ("Óleo de THC 5mg/ml",                   210.00, 0.10),
    ("Flores de CBD (10g) — Purple Punch",   280.00, 0.10),
    ("Flores de CBD/CBG (10g) — CBG-FORCE",  280.00, 0.10),
    ("Flores de THC (10g) — White Widow",    420.00, 0.10),
    ("Flores de THC (10g) — Zkittlez",       420.00, 0.10),
]

class SetupDB:
    def __init__(self, caminho: str = CAMINHO_DB):
        self.caminho = caminho

    def _conectar(self):
        return sqlite3.connect(self.caminho)

    def criar_tabelas(self, cursor):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                nome     TEXT    NOT NULL UNIQUE,
                preco    REAL    NOT NULL,
                desconto REAL    NOT NULL DEFAULT 0.0
            )
        """)

    def popular_produtos(self, cursor):
        cursor.execute("DELETE FROM produtos")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='produtos'")
        cursor.executemany(
            "INSERT INTO produtos (nome, preco, desconto) VALUES (?, ?, ?)",
            PRODUTOS_INICIAIS,
        )
        return len(PRODUTOS_INICIAIS)

    def listar_produtos(self):
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome, preco, desconto FROM produtos ORDER BY id")
            return cursor.fetchall()

    def inicializar(self):
        print("\n🔍 --- SINCRONIZANDO PRODUTOS ---")
        try:
            with self._conectar() as conn:
                cursor = conn.cursor()
                self.criar_tabelas(cursor)
                total = self.popular_produtos(cursor)
                conn.commit()
            print(f"✅ Banco '{os.path.basename(self.caminho)}' configurado!")
            print(f"   {total} produtos inseridos.\n")
            self._exibir_tabela()
        except sqlite3.OperationalError as e:
            print(f"❌ Erro de banco: {e}")
        except OSError as e:
            print(f"❌ Erro de arquivo: {e}")

    def _exibir_tabela(self):
        print(f"{'ID':<4} {'Produto':<40} {'Preco':>8}  {'Desconto':>9}")
        print("─" * 66)
        for id_, nome, preco, desconto in self.listar_produtos():
            print(f"{id_:<4} {nome:<40} R${preco:>7.2f}  {int(desconto*100):>8}%")
        print()

if __name__ == "__main__":
    SetupDB().inicializar()