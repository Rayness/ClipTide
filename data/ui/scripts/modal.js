var content;

function loadData(data){
  content = data
  console.log(content)
};

document.getElementById('close-modal').addEventListener('click', ()=>{
  const modal = document.getElementById('modal')

  modal.classList.remove('show')
});

document.getElementById('modal').addEventListener('click', (e) => {
  if (e.target === modal) {
    modal.classList.remove('show');
  }
});

document.getElementById('help-theme').addEventListener('click', ()=>{
  const lang = document.getElementById('language').value;
  console.log('содержимое: ', content[0].content.settings.language.ru)

  if (lang === 'ru') {
    displayData(content[0].content.settings.language.ru)
  }
  if (lang === 'en') {
    displayData(content[0].content.settings.language.en)
  }
});

function displayData(data){
  const title = document.getElementById('modal-title');
  const content = document.getElementById('modal-content');

  title.innerHTML = data.title;
  content.innerHTML = data.content;
};