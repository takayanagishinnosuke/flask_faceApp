let input = document.getElementById('fileSelct');

input.addEventListener('change', function(e){
  const file = e.target.files[0]

  if (!file) return

  let reader = new FileReader();

  reader.onload = function(e){
    document.querySelector('#create_img').src = e.target.result
  }

  reader.readAsDataURL(file)
})