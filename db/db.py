import sqlite3
import os

# Caminho absoluto para a raiz do projeto (um nível acima de db/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "petcare.db")

print(f"📁 Criando banco em: {DB_PATH}")

conexao = sqlite3.connect(DB_PATH)
cursor = conexao.cursor()

# Ativa verificação de chaves estrangeiras
cursor.execute("PRAGMA foreign_keys = ON")

# ===================== TABELAS =====================
cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome VARCHAR(255) NOT NULL,
        username VARCHAR(30) NOT NULL UNIQUE,
        cpf VARCHAR(14) UNIQUE NOT NULL,
        senha VARCHAR(255) NOT NULL,
        criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS tutores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome VARCHAR(255) NOT NULL,
        cpf VARCHAR(14) UNIQUE NOT NULL,
        data_nascimento DATE,
        email VARCHAR(100),
        telefone VARCHAR(20),
        cep VARCHAR(9),
        rua VARCHAR(255),
        numero VARCHAR(10),
        complemento VARCHAR(255),
        bairro VARCHAR(255),
        cidade VARCHAR(255),
        estado CHAR(2),
        criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS pets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome VARCHAR(255) NOT NULL,
        especie VARCHAR(255) NOT NULL,
        raca VARCHAR(50),
        porte VARCHAR(20),
        data_nascimento DATE,
        peso DECIMAL(5,2),
        observacoes TEXT,
        tutor_id INTEGER NOT NULL,
        criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (tutor_id) REFERENCES tutores(id)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS agendamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pet_id INTEGER NOT NULL,
        servico VARCHAR(50) NOT NULL,
        data DATE NOT NULL,
        horario TIME NOT NULL,
        observacoes TEXT,
        status VARCHAR(20) DEFAULT 'Agendado',
        FOREIGN KEY (pet_id) REFERENCES pets(id)
    )
""")

conexao.commit()

# ===================== VERIFICAÇÃO =====================
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tabelas = [row[0] for row in cursor.fetchall()]
print(f"✅ Tabelas criadas: {tabelas}")

conexao.close()