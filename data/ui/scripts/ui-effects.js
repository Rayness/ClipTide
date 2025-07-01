// Copyright (C) 2025 Rayness
// This program is free software under GPLv3. See LICENSE for details.

document.addEventListener("DOMContentLoaded", () => {
    const elements = document.querySelectorAll(".fade-in");
    const buttons = document.querySelectorAll(".main__button");

    buttons.forEach(button => {
        button.addEventListener("mouseenter", () => {
            button.style.transform = "scale(1.1)";
        });

        button.addEventListener("mouseleave", () => {
            button.style.transform = "scale(1)";
        });

        button.addEventListener("mousedown", () => {
            button.style.transform = "scale(0.95)";
            button.style.boxShadow = "0px 0px 15px rgba(74, 86, 198, 0.5)";
        });

        button.addEventListener("mouseup", () => {
            button.style.transform = "scale(1.05)";
            setTimeout(() => {
                button.style.transform = "scale(1)";
                button.style.boxShadow = "none";
            }, 150);
        });
    });

    elements.forEach((el) => {
        el.style.opacity = 0;
        el.style.transform = "translateY(20px)";
        setTimeout(() => {
            el.style.transition = "opacity 0.3s ease-out, transform 0.3s ease-out";
            el.style.opacity = 1;
            el.style.transform = "translateY(0)";
        }, 100);
    });
});

function updateProgress(value) {
    const progressBar = document.getElementById("progress-fill");
    progressBar.style.transition = "width 0.5s ease-in-out";
    progressBar.style.width = value + "%";
}


const buttons = document.querySelectorAll('.tab-btn');

    buttons.forEach(btn => {
    btn.addEventListener('click', () => {
        buttons.forEach(b => b.classList.remove('active')); // убрать у всех
        btn.classList.add('active'); // добавить только этой
    });
});