async function fetchAuth(url, options = {}) {
    const resp = await fetch(url, options);
    if (resp.status === 401) {
        window.location.href = "/";
        return null;
    }
    return resp;
}

async function carregarPets(filtro = "") {
    const url = filtro ? `/api/pets?q=${encodeURIComponent(filtro)}` : "/api/pets";
    const resp = await fetchAuth(url);
    if (!resp) return;

    const pets = await resp.json();
    const lista = document.getElementById("pet-list");
    lista.innerHTML = "";

    if (pets.length === 0) {
        lista.innerHTML = `<p style="color:#888;padding:20px;">Nenhum pet encontrado.</p>`;
        return;
    }

    pets.forEach(p => {
        const card = document.createElement("div");
        card.className = "pet-card";
        card.innerHTML = `
            <div class="pet-avatar">${p.nome.charAt(0).toUpperCase()}</div>
            <div class="pet-info">
                <h3>${p.nome}</h3>
                <p>${p.especie} • ${p.raca || "SRD"} • ${p.porte || "Porte não informado"} • ${p.peso ? p.peso + " kg" : "Peso não informado"}</p>
                <p><strong>Tutor:</strong> ${p.tutor_nome || "—"}</p>
                ${p.observacoes ? `<p style="color:#e53935;"><strong>⚠️ Obs.:</strong> ${p.observacoes}</p>` : ""}
            </div>
            <div class="pet-actions">
                <button class="icon-btn delete" onclick="excluirPet(${p.id})">🗑️</button>
            </div>
        `;
        lista.appendChild(card);
    });
}

async function excluirPet(id) {
    if (!confirm("Deseja excluir este pet?")) return;

    const resp = await fetchAuth(`/pets/${id}/excluir`, { method: "POST" });
    if (!resp) return;

    if (resp.ok) {
        // Sucesso: recarrega a lista
        carregarPets();
    } else {
        // Erro: mostra a mensagem do backend
        try {
            const erro = await resp.json();
            alert(erro.erro || "Erro ao excluir o pet.");
        } catch {
            alert("Erro ao excluir o pet.");
        }
    }
}
async function carregarTutoresSelect() {
    const resp = await fetchAuth("/api/tutores");
    if (!resp) return;

    const tutores = await resp.json();
    const select = document.getElementById("tutor_id");

    tutores.forEach(t => {
        const opt = document.createElement("option");
        opt.value = t.id;
        opt.textContent = `${t.nome} (CPF: ${t.cpf})`;
        select.appendChild(opt);
    });
}

document.getElementById("pet-search")?.addEventListener("input", e => {
    carregarPets(e.target.value);
});

document.getElementById("pet-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const resp = await fetchAuth("/cadastro_pet", { method: "POST", body: new FormData(e.target) });
    if (!resp) return;

    const data = await resp.json();

    if (resp.ok) {
        e.target.reset();
        carregarPets();
        const select = document.getElementById("tutor_id");
        select.innerHTML = '<option value="">Selecione o Tutor Responsável...</option>';
        carregarTutoresSelect();
        alert(data.mensagem || "Pet cadastrado com sucesso!");
    } else {
        alert(data.erro || "Erro ao cadastrar pet.");
    }
});

document.addEventListener("DOMContentLoaded", () => {
    carregarPets();
    carregarTutoresSelect();
});