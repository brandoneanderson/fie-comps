const scanButton = document.getElementById('scanButton');
const extensionUrlInput = document.getElementById('extensionUrl');
const resultsLink = document.getElementById('resultsLink');

// Optional: if user pastes a Google redirect URL from CSE, unwrap it
function normalizeStoreUrl(input) {
  try {
    const u = new URL(input);
    if (u.hostname === 'www.google.com' && u.pathname === '/url') {
      const q = u.searchParams.get('q');
      if (q) return q;
    }
  } catch {
    // ignore invalid URLs and fall through
  }
  return input;
}

if (scanButton && extensionUrlInput) {
  scanButton.addEventListener('click', async () => {
    const raw = extensionUrlInput.value.trim();
    const url = normalizeStoreUrl(raw);

    if (!url) {
      alert('Please enter a Chrome Web Store URL');
      return;
    }

    try {
      const r = await fetch('/api/download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ store_url: url }),
      });

      const text = await r.text();
      let data;
      try {
        data = JSON.parse(text);
      } catch {
        data = { raw: text };
      }

      if (!r.ok) {
        console.error('Error downloading extension', r.status, data);
        alert(`Error downloading extension (${r.status}). Check console for details.`);
        return;
      }

      // On success, behave like before: show the results section
      if (resultsLink) {
        resultsLink.style.display = 'inline-flex';
        resultsLink.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    } catch (e) {
      console.error('Network error while downloading extension', e);
      alert(`Network error: ${String(e)}`);
    }
  });

  // Allow Enter key to trigger scan
  extensionUrlInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      scanButton.click();
    }
  });
}

