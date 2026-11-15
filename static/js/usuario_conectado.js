async function carregarUsuario() {
    const resp = await fetch("/api/usuario_logado");
    if (!resp.ok) return;
    const user = await resp.json();
    const accName = document.getElementById("acc-name");
    const userName = document.getElementById("user-name");
    if (accName) accName.textContent = user.nome;
    if (userName) userName.textContent = user.nome;
}
document.addEventListener("DOMContentLoaded", carregarUsuario);

document.addEventListener("DOMContentLoaded", () => {
    const path = window.location.pathname;
    document.querySelectorAll(".nav-link").forEach(link => {
        const href = link.getAttribute("href");
        if (href === path) {
            link.classList.add("active");
            link.setAttribute("aria-current", "page");
            link.addEventListener("click", (e) => e.preventDefault());
        }
    });
});