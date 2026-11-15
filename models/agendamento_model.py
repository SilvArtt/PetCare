import sqlite3
from dataclasses import dataclass


# ============================================================
# Constantes de status (evita strings soltas no código)
# ============================================================
STATUS_AGENDADO = "Agendado"
STATUS_CONCLUIDO = "Concluído"
STATUS_CANCELADO = "Cancelado"

STATUS_VALIDOS = {STATUS_AGENDADO, STATUS_CONCLUIDO, STATUS_CANCELADO}


# ============================================================
# Modelo (dataclass)
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
# Exceções específicas
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

    @staticmethod
    def _row_para_agendamento(row: sqlite3.Row) -> Agendamento:
        return Agendamento(
            id=row["id"],
            pet_id=row["pet_id"],
            servico=row["servico"],
            data=row["data"],
            horario=row["horario"],
            observacoes=row["observacoes"] or "",
            status=row["Status"],  # atenção: coluna é "Status" (S maiúsculo no SQL)
        )

    # ============================================================
    # CADASTRAR — regra de duplicidade
    # ============================================================
    def cadastrar(self, agendamento: Agendamento) -> int:
        """
        Insere um agendamento garantindo que:
          - o pet_id existe;
          - o status inicial é válido;
          - NÃO existe outro agendamento do mesmo pet na mesma data+horário.

        :raises PetInexistenteError: se pet_id não existir
        :raises StatusInvalidoError: se status não estiver em STATUS_VALIDOS
        :raises AgendamentoDuplicadoError: se já houver agendamento no mesmo slot
        :return: id do agendamento criado
        """
        # 1) Validações básicas
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

            # 2) Pet existe?
            cur.execute("SELECT 1 FROM pets WHERE id = ?", (agendamento.pet_id,))
            if cur.fetchone() is None:
                raise PetInexistenteError(
                    f"Pet id={agendamento.pet_id} não encontrado."
                )

            # 3) Regra de duplicidade:
            #    mesmo pet + mesma data + mesmo horário + status != Cancelado
            #    (um agendamento cancelado libera o slot para reagendamento)
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

            # 4) Inserção
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
    # LISTAGEM COM FILTROS (data + status) — conforme a.html
    # ============================================================
    def listar_todos(
        self,
        data: str | None = None,
        status: str | None = None,
    ) -> list[Agendamento]:
        """
        Lista agendamentos com filtros opcionais de data e status
        (exatamente o que os <input type="date"> e <select> do a.html fazem).

        Ordena por data e horário ascendentes.
        """
        sql = "SELECT * FROM agendamentos"
        condicoes: list[str] = []
        params: list = []

        if data:
            condicoes.append("data = ?")
            params.append(data)

        if status:
            if status not in STATUS_VALIDOS:
                raise StatusInvalidoError(
                    f"Status '{status}' inválido para filtro."
                )
            condicoes.append("Status = ?")
            params.append(status)

        if condicoes:
            sql += " WHERE " + " AND ".join(condicoes)

        sql += " ORDER BY data ASC, horario ASC"

        with self._conectar() as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            return [self._row_para_agendamento(r) for r in cur.fetchall()]

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
    # ATUALIZAR STATUS — só Concluído ou Cancelado
    # ============================================================
    def atualizar_status(self, agendamento_id: int, novo_status: str) -> bool:
        """
        Altera o status de um agendamento.
        Regra: só permite transição para 'Concluído' ou 'Cancelado'.

        :raises StatusInvalidoError: se novo_status não for Concluído/Cancelado
        :return: True se alterou
        """
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
