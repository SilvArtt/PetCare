import sqlite3
from dataclasses import dataclass


# ============================================================
# Constantes de status
# ============================================================
STATUS_AGENDADO = "Agendado"
STATUS_CONCLUIDO = "Concluído"
STATUS_CANCELADO = "Cancelado"

STATUS_VALIDOS = {STATUS_AGENDADO, STATUS_CONCLUIDO, STATUS_CANCELADO}


# ============================================================
# Modelo (dataclass) — usado só para CADASTRAR/BUSCAR
# ============================================================
@dataclass
class Agendamento:
    id: int | None
    pet_id: int
    servico: str
    data: str
    horario: str
    observacoes: str
    status: str = STATUS_AGENDADO


# ============================================================
# Exceções
# ============================================================
class AgendamentoError(Exception):
    """Erro genérico de regra de negócio do Agendamento."""


class AgendamentoDuplicadoError(AgendamentoError):
    """Já existe agendamento para o mesmo pet na mesma data/horário."""


class PetInexistenteError(AgendamentoError):
    """O pet_id informado não existe."""


class StatusInvalidoError(AgendamentoError):
    """Status fora dos valores permitidos."""


# ============================================================
# Model
# ============================================================
class AgendamentoModel:
    def __init__(self, banco="petcare.db"):
        self.banco = banco

    # ---------- Helper ----------
    def _conectar(self):
        conn = sqlite3.connect(self.banco)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    # ---------- Conversão para dict (com JOIN do pet) ----------
    @staticmethod
    def _row_para_dict(row: sqlite3.Row) -> dict:
        return {
            "id": row["id"],
            "pet_id": row["pet_id"],
            "pet_nome": row["pet_nome"] if "pet_nome" in row.keys() else "",
            "pet_observacoes": row["pet_observacoes"] if "pet_observacoes" in row.keys() else "",
            "servico": row["servico"],
            "data": row["data"],
            "horario": row["horario"],
            "observacoes": row["observacoes"] or "",
            "status": row["Status"],
        }

    @staticmethod
    def _row_para_agendamento(row: sqlite3.Row) -> Agendamento:
        return Agendamento(
            id=row["id"],
            pet_id=row["pet_id"],
            servico=row["servico"],
            data=row["data"],
            horario=row["horario"],
            observacoes=row["observacoes"] or "",
            status=row["Status"],
        )

    # ============================================================
    # CADASTRAR
    # ============================================================
    def cadastrar(self, agendamento: Agendamento) -> int:
        if not agendamento.pet_id or agendamento.pet_id <= 0:
            raise AgendamentoError("pet_id é obrigatório.")
        if not agendamento.data or not agendamento.horario:
            raise AgendamentoError("Data e horário são obrigatórios.")

        status_inicial = agendamento.status or STATUS_AGENDADO
        if status_inicial not in STATUS_VALIDOS:
            raise StatusInvalidoError(
                f"Status '{status_inicial}' inválido. "
                f"Use: {', '.join(sorted(STATUS_VALIDOS))}."
            )

        with self._conectar() as conn:
            cur = conn.cursor()

            cur.execute("SELECT 1 FROM pets WHERE id = ?", (agendamento.pet_id,))
            if cur.fetchone() is None:
                raise PetInexistenteError(
                    f"Pet id={agendamento.pet_id} não encontrado."
                )

            cur.execute(
                """
                SELECT id, status FROM agendamentos
                WHERE pet_id = ? AND data = ? AND horario = ?
                """,
                (agendamento.pet_id, agendamento.data, agendamento.horario),
            )
            existente = cur.fetchone()
            if existente is not None and existente["status"] != STATUS_CANCELADO:
                raise AgendamentoDuplicadoError(
                    "Este pet já possui agendamento nesta data e horário."
                )

            cur.execute(
                """
                INSERT INTO agendamentos (
                    pet_id, servico, data, horario, observacoes, Status
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    agendamento.pet_id,
                    agendamento.servico,
                    agendamento.data,
                    agendamento.horario,
                    agendamento.observacoes or None,
                    status_inicial,
                ),
            )
            conn.commit()
            return cur.lastrowid

    # ============================================================
    # LISTAR COM FILTROS + JOIN DO PET (retorna dicts)
    # ============================================================
    def listar_todos(
        self,
        data: str | None = None,
        status: str | None = None,
    ) -> list[dict]:
        sql = """
            SELECT a.*, p.nome AS pet_nome, p.observacoes AS pet_observacoes
            FROM agendamentos a
            INNER JOIN pets p ON p.id = a.pet_id
        """
        condicoes: list[str] = []
        params: list = []

        if data:
            condicoes.append("a.data = ?")
            params.append(data)

        if status:
            if status not in STATUS_VALIDOS:
                raise StatusInvalidoError(
                    f"Status '{status}' inválido para filtro."
                )
            condicoes.append("a.Status = ?")
            params.append(status)

        if condicoes:
            sql += " WHERE " + " AND ".join(condicoes)

        sql += " ORDER BY a.data ASC, a.horario ASC"

        with self._conectar() as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            return [self._row_para_dict(r) for r in cur.fetchall()]

    # ============================================================
    # BUSCAR
    # ============================================================
    def buscar_por_id(self, agendamento_id: int) -> Agendamento | None:
        with self._conectar() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM agendamentos WHERE id = ?", (agendamento_id,)
            )
            row = cur.fetchone()
        return self._row_para_agendamento(row) if row else None

    # ============================================================
    # ATUALIZAR STATUS
    # ============================================================
    def atualizar_status(self, agendamento_id: int, novo_status: str) -> bool:
        if novo_status not in (STATUS_CONCLUIDO, STATUS_CANCELADO):
            raise StatusInvalidoError(
                "O status só pode ser alterado para 'Concluído' ou 'Cancelado'."
            )

        with self._conectar() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE agendamentos SET Status = ? WHERE id = ?",
                (novo_status, agendamento_id),
            )
            conn.commit()
            return cur.rowcount > 0