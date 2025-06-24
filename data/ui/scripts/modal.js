document.getElementById('close-modal').addEventListener('click', ()=>{
    const modal = document.getElementById('modal')

    modal.classList.remove('show')
})

document.getElementById('modal').addEventListener('click', (e) => {
    if (e.target === modal) {
      modal.classList.remove('show');
    }
  });