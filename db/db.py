import sqlite3
import os
import sys

# Caminho absoluto para a raiz do projeto (um nível acima de db/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "petcare.db")

# Garante que a raiz do projeto está no path (para importar models)
sys.path.insert(0, BASE_DIR)

print(f"📁 Criando banco em: {DB_PATH}")

# ===================== RESETAR BANCO =====================
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print("🗑️  Banco antigo removido.")

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
print("✅ Tabelas criadas.")

# ===================== INSERTS (3 por tabela) =====================
print("\n📝 Populando o banco...")

# --- 3 Usuários (com senha criptografada via UserModel) ---
from models.user_model import UserModel
user_model = UserModel(banco=DB_PATH)

usuarios = [
    ("Administrador", "admin", "111.111.111-11", "Senha@123"),
    ("Recepcionista", "recep", "222.222.222-22", "Senha@123"),
    ("Veterinário", "vet", "333.333.333-33", "Senha@123"),
]
for nome, username, cpf, senha in usuarios:
    uid = user_model.cadastrar(nome, username, cpf, senha)
    if uid:
        print(f"  ✅ Usuário '{username}' criado (id={uid})")
    else:
        print(f"  ⚠️  Usuário '{username}' já existia.")

# --- 3 Tutores ---
tutores = [
    ("João Silva", "444.444.444-44", "1990-05-15", "joao@email.com",
     "(11) 99999-1111", "01000-000", "Rua das Flores", "10", "Apto 12",
     "Centro", "São Paulo", "SP"),
    ("Maria Souza", "555.555.555-55", "1985-10-20", "maria@email.com",
     "(11) 99999-2222", "02000-000", "Av. Paulista", "20", "",
     "Bela Vista", "São Paulo", "SP"),
    ("Pedro Santos", "666.666.666-66", "2000-01-30", "pedro@email.com",
     "(11) 99999-3333", "03000-000", "Rua Augusta", "30", "",
     "Consolação", "São Paulo", "SP"),
]
for t in tutores:
    try:
        cursor.execute("""
            INSERT INTO tutores
            (nome, cpf, data_nascimento, email, telefone, cep, rua, numero,
             complemento, bairro, cidade, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, t)
        print(f"  ✅ Tutor '{t[0]}' inserido.")
    except sqlite3.IntegrityError:
        print(f"  ⚠️  Tutor '{t[0]}' já existia.")

# --- 3 Pets ---
pets = [
    ("Rex", "Cão", "Poodle", "Pequeno", "2020-03-10", 5.5, "Alérgico a dipirona", 1),
    ("Mimi", "Gato", "Persa", "Médio", "2019-07-22", 4.0, "Muito dócil", 2),
    ("Thor", "Cão", "Bulldog", "Grande", "2018-11-05", 15.0, "Precisa de acompanhamento", 3),
]
for p in pets:
    cursor.execute("""
        INSERT INTO pets
        (nome, especie, raca, porte, data_nascimento, peso, observacoes, tutor_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, p)
    print(f"  ✅ Pet '{p[0]}' inserido.")

# --- 3 Agendamentos ---
agendamentos = [
    (1, "Consulta de Rotina", "2026-11-20", "10:00", "Tosse seca há 3 dias"),
    (2, "Vacinação", "2026-11-21", "14:30", "Vacina anual"),
    (3, "Banho e Tosa", "2026-11-22", "09:00", ""),
]
for a in agendamentos:
    cursor.execute("""
        INSERT INTO agendamentos
        (pet_id, servico, data, horario, observacoes)
        VALUES (?, ?, ?, ?, ?)
    """, a)
    print(f"  ✅ Agendamento '{a[1]}' inserido.")

conexao.commit()

# ===================== VERIFICAÇÃO =====================
print("\n📊 Contagem de registros por tabela:")
for tabela in ["usuarios", "tutores", "pets", "agendamentos"]:
    cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
    total = cursor.fetchone()[0]
    print(f"  {tabela}: {total}")

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tabelas = [row[0] for row in cursor.fetchall()]
print(f"\n✅ Tabelas no banco: {tabelas}")

conexao.close()
print("\n🎉 Banco criado e populado com sucesso!")