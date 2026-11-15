import sqlite3
import hashlib
import secrets
from dataclasses import dataclass, field


@dataclass
class User:
    """Representa um usuário do sistema"""
    id: int | None
    username: str
    nome: str
    senha: str = field(repr=False)  # não aparece em repr()


class UserModel:
    def __init__(self, banco="petcare.db"):
        self.banco = banco

    # ---------- Helpers de conexão ----------
    def _conectar(self):
        conn = sqlite3.connect(self.banco)
        conn.row_factory = sqlite3.Row
        return conn

    # ---------- Hash de senha ----------
    @staticmethod
    def gerar_hash(senha: str) -> str:
        """
        Gera hash da senha no formato: salt$hash (ambos hex).
        O salt é aleatório por usuário (protege contra rainbow tables).
        """
        salt = secrets.token_hex(16)  # 32 caracteres hex
        hash_obj = hashlib.pbkdf2_hmac(
            "sha256",
            senha.encode("utf-8"),
            bytes.fromhex(salt),
            100_000,  # iterações (aumenta custo de força bruta)
        )
        return f"{salt}${hash_obj.hex()}"

    @staticmethod
    def verificar_senha(senha: str, hash_armazenado: str) -> bool:
        """Compara senha em texto puro com o hash salvo."""
        try:
            salt, hash_esperado = hash_armazenado.split("$", 1)
            hash_calculado = hashlib.pbkdf2_hmac(
                "sha256",
                senha.encode("utf-8"),
                bytes.fromhex(salt),
                100_000,
            ).hex()
            # compare_digest evita timing attacks
            return secrets.compare_digest(hash_calculado, hash_esperado)
        except (ValueError, AttributeError):
            return False

    # ---------- CRUD ----------
    def cadastrar(self, nome: str, username: str, cpf: str, senha: str) -> int | None:
        """
        Cria um novo usuário criptografando a senha.
        Retorna o ID do usuário criado, ou None se o CPF/username já existir.
        """
        senha_hash = self.gerar_hash(senha)

        try:
            with self._conectar() as conn:
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO usuarios (nome, username, cpf, senha)
                    VALUES (?, ?, ?, ?)
                    """,
                    (nome, username, cpf, senha_hash),
                )
                conn.commit()
                return cur.lastrowid
        except sqlite3.IntegrityError:
            # CPF ou username já cadastrado
            return None

    def autenticar_por_cpf(self, cpf: str, senha: str) -> User | None:
        """Variante que autentica pelo CPF (útil se o login for por CPF)."""
        with self._conectar() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, nome, username, senha FROM usuarios WHERE cpf = ?",
                (cpf,),
            )
            row = cur.fetchone()

        if row is None or not self.verificar_senha(senha, row["senha"]):
            return None

        return User(
            id=row["id"],
            username=row["username"],
            nome=row["nome"],
            senha=row["senha"],
        )

    def buscar_por_cpf(self, cpf: str) -> User | None:
        """Retorna os dados do usuário pelo CPF (sem validar senha)."""
        with self._conectar() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, nome, username, senha FROM usuarios WHERE cpf = ?",
                (cpf,),
            )
            row = cur.fetchone()

        if row is None:
            return None

        return User(
            id=row["id"],
            username=row["username"],
            nome=row["nome"],
            senha=row["senha"],
        )