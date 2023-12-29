document.addEventListener('DOMContentLoaded', function () {
    fetch('list.json')
      .then(response => response.json())
      .then(data => {
        const fileList = document.getElementById('fileList');
        const searchInput = document.getElementById('searchInput');
  
        searchInput.addEventListener('input', function() {
          const searchValue = this.value.toLowerCase();
          const listItems = fileList.querySelectorAll('li');
  
          listItems.forEach(item => {
            const fileName = item.querySelector('.file-name').textContent.toLowerCase();
            const matches = fileName.includes(searchValue);
  
            item.style.display = matches ? 'block' : 'none';
          });
        });
  
        data.forEach(item => {
          const li = document.createElement('li');
  
          const fileName = document.createElement('span');
          fileName.classList.add('file-name');
          fileName.textContent = `File Name: ${item.file_name}`;
          li.appendChild(fileName);
  
          const fileId = document.createElement('span');
          fileId.classList.add('file-id');
          fileId.textContent = `ID: ${item.id}`;
  
          const copyButton = document.createElement('button');
          copyButton.textContent = 'Copy';
          copyButton.classList.add('copy-button');
          copyButton.addEventListener('click', () => {
            copyToClipboard(item.id);
          });
  
          li.appendChild(document.createElement('br'));
          li.appendChild(fileId);
          li.appendChild(copyButton);
          fileList.appendChild(li);
        });
      })
      .catch(error => console.error('Error fetching data:', error));
  });
  
  function copyToClipboard(text) {
    const tempInput = document.createElement('textarea');
    tempInput.value = text;
    document.body.appendChild(tempInput);
    tempInput.select();
    document.execCommand('copy');
    document.body.removeChild(tempInput);
    alert(`ID "${text}" copied to clipboard`);
  }
  