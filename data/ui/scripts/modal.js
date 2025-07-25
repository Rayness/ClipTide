
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

document.getElementById('help-theme').addEventListener('click', ()=> {
  const data = content[0].content.settings.themes.language;
  const lang = document.getElementById('language').value;
  console.log('содержимое: ', )

  switch(lang) {
    case "ru":
      displayData(data.ru);
      break
    case "en":
      displayData(data.en);
      break
    default:
      displayData(data.en);
      break
  }
});

document.getElementById('help-proxy').addEventListener('click', ()=>{
  const data = content[0].content.settings.proxy.language;
  const lang = document.getElementById('language').value;

  switch(lang) {
    case "ru":
      displayData(data.ru);
      break
    case "en":
      displayData(data.en);
      break
    default:
      displayData(data.en);
      break
  }
});


function displayData(data){
  const title = document.getElementById('modal-title');
  const content = document.getElementById('modal-content');

  title.innerHTML = ``
  content.innerHTML = ``

  title.innerHTML = data.title;
  content.innerHTML = data.content;
};