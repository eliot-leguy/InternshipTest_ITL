document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('uploadForm');
  const ul = document.getElementById('files');

  async function loadFileList() {
    const res = await fetch('/files');
    const files = await res.json();

    ul.innerHTML = '';
    if (!files.length) {
      ul.innerHTML = '<li>No files yet</li>';
      return;
    }

    for (const name of files) {
      const li = document.createElement('li');
      li.className = 'file-item';
    
      const icon = document.createElement('span');
      icon.textContent = name.endsWith('.pdf') ? '📄' : '📃';
      icon.className = 'file-icon';
    
      const link = document.createElement('a');
      link.href = `/files/${encodeURIComponent(name)}`;
      link.textContent = name;
      link.className = 'file-link';
      link.target = '_blank';
    
      const btn = document.createElement('button');
      btn.textContent = '✖';
      btn.className = 'delete-btn';
      btn.onclick = async () => {
        await fetch(`/files/${encodeURIComponent(name)}`, { method: 'DELETE' });
        await loadFileList();
        await loadFAQ();
      };
    
      li.appendChild(icon);
      li.appendChild(link);
      li.appendChild(btn);
      ul.appendChild(li);
    }
    
  }

  async function loadFAQ() {
    const res = await fetch('/faq.json');
    const faq = await res.json();

    const faqDiv = document.getElementById('faq');
    faqDiv.innerHTML = '';

    if (!faq.length) {
      faqDiv.textContent = 'No FAQ generated yet.';
      return;
    }

    for (const { question, answer } of faq) {
      const details = document.createElement('details');
      const summary = document.createElement('summary');
      summary.textContent = question;
    
      const p = document.createElement('p');
      p.textContent = answer;
    
      details.appendChild(summary);
      details.appendChild(p);
      faqDiv.appendChild(details);
    }
  }

  form.addEventListener('submit', async e => {
    e.preventDefault();
    const data = new FormData(form);
    const status = document.getElementById('status');
  
    status.textContent = '📤 Uploading file...';
  
    let res, result;
    try {
      res = await fetch('/upload', {
        method: 'POST',
        body: data,
      });
  
      if (!res.ok) {
        status.textContent = `❌ Upload failed: HTTP ${res.status}`;
        return;
      }
  
      result = await res.json();
      if (result.status === 'ok') {
        status.textContent = '✅ FAQ updated.';
        await loadFileList();
        await loadFAQ();
      } else {
        status.textContent = '❌ FAQ update failed: ' + result.message;
      }
  
    } catch (err) {
      status.textContent = '❌ Upload failed: ' + err.message;
    }
  
    form.reset();
    setTimeout(() => (status.textContent = ''), 4000);
  });
  
  

  loadFileList();
  loadFAQ();
});
