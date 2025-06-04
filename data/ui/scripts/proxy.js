
document.getElementById('toggleSwitch').addEventListener('change', function () {
    const checkbox = document.getElementById('toggleSwitch');
    const label = document.getElementById('toggleLabel');
      label.textContent = this.checked ? 'On' : 'Off';
    });