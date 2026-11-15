import sqlite3
from dataclasses import dataclass


@dataclass
class Tutor:
    id: int | None
    nome: str
    cpf: str
    data_nascimento: str
    email: str
    telefone: str
    cep: str
    numero: str
    rua: str
    complemento: str
    bairro: str
    cidade: str
    estado: str


class TutorModel:
    def __init__(self, banco="petcare.db"):
        self.banco = banco

    # ---------- Helper de conexão ----------
    def _conectar(self):
        conn = sqlite3.connect(self.banco)
        conn.row_factory = sqlite3.Row
        return conn

    # ---------- Cadastro ----------
    def cadastrar(self, tutor: Tutor) -> int | None:
        """
        Insere um tutor. Retorna o ID gerado ou None se o CPF já existir.
        """
        try:
            with self._conectar() as conn:
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO tutores (
                        nome, cpf, data_nascimento, email, telefone,
                        cep, rua, numero, complemento, bairro, cidade, estado
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        tutor.nome, tutor.cpf, tutor.data_nascimento,
                        tutor.email, tutor.telefone, tutor.cep, tutor.rua,
                        tutor.numero, tutor.complemento, tutor.bairro,
                        tutor.cidade, tutor.estado,
                    ),
                )
                conn.commit()
                return cur.lastrowid
        except sqlite3.IntegrityError:
            return None  # CPF duplicado

    # ---------- Busca individual ----------
    def buscar_por_id(self, tutor_id: int) -> Tutor | None:
        with self._conectar() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM tutores WHERE id = ?", (tutor_id,))
            row = cur.fetchone()
        return self._row_para_tutor(row) if row else None

    # ---------- Listagem ----------
    def listar_todos(self) -> list[Tutor]:
        """Atalho para listar tudo (ordenado por nome)."""
        return self.listar()

    def listar(self, filtro: str | None = None, limite: int | None = None,
               offset: int = 0) -> list[Tutor]:
        """
        Lista tutores com filtro opcional por nome, CPF ou e-mail.
        """
        sql = "SELECT * FROM tutores"
        params: list = []

        if filtro:
            sql += " WHERE nome LIKE ? OR cpf LIKE ? OR email LIKE ?"
            like = f"%{filtro}%"
            params.extend([like, like, like])

        sql += " ORDER BY nome COLLATE NOCASE ASC"

        if limite is not None:
            sql += " LIMIT ? OFFSET ?"
            params.extend([limite, offset])

        with self._conectar() as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            rows = cur.fetchall()

        return [self._row_para_tutor(r) for r in rows]

    # ---------- Atualização ----------
    def atualizar(self, tutor: Tutor) -> bool:
        """Atualiza um tutor existente (pelo id). Retorna True se alterou."""
        try:
            with self._conectar() as conn:
                cur = conn.cursor()
                cur.execute(
                    """
                    UPDATE tutores SET
                        nome = ?, cpf = ?, data_nascimento = ?, email = ?,
                        telefone = ?, cep = ?, rua = ?, numero = ?,
                        complemento = ?, bairro = ?, cidade = ?, estado = ?
                    WHERE id = ?
                    """,
                    (
                        tutor.nome, tutor.cpf, tutor.data_nascimento,
                        tutor.email, tutor.telefone, tutor.cep, tutor.rua,
                        tutor.numero, tutor.complemento, tutor.bairro,
                        tutor.cidade, tutor.estado, tutor.id,
                    ),
                )
                conn.commit()
                return cur.rowcount > 0
        except sqlite3.IntegrityError:
            return False  # CPF duplicado em outro tutor

    # ---------- Remoção ----------
    def excluir(self, tutor_id: int) -> bool:
        """
        Remove o tutor. Retorna False se houver pets vinculados (FK).
        """
        try:
            with self._conectar() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM tutores WHERE id = ?", (tutor_id,))
                conn.commit()
                return cur.rowcount > 0
        except sqlite3.IntegrityError:
            return False  # tutor ainda tem pets

    # ---------- Conversão ----------
    @staticmethod
    def _row_para_tutor(row: sqlite3.Row) -> Tutor:
        return Tutor(
            id=row["id"],
            nome=row["nome"],
            cpf=row["cpf"],
            data_nascimento=row["data_nascimento"] or "",
            email=row["email"] or "",
            telefone=row["telefone"] or "",
            cep=row["cep"] or "",
            numero=row["numero"] or "",
            rua=row["rua"] or "",
            complemento=row["complemento"] or "",
            bairro=row["bairro"] or "",
            cidade=row["cidade"] or "",
            estado=row["estado"] or "",
        )