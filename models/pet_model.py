import sqlite3
from dataclasses import dataclass


# ============================================================
# Modelo (dataclass)
# ============================================================
@dataclass
class Pet:
    id: int | None
    nome: str
    especie: str
    raca: str
    porte: str
    data_nascimento: str
    peso: float | None
    observacoes: str
    tutor_id: int


# ============================================================
# Exceções específicas
# ============================================================
class PetError(Exception):
    """Erro genérico de regra de negócio do Pet."""


class TutorObrigatorioError(PetError):
    """Pet sem tutor_id ou tutor inexistente."""


class PetComAgendamentosError(PetError):
    """Não é possível excluir um pet que possui agendamentos."""


# ============================================================
# Model
# ============================================================
class PetModel:
    def __init__(self, banco="petcare.db"):
        self.banco = banco

    # ---------- Helper ----------
    def _conectar(self):
        conn = sqlite3.connect(self.banco)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    @staticmethod
    def _row_para_dict(row: sqlite3.Row) -> dict:
        """
        Converte uma linha do banco (que já vem com o JOIN do tutor)
        em um dicionário pronto para o JSON/Frontend.
        """
        return {
            "id": row["id"],
            "nome": row["nome"],
            "especie": row["especie"],
            "raca": row["raca"] or "",
            "porte": row["porte"] or "",
            "data_nascimento": row["data_nascimento"] or "",
            "peso": float(row["peso"]) if row["peso"] is not None else None,
            "observacoes": row["observacoes"] or "",
            "tutor_id": row["tutor_id"],
            "tutor_nome": row["tutor_nome"],  # <-- Vem do JOIN
        }

    @staticmethod
    def _row_para_pet(row: sqlite3.Row) -> Pet:
        """Usado apenas para o método de buscar_por_id (que não tem JOIN)."""
        return Pet(
            id=row["id"],
            nome=row["nome"],
            especie=row["especie"],
            raca=row["raca"] or "",
            porte=row["porte"] or "",
            data_nascimento=row["data_nascimento"] or "",
            peso=float(row["peso"]) if row["peso"] is not None else None,
            observacoes=row["observacoes"] or "",
            tutor_id=row["tutor_id"],
        )

    # ============================================================
    # CADASTRAR — regra de negócio principal
    # ============================================================
    def cadastrar(self, pet: Pet) -> int:
        # 1) Validação: tutor_id obrigatório
        if not pet.tutor_id or pet.tutor_id <= 0:
            raise TutorObrigatorioError("Todo pet precisa de um tutor responsável.")

        with self._conectar() as conn:
            cur = conn.cursor()

            # 2) Validação: tutor existe no banco
            cur.execute("SELECT 1 FROM tutores WHERE id = ?", (pet.tutor_id,))
            if cur.fetchone() is None:
                raise TutorObrigatorioError(f"Tutor id={pet.tutor_id} não encontrado.")

            # 3) Validação: nome obrigatório
            if not pet.nome or not pet.nome.strip():
                raise PetError("O nome do pet é obrigatório.")

            # 4) Inserção
            try:
                cur.execute(
                    """
                    INSERT INTO pets (
                        nome, especie, raca, porte,
                        data_nascimento, peso, observacoes, tutor_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        pet.nome.strip(), pet.especie, pet.raca or None,
                        pet.porte or None, pet.data_nascimento or None,
                        pet.peso, pet.observacoes or None, pet.tutor_id,
                    ),
                )
                conn.commit()
                return cur.lastrowid
            except sqlite3.IntegrityError as e:
                raise PetError(f"Erro ao cadastrar pet: {e}") from e

    # ============================================================
    # LISTAGENS (com JOIN para trazer o nome do tutor)
    # ============================================================
    def listar_todos(self) -> list[dict]:
        """Todos os pets + nome do tutor (para o painel esquerdo)."""
        sql = """
            SELECT p.*, t.nome AS tutor_nome
            FROM pets p
            INNER JOIN tutores t ON t.id = p.tutor_id
            ORDER BY p.nome COLLATE NOCASE ASC
        """
        with self._conectar() as conn:
            cur = conn.cursor()
            cur.execute(sql)
            return [self._row_para_dict(r) for r in cur.fetchall()]

    def listar(self, filtro: str | None = None) -> list[dict]:
        """Lista com busca (nome do pet ou nome do tutor)."""
        sql = """
            SELECT p.*, t.nome AS tutor_nome
            FROM pets p
            INNER JOIN tutores t ON t.id = p.tutor_id
        """
        params: list = []

        if filtro:
            sql += " WHERE p.nome LIKE ? OR t.nome LIKE ?"
            like = f"%{filtro}%"
            params.extend([like, like])

        sql += " ORDER BY p.nome COLLATE NOCASE ASC"

        with self._conectar() as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            return [self._row_para_dict(r) for r in cur.fetchall()]

    def listar_por_tutor(self, tutor_id: int) -> list[Pet]:
        """Pets de um tutor específico (para o dropdown de agendamento)."""
        with self._conectar() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM pets WHERE tutor_id = ? ORDER BY nome COLLATE NOCASE ASC",
                (tutor_id,),
            )
            return [self._row_para_pet(r) for r in cur.fetchall()]

    # ============================================================
    # BUSCAR
    # ============================================================
    def buscar_por_id(self, pet_id: int) -> Pet | None:
        with self._conectar() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM pets WHERE id = ?", (pet_id,))
            row = cur.fetchone()
        return self._row_para_pet(row) if row else None

    # ============================================================
    # ATUALIZAR
    # ============================================================
    def atualizar(self, pet_id: int, dados: dict) -> bool:
        if not dados:
            raise PetError("Nenhum campo para atualizar.")

        if "tutor_id" in dados:
            novo_tutor = dados["tutor_id"]
            if not novo_tutor or novo_tutor <= 0:
                raise TutorObrigatorioError("Todo pet precisa de um tutor responsável.")
            with self._conectar() as conn:
                cur = conn.cursor()
                cur.execute("SELECT 1 FROM tutores WHERE id = ?", (novo_tutor,))
                if cur.fetchone() is None:
                    raise TutorObrigatorioError(f"Tutor id={novo_tutor} não encontrado.")

        colunas_permitidas = {
            "nome", "especie", "raca", "porte",
            "data_nascimento", "peso", "observacoes", "tutor_id",
        }
        campos = [c for c in dados.keys() if c in colunas_permitidas]
        if not campos:
            raise PetError("Nenhum campo válido para atualizar.")

        set_sql = ", ".join(f"{c} = ?" for c in campos)
        valores = [dados[c] for c in campos] + [pet_id]

        with self._conectar() as conn:
            cur = conn.cursor()
            try:
                cur.execute(f"UPDATE pets SET {set_sql} WHERE id = ?", valores)
                conn.commit()
                return cur.rowcount > 0
            except sqlite3.IntegrityError as e:
                raise PetError(f"Erro ao atualizar pet: {e}") from e

    # ============================================================
    # DELETAR
    # ============================================================
    def deletar(self, pet_id: int) -> bool:
        with self._conectar() as conn:
            cur = conn.cursor()

            cur.execute(
                "SELECT COUNT(*) AS total FROM agendamentos WHERE pet_id = ?",
                (pet_id,),
            )
            total = cur.fetchone()["total"]
            if total > 0:
                raise PetComAgendamentosError(
                    f"Este pet possui {total} agendamento(s) e não pode ser excluído."
                )

            cur.execute("DELETE FROM pets WHERE id = ?", (pet_id,))
            conn.commit()
            return cur.rowcount > 0