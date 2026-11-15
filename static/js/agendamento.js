// ============================================
// Utilitário: fetch com tratamento de 401
// ============================================
async function fetchAuth(url, options = {}) {
    const resp = await fetch(url, options);
    if (resp.status === 401) {
        window.location.href = "/";
        return null;
    }
    return resp;
}

// ============================================
// Listar agendamentos (com filtros)
// ============================================
async function carregarAgendamentos() {
    const data = document.getElementById("filtro-data").value;
    const status = document.getElementById("filtro-status").value;

    const params = new URLSearchParams();
    if (data) params.append("data", data);
    if (status) params.append("status", status);

    const resp = await fetchAuth(`/api/agendamentos?${params.toString()}`);
    if (!resp) return;

    const lista = await resp.json();
    const container = document.getElementById("lista-agendamentos");
    container.innerHTML = "";

    if (lista.length === 0) {
        container.innerHTML = `<p style="color:#888;padding:20px;">Nenhum agendamento encontrado.</p>`;
        return;
    }

    lista.forEach(a => {
        const card = document.createElement("div");
        card.className = "card-agendamento";
        card.innerHTML = `
            <div class="card-title">${a.servico}<span class="sep">•</span>${a.data} às ${a.horario}</div>
            <div class="card-tutor">Status: ${a.status}</div>
            ${a.observacoes ? `<div class="card-obs">${a.observacoes}</div>` : ""}
            <div class="card-info">
                ${a.status === "Agendado" ? `
                    <button onclick="alterarStatus(${a.id}, 'Concluído')" class="btn-solid" style="padding:6px 12px;font-size:.85rem;">Concluir</button>
                    <button onclick="alterarStatus(${a.id}, 'Cancelado')" class="btn-outline" style="padding:6px 12px;font-size:.85rem;">Cancelar</button>
                ` : ""}
            </div>
        `;
        container.appendChild(card);
    });
}

// ============================================
// Alterar status
// ============================================
async function alterarStatus(id, novo) {
    const resp = await fetchAuth(`/agendamentos/${id}/status/${encodeURIComponent(novo)}`, { method: "POST" });
    if (resp && resp.ok) {
        carregarAgendamentos();
    }
}

// ============================================
// Popular select de pets
// ============================================
async function carregarPetsSelect() {
    const resp = await fetchAuth("/api/pets");
    if (!resp) return;

    const pets = await resp.json();
    const select = document.getElementById("pet");

    pets.forEach(p => {
        const opt = document.createElement("option");
        opt.value = p.id;
        opt.textContent = `${p.nome} (Tutor: ${p.tutor_nome || "—"})`;
        select.appendChild(opt);
    });
}

// ============================================
// Filtros
// ============================================
document.getElementById("filtro-data")?.addEventListener("change", carregarAgendamentos);
document.getElementById("filtro-status")?.addEventListener("change", carregarAgendamentos);

// ============================================
// Submit do formulário (cadastro)
// ============================================
document.getElementById("agendamento-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const resp = await fetchAuth("/agendamentos", { method: "POST", body: new FormData(e.target) });
    if (!resp) return;

    if (resp.ok) {
        e.target.reset();
        carregarAgendamentos();
    } else {
        alert("Erro ao cadastrar agendamento.");
    }
});

// ============================================
// Ao carregar a página
// ============================================
document.addEventListener("DOMContentLoaded", () => {
    carregarAgendamentos();
    carregarPetsSelect();
});