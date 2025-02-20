document.addEventListener("DOMContentLoaded", () => {
    const elements = document.querySelectorAll(".fade-in");
    elements.forEach((el) => {
        el.style.opacity = 0;
        el.style.transform = "translateY(20px)";
        setTimeout(() => {
            el.style.transition = "opacity 0.6s ease-out, transform 0.6s ease-out";
            el.style.opacity = 1;
            el.style.transform = "translateY(0)";
        }, 100);
    });
});

const buttons = document.querySelectorAll(".main__button");

buttons.forEach(button => {
    button.addEventListener("mouseenter", () => {
        button.style.transform = "scale(1.05)";
        button.style.boxShadow = "0px 4px 10px rgba(0, 0, 0, 0.2)";
    });

    button.addEventListener("mouseleave", () => {
        button.style.transform = "scale(1)";
        button.style.boxShadow = "none";
    });
});

function updateProgress(value) {
    const progressBar = document.getElementById("progress-fill");
    progressBar.style.transition = "width 0.5s ease-in-out";
    progressBar.style.width = value + "%";
}