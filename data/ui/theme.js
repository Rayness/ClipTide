function setTheme(themeName) {
    const themeLink = document.getElementById('theme-link');
    const theme = document.getElementById('theme')
    themeLink.href = `themes/${themeName}/styles.css`;
    theme.value = themeName
}

function setStyle(styleName) {
    const style = document.getElementById('style')
    document.body.className = '';
    document.body.classList.add(`theme-${styleName}`);
    // style.value = styleName
}

function loadTheme(themeName, styleName, themes) {
    const themeSelect = document.getElementById('theme');
    const styleSelect = document.getElementById('style');

    themes.forEach(theme => {
        const option = document.createElement("option");
        option.value = theme.id;
        option.textContent = theme.name;
        if (theme.id === themeName) {
            option.selected = true;
        }
        themeSelect.appendChild(option);
    });

    function loadStylesForTheme(themeName) {
        const selectedTheme = themes.find(t => t.id === themeName);
        styleSelect.innerHTML = "";
        // При выборе темы — загружаем стили
        selectedTheme?.styles.forEach(style => {
            const opt = document.createElement("option");
            opt.value = style;
            opt.textContent = style;
            if (style === styleName) {
                opt.selected = true;
            }
            styleSelect.appendChild(opt);
        });
    }


    loadStylesForTheme(themeName || selectedTheme.value);
    setTheme(themeName);
    setStyle(styleName);

    themeSelect.addEventListener("change", () => {
        loadStylesForTheme(themeSelect.value);
    });
}

function changeTheme(theme) {
    setTheme(theme);
    window.pywebview.api.saveTheme(theme);
}

function changeStyle(style) {
    setStyle(style);
    window.pywebview.api.saveStyle(style);
}

document.getElementById("theme").addEventListener('change', ()=>{
    const theme = document.getElementById('theme').value || 'dark';
    changeTheme(theme);
})

document.getElementById("style").addEventListener('change', () => {
    const style = document.getElementById('style').value || 'dark';
    changeStyle(style);
})