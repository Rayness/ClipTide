// Copyright (C) 2025 Rayness
// This program is free software under GPLv3. See LICENSE for details.

document.getElementById('switch_proxy').addEventListener('change', function () {
    const checkbox = document.getElementById('switch_proxy');
    const input = document.getElementById('input_proxy');

    if (checkbox.checked) {
      window.pywebview.api.switch_proxy("True");
      input.disabled = false
    } else {
      input.disabled = true
      window.pywebview.api.switch_proxy("False");
    }
});

document.getElementById('proxy_apply').addEventListener('click', function () {
    const input = document.getElementById('input_proxy').value;

    window.pywebview.api.switch_proxy_url(input);
});

function loadproxy(proxy, proxy_enabled){
  const input =  document.getElementById('input_proxy');
  const checkbox = document.getElementById('switch_proxy');

  if (proxy_enabled == "True") {
    input.disabled = false
    checkbox.checked = true
  } else {
    input.disabled = true
    checkbox.checked = false
    
  };

  input.value = proxy
}


document.getElementById('help-proxy').addEventListener('click', ()=>{
    modal.classList.add('show')
})