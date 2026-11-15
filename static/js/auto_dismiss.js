// flash messages após 3 segundos
document.addEventListener("DOMContentLoaded", () => {
    const flashes = document.querySelectorAll(".flash");
    flashes.forEach((flash, index) => {
        setTimeout(() => {
            flash.style.transition = "opacity 0.4s ease, transform 0.4s ease";
            flash.style.opacity = "0";
            flash.style.transform = "translateX(100%)";
            setTimeout(() => flash.remove(), 400);
        }, 3000 + index * 300); // 3s + 300ms de delay entre cada flash
    });
});