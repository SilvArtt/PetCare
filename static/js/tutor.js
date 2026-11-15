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
// Listar tutores
// ============================================
async function carregarTutores(filtro = "") {
    const url = filtro ? `/api/tutores?q=${encodeURIComponent(filtro)}` : "/api/tutores";
    const resp = await fetchAuth(url);
    if (!resp) return;

    const tutores = await resp.json();
    const lista = document.getElementById("tutor-list");
    lista.innerHTML = "";

    if (tutores.length === 0) {
        lista.innerHTML = `<p style="color:#888;padding:20px;">Nenhum tutor encontrado.</p>`;
        return;
    }

    tutores.forEach(t => {
        const card = document.createElement("div");
        card.className = "tutor-card";
        card.innerHTML = `
            <div class="tutor-avatar">${t.nome.charAt(0).toUpperCase()}</div>
            <div class="tutor-info">
                <h3>${t.nome}</h3>
                <p>CPF: ${t.cpf} • ${t.email || "sem e-mail"}</p>
            </div>
            <div class="tutor-actions">
                <button class="icon-btn delete" onclick="excluirTutor(${t.id})">🗑️</button>
            </div>
        `;
        lista.appendChild(card);
    });
}

// ============================================
// Excluir tutor
// ============================================
async function excluirTutor(id) {
    if (!confirm("Deseja excluir este tutor?")) return;
    const resp = await fetchAuth(`/api/tutores/${id}`, { method: "DELETE" });
    if (!resp) return;

    if (resp.ok) {
        carregarTutores();
    } else {
        const e = await resp.json();
        alert(e.erro || "Erro ao excluir.");
    }
}

// ============================================
// Busca em tempo real
// ============================================
document.getElementById("tutor-search")?.addEventListener("input", e => {
    carregarTutores(e.target.value);
});

// ============================================
// Submit do formulário (cadastro)
// ============================================
document.getElementById("tutor-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const resp = await fetchAuth("/tutor", { method: "POST", body: new FormData(e.target) });
    if (!resp) return;

    if (resp.ok) {
        e.target.reset();
        carregarTutores();
    } else {
        alert("Erro ao cadastrar tutor.");
    }
});

// ============================================
// Ao carregar a página
// ============================================
document.addEventListener("DOMContentLoaded", () => carregarTutores());