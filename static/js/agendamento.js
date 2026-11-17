async function fetchAuth(url, options = {}) {
    const resp = await fetch(url, options);
    if (resp.status === 401) {
        window.location.href = "/";
        return null;
    }
    return resp;
}

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
            <div class="card-tutor"><strong>Pet:</strong> ${a.pet_nome} • <strong>Status:</strong> ${a.status}</div>
            ${a.pet_observacoes ? `<div class="card-obs"><strong>⚠️ Alergias/Obs. do pet:</strong> ${a.pet_observacoes}</div>` : ""}
            ${a.observacoes ? `<div class="card-obs"><strong>Obs. do agendamento:</strong> ${a.observacoes}</div>` : ""}
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

async function alterarStatus(id, novo) {
    const resp = await fetchAuth(`/agendamentos/${id}/status/${encodeURIComponent(novo)}`, { method: "POST" });
    if (resp && resp.ok) {
        carregarAgendamentos();
    }
    else{
        try {
            const erro = await resp.json();
            alert(erro.erro || "erro ao modificar o status do agendamento")
        } catch {
            alert("Erro ao modificar o status do agendamento")
        }
    }
}

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

document.getElementById("filtro-data")?.addEventListener("change", carregarAgendamentos);
document.getElementById("filtro-status")?.addEventListener("change", carregarAgendamentos);

document.getElementById("agendamento-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const resp = await fetchAuth("/agendamentos", { method: "POST", body: new FormData(e.target) });
    if (!resp) return;

    const data = await resp.json();

    if (resp.ok) {
        e.target.reset();
        carregarAgendamentos();
        alert(data.mensagem || "Agendamento criado com sucesso!");
    } else {
        alert(data.erro || "Erro ao cadastrar agendamento.");
    }
});

document.addEventListener("DOMContentLoaded", () => {
    carregarAgendamentos();
    carregarPetsSelect();
});